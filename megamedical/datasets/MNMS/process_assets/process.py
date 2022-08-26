import nibabel as nib
from tqdm import tqdm
import numpy as np
import glob
import os

#New line!
from megamedical.src import preprocess_scripts as pps
from megamedical.utils.registry import paths
from megamedical.utils import proc_utils as put


class MNMS:

    def __init__(self):
        self.name = "MNMS"
        self.dset_info = {
            "2020":{
                "main":"MNMS",
                "image_root_dir":f"{paths['DATA']}/MNMS/original_unzipped/2020/OpenDataset",
                "label_root_dir":f"{paths['DATA']}/MNMS/original_unzipped/2020/OpenDataset",
                "modality_names":["T1"],
                "planes":[2],
                "clip_args": [0.5, 99.5],
                "norm_scheme":"MR",
                "do_clip":True,
                "proc_size":256
            }
        }

    def proc_func(self,
                  dset_name,
                  proc_func,
                  version=None,
                  show_hists=False,
                  show_imgs=False,
                  save_slices=False,
                  redo_processed=True):
        assert not(version is None and save_slices), "Must specify version for saving."
        assert dset_name in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        proc_dir = pps.make_processed_dir(self.name, dset_name, save_slices, version, self.dset_info[dset_name])
        image_list = os.listdir(self.dset_info[dset_name]["image_root_dir"])
        with tqdm(total=len(image_list), desc=f'Processing: {dset_name}', unit='image') as pbar:
            for image in image_list:
                try:
                    proc_dir_template = os.path.join(proc_dir, f"megamedical_v{version}", dset_name, "*", image)
                    if redo_processed or (len(glob.glob(proc_dir_template)) == 0):
                        im_dir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, f"{image}_sa.nii.gz")
                        label_dir = os.path.join(self.dset_info[dset_name]["label_root_dir"], image, f"{image}_sa_gt.nii.gz")
                        
                        loaded_image = nib.load(im_dir)
                        loaded_label = nib.load(label_dir)
                        
                        loaded_image = loaded_image.get_fdata()
                        loaded_label = loaded_label.get_fdata()
                        
                        # What is this? Why 0?
                        loaded_image = loaded_image[...,0]
                        loaded_label = loaded_label[...,0]

                        assert not (loaded_image is None), "Invalid Image"
                        assert not (loaded_label is None), "Invalid Label"

                        proc_func(proc_dir,
                                  version,
                                  dset_name,
                                  image, 
                                  loaded_image,
                                  loaded_label,
                                  self.dset_info[dset_name],
                                  show_hists=show_hists,
                                  show_imgs=show_imgs,
                                  save_slices=save_slices)
                except Exception as e:
                    print(e)
                    #raise ValueError
                pbar.update(1)
        pbar.close()