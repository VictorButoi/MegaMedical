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

#New line!
from megamedical.utils.registry import paths


class CheXplanation:

    def __init__(self):
        
        self.dataset_info_dictionary = {
            "retreived_2022_03_04":{
                "main":"CoNSeP",
                "image_root_dir":"/home/vib9/src/data/CoNSeP/processed/original_unzipped/retreived_2022_03_04/CoNSeP/Train/Images",
                "label_root_dir":"/home/vib9/src/data/CoNSeP/processed/original_unzipped/retreived_2022_03_04/CoNSeP/Train/Labels",
                "modality_names":["NA"],
                "planes":[0],
                "clip_args": None,
                "norm_scheme": None,
                "do_clip": False,
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
                        if dset_name == "CT":
                            DicomDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "DICOM_anon")
                            GroundDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "Ground")
                        else:
                            DicomDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "T2SPIR/DICOM_anon")
                            GroundDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "T2SPIR/Ground")

                        planes = []
                        for plane in os.listdir(DicomDir):
                            planes.append(dicom.dcmread(os.path.join(DicomDir, plane)).pixel_array)
                        loaded_image = np.stack(planes)

                        gt_planes = []
                        for gt_plane in os.listdir(GroundDir):
                            gt_planes.append(np.array(Image.open(os.path.join(GroundDir, gt_plane)).convert('L')))
                        loaded_label = np.stack(gt_planes)

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        images.append(loaded_image)
                        segs.append(loaded_label)
                except Exception as e:
                    print(e)
                pbar.update(1)
        pbar.close()
        return images, segs