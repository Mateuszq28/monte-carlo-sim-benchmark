import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, rc
from scipy.stats import chisquare
from matplotlib.colors import LogNorm, Normalize
from PIL import Image

np.random.seed(seed=1)

def load_from_file(filename):
    file = open(filename, 'r')
    data = json.load(file)
    file.close()
    return data

def cube_list2array(d):
    d['cube'] = np.asarray(d['cube'])

def normalization(d):
    if d['normalized_already']:
        print('dane znormalizowano już wcześniej!')
    else:
        # bins_per_1_cm = 120
        # mu_a = 0.37
        # n_photons = 1_000_000
        # val = val * 4.67
        bin_size_in_cm = 1 / d['bins_per_1_cm']
        bin_volume = (bin_size_in_cm)**3
        multi = 1 / (d['n_photons'] * bin_volume * d['mu_a'])
        d['cube'] = d['cube'] * multi
        d['overflow'] = d['overflow'] * multi
        d['photon_weight'] = d['photon_weight'] * multi
        d['normalized_already'] = True

def make_frames(cub_list, arr_list=None):
    for i in range(len(cub_list)):
        if arr_list is None:
            arr = cub_list[i]['cube']
        else:
            arr = arr_list[i]

        sh = arr.shape
        f = [None for _ in range(20)]

        # --- x_high ---
        # z tej strony wbijamy nóż cięcia slice

        # 3 vertical slices
        f[0] = arr[:,0,:]
        f[1] = arr[:,sh[1]//2,:]
        f[2] = arr[:,-1,:]
        
        # 3 horizontal slices
        f[3] = arr[:,:,-1]
        f[4] = arr[:,:,sh[0]//2]
        f[5] = arr[:,:,0]

        # sums have to be normalized -> division
        # avg y
        f[6] = arr.sum(axis=1) / sh[1]
        # avg z
        f[7] = arr.sum(axis=2) / sh[2]

        # --- z_high ---
        # z tej strony wbijamy nóż cięcia slice

        # 3 vertical slices
        sh = arr.shape
        f[8] = f[0]
        f[9] = f[1]
        f[10] = f[2]
        
        # 3 horizontal slices
        f[11] = arr[0,:,:]
        f[12] = arr[sh[0]//2,:,:]
        f[13] = arr[-1,:,:]

        # avg y
        f[14] = f[6]
        # avg x
        f[15] = arr.sum(axis=0) / sh[0]

        # --- 1D - sum along 2 axes

        # avg xy
        f[16] = arr.sum(axis=(0,1)) / sh[0] / sh[1]
        # avg xz
        f[17] = arr.sum(axis=(0,2)) / sh[0] / sh[2]

        # avg yz
        f[18] = arr.sum(axis=(1,2)) / sh[1] / sh[2]
        # avg xz
        f[19] = f[17]

        # --- save frames ---

        bpc = cub_list[i]['bins_per_1_cm']
        cub_list[i]['frames'] = f
        cub_list[i]['frame_names'] = [
            f"y_low, slice, const y={0: .2f}",
            f"y_low, slice, const y={sh[1]/2/bpc: .2f}",
            f"y_low, slice, const y={sh[1]/bpc: .2f}",

            f"z_high, slice, const z={sh[2]/bpc: .2f}",
            f"z_high, slice, const z={sh[2]/2/bpc: .2f}",
            f"z_high, slice, const z={0.0: .2f}",

            f"y_low\nśrednia wzdłuż osi y",
            f"z_high\nśrednia wzdłuż osi z",

            "",
            "",
            "",

            f"x_high, slice, const x={0.0: .2f}",
            f"x_high, slice, const x={sh[0]/2/bpc: .2f}",
            f"x_high, slice, const x={sh[0]/bpc: .2f}",

            "",
            f"x_high\nśrednia wzdłuż osi x",


            f"średnia wzdłuż osi x oraz y",
            f"średnia wzdłuż osi x oraz z",
            f"średnia wzdłuż osi y oraz z",
            "",
        ]

        cub_list[i]['frame_shortnames'] = [
            "y_low slice",
            "y_low slice",
            "y_low slice",

            "z_high slice",
            "z_high slice",
            "z_high slice",

            "avg_y y_low",
            "avg_z z_high",

            "",
            "",
            "",

            "x_high slice",
            "x_high slice",
            "x_high slice",

            "",
            "avg_x x_high",


            f"avg_xy",
            f"avg_xz",
            f"avg_yz",
            "",
        ]

