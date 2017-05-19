#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 11:23:57 2017

@author: asier
"""
from os.path import join as opj
import numpy as np
import nibabel as nib


def scrubbing(time_series, FD, thres=0.2):
    """
    simple scrubbing strategy based on timepoint removal
    """
    scrubbed_time_series = time_series.T[:, (FD < thres)]
    return scrubbed_time_series.T


def atlas_with_all_rois():
    """
    Function to correct atlas after resampling (looses some rois),
    this function recovers those lost rois
    """
    atlas_old = '/home/asier/git/ruber/data/external/bha_atlas_2754_1mm_mni09c.nii.gz'
    atlas_new = opj(base_path, 'sub-001_atlas_2754_bold_space.nii.gz')

    atlas_new_img = nib.load(atlas_new)
    m = atlas_new_img.affine[:3, :3]

    atlas_old_data = nib.load(atlas_old).get_data()
    atlas_old_data_rois = np.unique(atlas_old_data)
    atlas_new_data = atlas_new_img.get_data()
    atlas_new_data_rois = np.unique(atlas_new_data)

    diff_rois = np.setdiff1d(atlas_old_data_rois, atlas_new_data_rois)

    for roi in diff_rois:
        p = np.argwhere(atlas_old_data == roi)[0]
        x, y, z = (np.round(np.diag(np.divide(p, m)))).astype(int)
        atlas_new_data[x, y, z] = roi

    atlas_new_data_img_corrected = nib.Nifti1Image(atlas_new_data,
                                                   affine=atlas_new_img.affine)
    nib.save(atlas_new_data_img_corrected,
             opj(base_path, 'sub-001_atlas_2754_bold_space.nii.gz'))


# TODO: 
def load_elec_file(elec_file):
    pass

def extend_elec_location(elec_location):

    for elec_key, value in elec_location.items():
        x, y, z = value[0]
        elec_location[elec_key].append([x + 1, y + 1, z + 1])
        elec_location[elec_key].append([x + 1, y + 1, z - 1])
        elec_location[elec_key].append([x + 1, y + 1, z])
        elec_location[elec_key].append([x + 1, y - 1, z + 1])
        elec_location[elec_key].append([x + 1, y - 1, z - 1])
        elec_location[elec_key].append([x + 1, y - 1, z])
        elec_location[elec_key].append([x + 1, y, z + 1])
        elec_location[elec_key].append([x + 1, y, z - 1])
        elec_location[elec_key].append([x + 1, y, z])

        elec_location[elec_key].append([x - 1, y + 1, z + 1])
        elec_location[elec_key].append([x - 1, y + 1, z - 1])
        elec_location[elec_key].append([x - 1, y + 1, z])
        elec_location[elec_key].append([x - 1, y - 1, z + 1])
        elec_location[elec_key].append([x - 1, y - 1, z - 1])
        elec_location[elec_key].append([x - 1, y - 1, z])
        elec_location[elec_key].append([x - 1, y, z + 1])
        elec_location[elec_key].append([x - 1, y, z - 1])
        elec_location[elec_key].append([x - 1, y, z])

        elec_location[elec_key].append([x, y + 1, z + 1])
        elec_location[elec_key].append([x, y + 1, z - 1])
        elec_location[elec_key].append([x, y + 1, z])
        elec_location[elec_key].append([x, y - 1, z + 1])
        elec_location[elec_key].append([x, y - 1, z - 1])
        elec_location[elec_key].append([x, y - 1, z])
        elec_location[elec_key].append([x, y, z + 1])
        elec_location[elec_key].append([x, y, z - 1])
    return elec_location


def writeDict(dict, filename, sep=','):
    with open(filename, "a") as f:
        for i in dict.keys():
            f.write(i + ":" + sep.join([str(x) for x in dict[i]]) + "\n")


def locate_electrodes(elec_file, atlas_file, neighbours=0):
    from collections import defaultdict

    elec_location_mni09 = load_elec_file(elec_file)
    if neighbours:
        elec_location_mni09 = extend_elec_location(elec_location_mni09)

    atlas_data = nib.load(atlas_file).get_data()
    roi_location_mni09 = defaultdict(set)

    for elec in elec_location_mni09.keys():
        for location in elec_location_mni09[elec]:
            x, y, z = location
            roi_location_mni09[elec].add(atlas_data[x, y, z].astype('int'))

    writeDict(roi_location_mni09,
              '/home/asier/Desktop/test_ruber/sub001elec.roi')





"""
from nilearn import datasets

dataset = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_filename = dataset.maps
labels = dataset.labels

print('Atlas ROIs are located in nifti image (4D) at: %s' %
      atlas_filename)  # 4D data

# One subject of resting-state data
data = datasets.fetch_adhd(n_subjects=1)
fmri_filenames = data.func[0]


from nilearn.input_data import NiftiLabelsMasker
masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True,
                           memory='nilearn_cache', verbose=5)

# Here we go from nifti files to the signal time series in a numpy
# array. Note how we give confounds to be regressed out during signal
# extraction
time_series = masker.fit_transform(fmri_filenames, confounds=data.confounds)

from nilearn.connectome import ConnectivityMeasure
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([time_series_2754])[0]


# Plot the correlation matrix
import numpy as np
from matplotlib import pyplot as plt
plt.figure(figsize=(10, 10))
# Mask the main diagonal for visualization:
np.fill_diagonal(correlation_matrix, 0)

plt.imshow(correlation_matrix, interpolation="nearest", cmap="RdBu_r",
           vmax=0.8, vmin=-0.8)

# Add labels and adjust margins
plt.gca().yaxis.tick_right()
plt.subplots_adjust(left=.01, bottom=.3, top=.99, right=.62)  
"""