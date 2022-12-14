import nibabel as nib
from tqdm.notebook import tqdm_notebook
from PIL import Image
import numpy as np
import numpy as np
import glob
import os

from megamedical.src import processing as proc
from megamedical.src import preprocess_scripts as pps
from megamedical.utils.registry import paths
from megamedical.utils import proc_utils as put


class PanNuke:

    def __init__(self):
        self.name = "PanNuke"
        self.dset_info = {
            "Fold1":{
                "main":"PanNuke",
                "image_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold1/images/fold1/images.npy",
                "label_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold1/masks/fold1/masks.npy",
                "modality_names":["NA"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None
            },
            "Fold2":{
                "main":"PanNuke",
                "image_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold2/images/fold2/images.npy",
                "label_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold2/masks/fold2/masks.npy",
                "modality_names":["NA"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None
            },
            "Fold3":{
                "main":"PanNuke",
                "image_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold3/images/fold3/images.npy",
                "label_root_dir":f"{paths['DATA']}/PanNuke/original_unzipped/retreived_2022_03_04/Fold3/masks/fold3/masks.npy",
                "modality_names":["NA"],
                "planes":[0],
                "clip_args":None,
                "norm_scheme":None
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
        image_array = np.load(self.dset_info[subdset]["image_root_dir"], mmap_mode='r')
        label_array = np.load(self.dset_info[subdset]["label_root_dir"], mmap_mode='r')
        image_list = [str(idx) for idx in range(image_array.shape[0])]
        subj_dict, res_dict = proc.process_image_list(process_PanNuke_image,
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
                                                      save,
                                                      preloaded_images=image_array,
                                                      preloaded_labels=label_array)
        if accumulate:
            return proc_dir, subj_dict, res_dict

        
global process_PanNuke_image
def process_PanNuke_image(item):
    dset_info = item['dset_info']
    # template follows processed/resolution/dset/midslice/subset/modality/plane/subject
    file_name = item['image']
    item['image'] = file_name.split(".")[0]
    rtp = item["resolutions"] if item['redo_processed'] else put.check_proc_res(item)
    if len(rtp) > 0:
        # "clever" hack to get Image.fromarray to work
        loaded_image = item["image_array"][int(file_name),...]
        loaded_image = 0.2989*loaded_image[...,0] + 0.5870*loaded_image[...,1] + 0.1140*loaded_image[...,2] 

        loaded_label = np.transpose(item["label_array"][int(file_name),...], (2, 0, 1))
        background_label = np.zeros((1, loaded_label.shape[1], loaded_label.shape[2]))
        loaded_label = np.concatenate([background_label, loaded_label], axis=0)
        loaded_label = np.argmax(loaded_label, axis=0)

        assert not (loaded_image is None), "Invalid Image"
        assert not (loaded_label is None), "Invalid Label"

        # Set the name to be saved
        subj_name = item['image']
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