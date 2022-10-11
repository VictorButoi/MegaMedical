from PIL import Image
import pydicom as dicom
import numpy as np
from tqdm.notebook import tqdm_notebook
import glob
import os

#New line!
from megamedical.src import preprocess_scripts as pps
from megamedical.utils.registry import paths
from megamedical.utils import proc_utils as put


class CHAOS:

    def __init__(self):
        self.name = "CHAOS"
        self.dset_info = {
            "CT":{
                "main":"CHAOS",
                "image_root_dir":f"{paths['DATA']}/CHAOS/original_unzipped/retreived_2022_03_08/Train_Sets/CT",
                "label_root_dir":f"{paths['DATA']}/CHAOS/original_unzipped/retreived_2022_03_08/Train_Sets/CT",
                "modality_names":["CT"],
                "planes":[0],
                "labels": [1,2,3],
                "clip_args": [600,1500],
                "norm_scheme": "CT"
            },
            "MR":{
                "main":"CHAOS",
                "image_root_dir":f"{paths['DATA']}/CHAOS/original_unzipped/retreived_2022_03_08/Train_Sets/MR",
                "label_root_dir":f"{paths['DATA']}/CHAOS/original_unzipped/retreived_2022_03_08/Train_Sets/MR",
                "modality_names":["T2"],
                "planes":[0],
                "labels": [1,2,3],
                "clip_args": [0.5, 99.5],
                "norm_scheme": "MR"
            }
        }

    def proc_func(self,
                  dset_name,
                  proc_func,
                  load_images=True,
                  accumulate=False,
                  version=None,
                  show_imgs=False,
                  save=False,
                  show_hists=False,
                  resolutions=None,
                  redo_processed=True):
        assert not(version is None and save), "Must specify version for saving."
        assert dset_name in self.dset_info.keys(), "Sub-dataset must be in info dictionary."
        image_list = sorted(os.listdir(self.dset_info[dset_name]["image_root_dir"]))
        proc_dir = os.path.join(paths['ROOT'], "processed")
        res_dict = {}
        for resolution in resolutions:
            accumulator = []
            for image in tqdm_notebook(image_list, desc=f'Processing: {dset_name}'):
                try:
                    # template follows processed/resolution/dset/midslice/subset/modality/plane/subject
                    template_root = os.path.join(proc_dir, f"res{resolution}", self.name)
                    mid_proc_dir_template = os.path.join(template_root, f"midslice_v{version}", dset_name, "*/*", image)
                    max_proc_dir_template = os.path.join(template_root, f"maxslice_v{version}", dset_name, "*/*", image)
                    if redo_processed or (len(glob.glob(mid_proc_dir_template)) == 0) or (len(glob.glob(max_proc_dir_template)) == 0):
                        if dset_name == "CT":
                            DicomDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "DICOM_anon")
                            GroundDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "Ground")
                        else:
                            DicomDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "T2SPIR/DICOM_anon")
                            GroundDir = os.path.join(self.dset_info[dset_name]["image_root_dir"], image, "T2SPIR/Ground")

                        if load_images:
                            planes = []
                            for plane in os.listdir(DicomDir):
                                planes.append(dicom.dcmread(os.path.join(DicomDir, plane)).pixel_array)
                            loaded_image = np.stack(planes)

                            gt_planes = []
                            for gt_plane in os.listdir(GroundDir):
                                gt_planes.append(np.array(Image.open(os.path.join(GroundDir, gt_plane)).convert('L')))
                            loaded_label = np.stack(gt_planes)

                            assert not (loaded_label is None), "Invalid Label"
                            assert not (loaded_image is None), "Invalid Image"
                        else:
                            loaded_image = None
                            gt_planes = []
                            for gt_plane in os.listdir(GroundDir):
                                gt_planes.append(np.array(Image.open(os.path.join(GroundDir, gt_plane)).convert('L')))
                            loaded_label = np.stack(gt_planes)

                        proc_return = proc_func(proc_dir,
                                              version,
                                              dset_name,
                                              image, 
                                              loaded_image,
                                              loaded_label,
                                              self.dset_info[dset_name],
                                              show_hists=show_hists,
                                              show_imgs=show_imgs,
                                              res=resolution,
                                              save=save)

                        if accumulate:
                            accumulator.append(proc_return)
                except Exception as e:
                    print(e)
                    #raise ValueError
            res_dict[resolution] = accumulator
        if accumulate:
            return proc_dir, res_dict