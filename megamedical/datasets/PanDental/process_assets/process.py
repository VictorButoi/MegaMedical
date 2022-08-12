from ast import DictComp
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


class PanDental:

    def __init__(self):
        self.name = "PanDental"
        self.dset_info = {
            "v1":{
                "main": "PanDental",
                "image_root_dir":f"{paths['ROOT']}/megamedical/datasets/PanDental/processed/original_unzipped/v1/Images",
                "label_root_dir":f"{paths['ROOT']}/megamedical/datasets/PanDental/processed/original_unzipped/v1/orig_masks",
                "modality_names":["XRay"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None,
                "do_clip":False,
                "proc_size":256
            },
            "v2":{
                "main": "PanDental",
                "image_root_dir":f"{paths['ROOT']}/megamedical/datasets/PanDental/processed/original_unzipped/v2/Images",
                "label_root_dir":f"{paths['ROOT']}/megamedical/datasets/PanDental/processed/original_unzipped/v2/Segmentation1",
                "modality_names":["XRay"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None,
                "do_clip":False,
                "proc_size":256
            }
        }

    def proc_func(self,
                dset_name,
                show_hists=False,
                  show_imgs=False,
                  save_slices=False,
                redo_processed=True):
        assert dset_name in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        proc_dir = pps.make_processed_dir(dset_name, self.dset_info[dset_name], save_slices)
        image_list = os.listdir(self.dset_info[dset_name]["image_root_dir"])
        with tqdm(total=len(image_list), desc=f'Processing: {dset_name}', unit='image') as pbar:
            for image in image_list:
                try:
                    if redo_processed or (len(glob.glob(os.path.join(processed_dir, "*", image))) == 0):
                        im_dir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image)
                        label_dir = os.path.join(self.dset_info[dset_name]["label_root_dir"], image)

                        loaded_image = np.array(Image.open(im_dir).convert('L'))

                        if dset_name == "v1":
                            loaded_label = np.array(Image.open(label_dir))[...,0]
                        else:
                            loaded_label = (np.array(Image.open(label_dir)) > 40) + 0

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        pps.produce_slices(proc_dir,
                                          dset_name,
                                          loaded_image,
                                          loaded_label,
                                          self.dset_info[dset_name],
                                          show_hists=show_hists,
                                          show_imgs=show_imgs)
                except Exception as e:
                    print(e)
                pbar.update(1)
        pbar.close()