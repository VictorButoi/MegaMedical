from multiprocessing.sharedctypes import Value
from operator import truediv
from select import select
from turtle import pos
import numpy as np
from torch import mul
import nibabel as nib
import numpy as np
import os
import math
import matplotlib.pyplot as plt
from scipy import ndimage
from tqdm import tqdm
import pickle
from PIL import Image
from glob import glob
import SimpleITK as sitk
import imageio as io
import nrrd
import cv2
import gzip
import scipy
import pathlib
import glob

#New line!
from megamedical.utils.registry import paths


class OASIS:

    def __init__(self):

        self.dataset_info_dictionary = {
            "retrieved_2021_01_26":{
                "main":"OASIS",
                "image_root_dir":"/home/vib9/src/data/OASIS/processed/original_unzipped/retrieved_2021_01_26",
                "label_root_dir":"/home/vib9/src/data/OASIS/processed/original_unzipped/retrieved_2021_01_26",
                "modality_names":["T1"],
                "planes":[0, 1, 2],
                "clip_args":None,
                "norm_scheme":"MR",
                "do_clip":True,
                "proc_size":256
            }
        }

    def proc_func(self,
                dset_name,
                processed_dir,
                redo_processed=True):
        assert dset_name in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        images = []
        segs = []
        image_list = os.listdir(self.dset_info[dset_name]["image_root_dir"])
        with tqdm(total=len(image_list), desc=f'Processing: {dset_name}', unit='image') as pbar:
            for image in image_list:
                try:
                    if redo_processed or (len(glob.glob(os.path.join(processed_dir, "*", image))) == 0):
                        im_dir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "aligned_norm.nii.gz")
                        label_dir = os.path.join(self.dset_info[dset_name]["label_root_dir"], image, "aligned_seg35.nii.gz")

                        loaded_image = np.array(nib.load(im_dir).dataobj)
                        loaded_label = np.array(nib.load(label_dir).dataobj)

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        images.append(loaded_image)
                        segs.append(loaded_label)
                except Exception as e:
                    print(e)
                pbar.update(1)
        pbar.close()
        return images, segs