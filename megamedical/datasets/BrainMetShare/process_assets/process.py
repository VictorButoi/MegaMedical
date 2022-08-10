from ast import DictComp
from multiprocessing.sharedctypes import Value
import numpy as np
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
import medpy.io
import pydicom as dicom
import scipy.io

#New line!
from megamedical.utils.registry import paths


class BrainMetShare:

    def __init__(self):

        self.dataset_info_dictionary = {
            "retrieved_2022_03_04":{
                "main": "BrainMetShare",
                "image_root_dir":"/home/vib9/src/data/BrainMetShare/processed/original_unzipped/retrieved_2022_03_04/stanford_release_brainmask/mets_stanford_releaseMask_train",
                "label_root_dir":"/home/vib9/src/data/BrainMetShare/processed/original_unzipped/retrieved_2022_03_04/stanford_release_brainmask/mets_stanford_releaseMask_train",
                "modality_names":["T1", "T1-spin-pre", "T1-spin-post", "T2-FLAIR"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":"MR",
                "do_clip":False,
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
                        "T1", "T1-spin-pre", "T1-spin-post", "T2-FLAIR"
                        t1_im_dirs = [os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "0", slice) for slice in os.listdir(os.path.join(self.dset_info["image_root_dir"], image, "0"))]
                        t1_spin_pre_dirs = [os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "1", slice) for slice in os.listdir(os.path.join(self.dset_info["image_root_dir"], image, "1"))]
                        t1_spin_post_dirs = [os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "2", slice) for slice in os.listdir(os.path.join(self.dset_info["image_root_dir"], image, "2"))]
                        t2_flair_dirs = [os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "3", slice) for slice in os.listdir(os.path.join(self.dset_info["image_root_dir"], image, "3"))]

                        label_dirs = [os.path.join(self.dset_info[dset_name]["label_root_dir"], image, "seg", slice) for slice in os.listdir(os.path.join(self.dset_info["label_root_dir"], image, "seg"))]

                        t1_images = np.stack([np.array(Image.open(im_dir).convert('L')) for im_dir in t1_im_dirs])
                        t1_spin_pre_image = np.stack([np.array(Image.open(im_dir).convert('L')) for im_dir in t1_spin_pre_dirs])
                        t1_spin_post_image = np.stack([np.array(Image.open(im_dir).convert('L')) for im_dir in t1_spin_post_dirs])
                        t2_flair_image = np.stack([np.array(Image.open(im_dir).convert('L')) for im_dir in t2_flair_dirs])

                        loaded_image = np.stack([t1_images, t1_spin_pre_image, t1_spin_post_image, t2_flair_image], -1)
                        loaded_label = np.stack([np.array(Image.open(im_dir)) for im_dir in label_dirs])

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        images.append(loaded_image)
                        segs.append(loaded_label)
                except Exception as e:
                    print(e)
                pbar.update(1)
        pbar.close()
        return images, segs