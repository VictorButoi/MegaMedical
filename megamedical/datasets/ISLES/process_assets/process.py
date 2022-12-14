import nibabel as nib
from tqdm.notebook import tqdm_notebook
import numpy as np
import glob
import os

from megamedical.src import processing as proc
from megamedical.src import preprocess_scripts as pps
from megamedical.utils.registry import paths
from megamedical.utils import proc_utils as put


class ISLES:

    def __init__(self):
        self.name = "ISLES"
        self.dset_info = {
            "ISLES2017":{
                "main":"ISLES",
                "image_root_dir":f"{paths['DATA']}/ISLES/original_unzipped/ISLES2017/training",
                "label_root_dir":f"{paths['DATA']}/ISLES/original_unzipped/ISLES2017/training",
                "modality_names":["ADC","MIT","TTP","Tmax","rCBF","rCBV"],
                "planes":[2],
                "clip_args": [0.5, 99.5],
                "norm_scheme":"MR"
            }
        }

    def proc_func(self,
                  subdset,
                  task,
                  pps_function,
                  parallelize=False,
                  load_images=True,
                  accumulate=False,
                  version=None,
                  show_imgs=False,
                  save=False,
                  show_hists=False,
                  resolutions=None,
                  redo_processed=True):
        assert not(version is None and save), "Must specify version for saving."
        assert subdset in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        proc_dir = os.path.join(paths['ROOT'], "processed")
        image_list = sorted(os.listdir(self.dset_info[subdset]["image_root_dir"]))
        subj_dict, res_dict = proc.process_image_list(process_ISLES_image,
                                                      proc_dir,
                                                      task,
                                                      image_list,
                                                      parallelize,
                                                      pps_function,
                                                      resolutions,
                                                      self.name,
                                                      subdset,
                                                      self.dset_info,
                                                      redo_processed,
                                                      load_images,
                                                      show_hists,
                                                      version,
                                                      show_imgs,
                                                      accumulate,
                                                      save)
        
        
global process_ISLES_image
def process_ISLES_image(item):
    dset_info = item['dset_info']
    # template follows processed/resolution/dset/midslice/subset/modality/plane/subject
    rtp = item["resolutions"] if item['redo_processed'] else put.check_proc_res(item)
    labels_found = glob.glob(os.path.join(dset_info[item['subdset']]["label_root_dir"], item['image'], "VSD.Brain.XX.O.OT*/VSD.Brain.XX.O.OT*.nii"))
    if len(rtp) > 0 and len(labels_found) > 0:
        subj_folder = os.path.join(dset_info[item['subdset']]["image_root_dir"], item['image'])

        prefix = "VSD.Brain.XX.O.MR_"
        label_dir = labels_found[0]

        if item['load_images']:
            ADC_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}ADC*/{prefix}ADC*.nii"))[0]
            MIT_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}MTT*/{prefix}MTT*.nii"))[0]
            TTP_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}TTP*/{prefix}TTP*.nii"))[0]
            Tmax_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}Tmax*/{prefix}Tmax*.nii"))[0]
            rCBF_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}rCBF*/{prefix}rCBF*.nii"))[0]
            rCBV_im_dir = glob.glob(os.path.join(subj_folder, f"{prefix}rCBV*/{prefix}rCBV*.nii"))[0]

            ADC = nib.load(ADC_im_dir).get_fdata()
            MIT = nib.load(MIT_im_dir).get_fdata()
            TTP = nib.load(TTP_im_dir).get_fdata()
            Tmax = nib.load(Tmax_im_dir).get_fdata()
            rCBF = nib.load(rCBF_im_dir).get_fdata()
            rCBV = nib.load(rCBV_im_dir).get_fdata()

            loaded_image = np.stack([ADC, MIT, TTP, Tmax, rCBF, rCBV], -1)
            loaded_label = nib.load(label_dir).get_fdata()

            assert not (loaded_image is None), "Invalid Image"
            assert not (loaded_label is None), "Invalid Label"
        else:
            loaded_image = None
            loaded_label = nib.load(label_dir).get_fdata()

        # Set the name to be saved
        subj_name = item['image'].split(".")[0]
        pps_function = item['pps_function']
        proc_return = pps_function(item['proc_dir'],
                                    item['version'],
                                    item['subdset'],
                                    subj_name, 
                                    loaded_image,
                                    loaded_label,
                                    dset_info[item['subdset']],
                                    show_hists=item['show_hists'],
                                    show_imgs=item['show_imgs'],
                                    resolutions=rtp,
                                    save=item['save'])

        return proc_return, subj_name
    else:
        return None, None