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
import universeg as uvs
from scripts import preprocess_scripts

dataset_info_dictionary = {
    "HammersAtlasDatabase":{
        "main":"BrainDevelopment",
        "image_root_dir":"/home/vib9/src/data/BrainDevelopment/processed/original_unzipped/HammersAtlasDatabase/Hammers67n20/images",
        "label_root_dir":"/home/vib9/src/data/BrainDevelopment/processed/original_unzipped/HammersAtlasDatabase/Hammers67n20/segs",
        "modality_names":["T1"],
        "planes":[0, 1, 2],
        "clip_args":None,
        "norm_scheme":"MR",
        "do_clip":True,
        "proc_size":256
    },
    "PediatricAtlas":{
        "main":"BrainDevelopment",
        "image_root_dir":"/home/vib9/src/data/BrainDevelopment/processed/original_unzipped/PediatricAtlas/images",
        "label_root_dir":"/home/vib9/src/data/BrainDevelopment/processed/original_unzipped/PediatricAtlas/segmentations",
        "modality_names":["T1"],
        "planes":[0, 1, 2],
        "clip_args":None,
        "norm_scheme":"MR",
        "do_clip":True,
        "proc_size":256
    }
}


def proc_func(dset_name,
            dset_info, 
            save_slices=False, 
            show_hists=False,
            show_imgs=False,
            redo_processed=True):
    
    processed_dir = preprocess_scripts.make_processed_dir(dset_name, dset_info, save_slices)
    
    image_list = os.listdir(dset_info["image_root_dir"])
    with tqdm(total=len(image_list), desc=f'Processing: {dset_name}', unit='image') as pbar:
        for image in image_list:
            try:
                if redo_processed or (len(glob.glob(os.path.join(processed_dir, "*", image))) == 0):
                    im_dir = os.path.join(dset_info["image_root_dir"], image)

                    if dset_name == "HammersAtlasDatabase":
                        label_dir = os.path.join(dset_info["label_root_dir"], image.replace(".nii.gz", "-seg.nii.gz"))
                        loaded_image = np.array(nib.load(im_dir).dataobj)
                        loaded_label = np.array(nib.load(label_dir).dataobj)[...,0]
                    else:
                        label_dir = os.path.join(dset_info["label_root_dir"], image.replace(".nii.gz", "_seg_83ROI.nii.gz"))
                        loaded_image = np.array(nib.load(im_dir).dataobj)[...,0]
                        loaded_label = np.array(nib.load(label_dir).dataobj)

                    print(loaded_label.shape)
                    print(loaded_image.shape)

                    assert not (loaded_image is None), "Invalid Image"
                    assert not (loaded_label is None), "Invalid Label"

                    preprocess_scripts.produce_slices(processed_dir,
                                    dset_name,
                                    loaded_image,
                                    loaded_label,
                                    dset_info["modality_names"],
                                    image, 
                                    planes=dset_info["planes"],
                                    proc_size=dset_info["proc_size"],
                                    save_slices=save_slices, 
                                    show_hists=show_hists,
                                    show_imgs=show_imgs,
                                    do_clip=dset_info["do_clip"],
                                    clip_args=dset_info["clip_args"],
                                    norm_scheme=dset_info["norm_scheme"])
            except Exception as e:
                print(e)
            pbar.update(1)
    pbar.close()

def process_datasets(dtp,
                    save_volumes, 
                    show_imgs, 
                    show_hists,
                    redo_processed):
    for subset in dtp:
        proc_func(
                dset_name=subset,
                dset_info=dataset_info_dictionary[subset],
                save_slices=save_volumes,
                show_hists=show_hists,
                show_imgs=show_imgs,
                redo_processed=redo_processed
        )

if __name__ == "__main__":
    dtp = ["HammersAtlasDatabase", "PediatricAtlas"]
    process_datasets(dtp=dtp, save_volumes=True, show_imgs=False, show_hists=False, redo_processed=True)
