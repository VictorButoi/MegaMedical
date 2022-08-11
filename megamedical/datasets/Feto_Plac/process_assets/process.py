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


class Feto_Plac:

    def __init__(self):

        self.dataset_info_dictionary = {
            "retreived_2022_03_09":{
                "main": "Feto_Plac",
                "image_root_dir":"/home/vib9/src/data/Feto_Plac/processed/original_unzipped/retreived_2022_03_09/FetoscopyPlacentaDataset/Vessel_segmentation_annotations",
                "label_root_dir":"/home/vib9/src/data/Feto_Plac/processed/original_unzipped/retreived_2022_03_09/FetoscopyPlacentaDataset/Vessel_segmentation_annotations",
                "modality_names":["Video"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None,
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
            for video in image_list:
                vid_dir = os.path.join(self.dset_info[dset_name]["image_root_dir"], video)
                for frame in os.listdir(os.path.join(vid_dir, "images")):
                    image = f"{video}_{frame}"
                    try:
                        if redo_processed or (len(glob.glob(os.path.join(processed_dir, "*", image))) == 0):
                            im_dir = os.path.join(vid_dir, "images", frame)
                            label_dir = os.path.join(vid_dir, "masks_gt", f"{frame[:-4]}_mask.png")

                            loaded_image = np.array(Image.open(im_dir).convert('L'))
                            loaded_label = np.array(Image.open(label_dir).convert('L'))

                            assert not (loaded_image is None), "Invalid Image"
                            assert not (loaded_label is None), "Invalid Label"

                            images.append(loaded_image)
                        segs.append(loaded_label)
                    except Exception as e:
                        print(e)
                    pbar.update(1)
        pbar.close()
        return images, segs