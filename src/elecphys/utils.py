# -*- coding: utf-8 -*-
"""
Utilities to help in the deep electrode signals pre-processing
"""
from src.env import DATA

import os
import os.path as op
from os.path import join as opj
import numpy as np
import tempfile
import shutil
import matplotlib.pyplot as plt
from scipy.signal import remez, filtfilt



def clean_file(file_path):

    wrong_word = 'BREAK'
    temp_file = tempfile.mkstemp()[1]

    with open(file_path) as oldfile, open(temp_file, 'w') as newfile:
        for line in oldfile:
            if wrong_word not in line:
                newfile.write(line)

    shutil.move(temp_file, file_path)


def clean_all_files_and_convert_to_npy():

    for filename in os.listdir(INTERICTAL_DATA):
        file = opj(INTERICTAL_DATA, filename)
        if filename.endswith(".txt"):
            clean_file(file)
            with open(file, 'r') as f:
                ncols = len(f.readline().split('\t'))

            numpy_matrix = np.loadtxt(file,
                                      dtype='float32',
                                      delimiter='\t',
                                      usecols=range(3, ncols-1))
            np.save(file[:-4], numpy_matrix)


def bandpass_filter(data, fs, lowcut, highcut):

    order = 1000
    ns, num_channels = np.shape(data)
    if ns < 3 * order:
        order = np.floor(ns/3)

    Fstop1 = lowcut - 0.001
    Fpass1 = lowcut

    Fpass2 = highcut
    Fstop2 = highcut + 0.005
    Wstop1 = 10
    Wpass = 1
    Wstop2 = 10
    dens = 20

    b = remez(order+1,
              bands=np.array([0, Fstop1, Fpass1, Fpass2, Fstop2, fs/2]),
              desired=[0, 1, 0],
              Hz=fs,
              weight=[Wstop1, Wpass, Wstop2],
              grid_density=dens)

    y = filtfilt(b, 1, data[:, 0])
    return y