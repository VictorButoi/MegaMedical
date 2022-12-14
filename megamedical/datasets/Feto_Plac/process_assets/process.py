from PIL import Image
from tqdm.notebook import tqdm_notebook
import numpy as np
import glob
import os

#New line!
from megamedical.src import preprocess_scripts as pps
from megamedical.utils.registry import paths
from megamedical.utils import proc_utils as put


class Feto_Plac:

    def __init__(self):
        self.name = "Feto_Plac"
        self.dset_info = {
            "retreived_2022_03_09":{
                "main": "Feto_Plac",
                "image_root_dir":f"{paths['DATA']}/Feto_Plac/original_unzipped/retreived_2022_03_09/FetoscopyPlacentaDataset/Vessel_segmentation_annotations",
                "label_root_dir":f"{paths['DATA']}/Feto_Plac/original_unzipped/retreived_2022_03_09/FetoscopyPlacentaDataset/Vessel_segmentation_annotations",
                "modality_names":["Video"],
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
        assert redo_processed==True, "Redo-Processed = False not implemented for Feto_plac."
        assert not(version is None and save), "Must specify version for saving."
        assert subdset in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        video_list = sorted(os.listdir(self.dset_info[subdset]["image_root_dir"]))
        proc_dir = os.path.join(paths['ROOT'], "processed")
        
        res_dict = {res:[] for res in resolutions}
        subj_dict = {res:[] for res in resolutions}
        
        for video in tqdm_notebook(video_list, desc=f'Processing: {subdset}'):
            vid_dir = os.path.join(self.dset_info[subdset]["image_root_dir"], video)
            frameset = sorted(os.listdir(os.path.join(vid_dir, "images")))
            for frame in frameset:
                im_dir = os.path.join(vid_dir, "images", frame)
                label_dir = os.path.join(vid_dir, "masks_gt", f"{frame[:-4]}_mask.png")

                if load_images:
                    loaded_image = np.array(Image.open(im_dir).convert('L'))
                    loaded_label = np.array(Image.open(label_dir).convert('L'))
                    assert not (loaded_label is None), "Invalid Label"
                    assert not (loaded_image is None), "Invalid Image"
                else:
                    loaded_image = None
                    loaded_label = np.array(Image.open(label_dir).convert('L'))

                subj_name = f"{video}_{frame}"
                proc_return = pps_function(proc_dir,
                                            version,
                                            subdset,
                                            subj_name, 
                                            loaded_image,
                                            loaded_label,
                                            self.dset_info[subdset],
                                            show_hists=show_hists,
                                            show_imgs=show_imgs,
                                            resolutions=resolutions,
                                            save=save)

                if accumulate:
                    for res in resolutions:
                        res_dict[res].append(proc_return[res])
                        subj_dict[res].append(subj_name)
                        
        if accumulate:
            return proc_dir, subj_dict, res_dict