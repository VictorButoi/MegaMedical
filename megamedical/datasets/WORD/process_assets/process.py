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
import rawpy
import nibabel as nib
import nibabel.processing as nip


#New line!
from megamedical.utils.registry import paths


class WORD:

    def __init__(self):

        self.dataset_info_dictionary = {
            "retrieved_2022_05_01":{
                "main":"WORD",
                "image_root_dir":"/share/sablab/nfs02/users/gid-dalcaav/data/originals/WORD/processed/unzipped/WORD-V0.1.0-remapped-subset/images",
                "label_root_dir":"/share/sablab/nfs02/users/gid-dalcaav/data/originals/WORD/processed/unzipped/WORD-V0.1.0-remapped-subset/labels",
                "modality_names":["CT"],
                "planes":[0, 1, 2],
                "clip_args":[-500,1000],
                "norm_scheme":"CT",
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
        image_list = os.listdir(self.dset_info["image_root_dir"])
        with tqdm(total=len(image_list), desc=f'Processing: {dset_name}', unit='image') as pbar:
            for sub_num, image in enumerate(image_list):
                try:
                    if redo_processed or (len(glob.glob(os.path.join(processed_dir, "*", image))) == 0):
                        im_dir = os.path.join(self.dset_info["image_root_dir"], image)
                        label_dir = os.path.join(self.dset_info["label_root_dir"], image)

                        assert os.path.isfile(im_dir), "Valid image dir required!"
                        assert os.path.isfile(label_dir), "Valid label dir required!"

                        loaded_image = preprocess_scripts.resample_nib(nib.load(im_dir))
                        loaded_label = preprocess_scripts.resample_mask_to(nib.load(label_dir), loaded_image)

                        loaded_image = np.array(loaded_image.dataobj)
                        loaded_label = np.array(loaded_label.dataobj)

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        image_name = f"subj_{sub_num}"

                        images.append(loaded_image)
                        segs.append(loaded_label)
                except Exception as e:
                    print(e)
                pbar.update(1)
        pbar.close()
        return images, segs