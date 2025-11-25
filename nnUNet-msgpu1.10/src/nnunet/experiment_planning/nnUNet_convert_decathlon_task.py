# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""convert decathlon task"""
########### 修改 ##########
import sys
sys.path.append('./')

import os

NUM_TRAIN = int(os.environ.get("NUM_TRAIN", 210))
NUM_TEST = int(os.environ.get("NUM_TEST", 90))

import logging  # 可视化模块
import time
from tqdm import tqdm  # tqdm 是一个命令行进度条库，pip install tqdm

from batchgenerators.utilities.file_and_folder_operations import subfolders, subfiles, join, os

from src.nnunet.configuration import default_num_threads
from src.nnunet.experiment_planning.utils import split_4d
from src.nnunet.paths import nnUNet_raw_data
from src.nnunet.utilities.file_endings import remove_trailing_slash

def setup_logger(log_file=None, level=logging.INFO):
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

def crawl_and_remove_hidden_from_decathlon(folder):
    """crawl and remove hidden from decathlon"""
    folder = remove_trailing_slash(folder)
    assert folder.split('/')[-1].startswith("Task"), "This does not seem to be a decathlon folder. Please give me a" \
                                                     "folder that starts with TaskXX and has the subfolders imagesTr," \
                                                     "labelsTr and imagesTs"
    subf = subfolders(folder, join=False)
    assert 'imagesTr' in subf, "This does not seem to be a decathlon folder. Please give me a " \
                               "folder that starts with TaskXX and has the subfolders imagesTr, " \
                               "labelsTr and imagesTs"
    assert 'imagesTs' in subf, "This does not seem to be a decathlon folder. Please give me a " \
                               "folder that starts with TaskXX and has the subfolders imagesTr, " \
                               "labelsTr and imagesTs"
    assert 'labelsTr' in subf, "This does not seem to be a decathlon folder. Please give me a " \
                               "folder that starts with TaskXX and has the subfolders imagesTr, " \
                               "labelsTr and imagesTs"
    _ = [os.remove(i) for i in subfiles(folder, prefix=".")]
    _ = [os.remove(i) for i in subfiles(join(folder, 'imagesTr'), prefix=".")]
    _ = [os.remove(i) for i in subfiles(join(folder, 'labelsTr'), prefix=".")]
    _ = [os.remove(i) for i in subfiles(join(folder, 'imagesTs'), prefix=".")]


import glob
import shutil
import json
import SimpleITK as sitk
import numpy as np


def normalize_task_directory(task_path):
    """Ensure task directory follows TaskXX_name convention with two-digit ID."""
    task_path = remove_trailing_slash(task_path)
    parent_dir = os.path.dirname(task_path)
    folder_name = os.path.basename(task_path)

    if not folder_name.startswith("Task"):
        raise ValueError(f"任务目录必须以 'Task' 开头，当前为: {folder_name}")
    if "_" not in folder_name:
        raise ValueError(f"任务目录需包含下划线分隔 ID 与名称，当前为: {folder_name}")

    prefix, suffix = folder_name.split("_", 1)
    digits = prefix[4:]
    if not digits.isdigit():
        raise ValueError(f"Task 后必须跟数字，当前为: {prefix}")

    task_id = int(digits)
    if task_id < 0 or task_id > 99:
        raise ValueError(f"Task 编号需在 0-99 之间，当前为: {task_id}")

    normalized_folder = f"Task{task_id:02d}_{suffix}"
    normalized_path = os.path.join(parent_dir, normalized_folder)

    if normalized_path != task_path:
        os.makedirs(parent_dir, exist_ok=True)
        if os.path.exists(task_path):
            if os.path.exists(normalized_path):
                logging.info("检测到标准目录已存在，直接使用: %s", normalized_folder)
            else:
                shutil.move(task_path, normalized_path)
                logging.info("已自动将输入目录重命名为 %s", normalized_folder)
        else:
            logging.info("原始目录不存在，将直接使用标准命名路径: %s", normalized_folder)
        task_path = normalized_path

    return task_path, task_id, suffix


def update_dataset_json_with_modality_suffix(task_suffix, task_id):
    """
    在 split_4d 之后，将 dataset.json 中的影像路径补上 `_0000` 后缀，
    以匹配拆模态后的文件命名。
    """
    output_folder = join(nnUNet_raw_data, f"Task{task_id:03d}_{task_suffix}")
    dataset_json_path = join(output_folder, "dataset.json")

    if not os.path.isfile(dataset_json_path):
        logging.warning("未找到 dataset.json: %s，跳过后缀补全", dataset_json_path)
        return

    with open(dataset_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def _add_suffix(path):
        if not path.endswith(".nii.gz"):
            return path
        if path.endswith("_0000.nii.gz"):
            return path
        return path[:-7] + "_0000.nii.gz"

    updated = False
    for entry in data.get("training", []):
        new_path = _add_suffix(entry["image"])
        if new_path != entry["image"]:
            entry["image"] = new_path
            updated = True

    tests = data.get("test", [])
    for idx, path in enumerate(tests):
        new_path = _add_suffix(path)
        if new_path != path:
            tests[idx] = new_path
            updated = True

    if updated:
        with open(dataset_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logging.info("已为 dataset.json 中的影像路径补全 `_0000` 后缀。")
    else:
        logging.info("dataset.json 中的影像路径已包含 `_0000` 后缀，无需修改。")


def transform(image,newSpacing, resamplemethod=sitk.sitkNearestNeighbor):
    # 设置一个Filter
    resample = sitk.ResampleImageFilter()
    # 初始的体素块尺寸
    originSize = image.GetSize()
    # 初始的体素间距
    originSpacing = image.GetSpacing()
    print('\noriginSpacing', originSpacing)
    newSize = [
        int(np.round(originSize[0] * originSpacing[0] / newSpacing[0])),
        int(np.round(originSize[1] * originSpacing[1] / newSpacing[1])),
        int(np.round(originSize[2] * originSpacing[2] / newSpacing[2]))
    ]
    print('current size:',newSize)

    # 沿着x,y,z,的spacing（3）
    # The sampling grid of the output space is specified with the spacing along each dimension and the origin.
    resample.SetOutputSpacing(newSpacing)
    # 设置original
    resample.SetOutputOrigin(image.GetOrigin())
    # 设置方向
    resample.SetOutputDirection(image.GetDirection())
    resample.SetSize(newSize)
    # 设置插值方式
    resample.SetInterpolator(resamplemethod)
    # 设置transform
    resample.SetTransform(sitk.Euler3DTransform())
    # 默认像素值   resample.SetDefaultPixelValue(image.GetPixelIDValue())
    return resample.Execute(image)

def raw_convert_task_architecture(raw_path, task_path):
    
    all_dirs = sorted(glob.glob(join(raw_path, 'case_*')))
    train_dirs = all_dirs[:NUM_TRAIN]
    test_dirs  = all_dirs[NUM_TRAIN:NUM_TRAIN + NUM_TEST]
    
    os.makedirs(join(task_path, 'imagesTr'), exist_ok=True)
    os.makedirs(join(task_path, 'labelsTr'), exist_ok=True)
    os.makedirs(join(task_path, 'imagesTs'), exist_ok=True)
    
    # 创建json文件
    dataset_json = { 
                    "name": "kits19", 
                    "description": "MindSpore AI",
                    "reference": "the 2019 Kidney Tumor Segmentation Challenge",
                    "tensorImageSize": "3D",
                    "modality":{"0":"CT"},
                    "labels":{"0":"Background","1": "Kidney","2": "Tumor"},
                    "numTraining": NUM_TRAIN, #   50 
                    "numTest": NUM_TEST, # 50
                    "training":[],
                    "test":[]
                    }
    
    # 创建训练集
    """for train_dir in train_dirs:
        case_name = os.path.basename(train_dir)
        
        train_img = join(train_dir, 'imaging.nii.gz')

        img_itk = sitk.ReadImage(train_img)
        print('origin size:', img_itk.GetSize())
        new_itk = transform(img_itk, [3.22, 1.62, 1.62], sitk.sitkBSpline) # sitk.sitkLinear
        sitk.WriteImage(new_itk, join(task_path, 'imagesTr', 'kits_' + case_name + '.nii.gz'))
        # shutil.copy(train_img, join(task_path, 'imagesTr', 'kits_' + case_name + '.nii.gz'))
        
        train_label = join(train_dir, 'segmentation.nii.gz')

        label_itk = sitk.ReadImage(train_label)
        print('origin size:', label_itk.GetSize())
        new_itk = transform(label_itk, [3.22, 1.62, 1.62])
        sitk.WriteImage(new_itk, join(task_path, 'labelsTr', 'kits_' + case_name + '.nii.gz'))
        # shutil.copy(train_label, join(task_path, 'labelsTr', 'kits_' + case_name + '.nii.gz'))
        
        dataset_json["training"].append({"image":'./imagesTr/kits_' + case_name + '.nii.gz', "label":'./labelsTr/kits_' + case_name + '.nii.gz'})
    """
    logging.info(f"共发现 {len(all_dirs)} 个病例，将 {NUM_TRAIN} 用作训练，{NUM_TEST} 用作测试。")

    for idx, train_dir in enumerate(tqdm(train_dirs, desc="处理训练集", ncols=100)):
        case_name = os.path.basename(train_dir)
        logging.debug(f"正在处理 {case_name}")

        train_img = join(train_dir, 'imaging.nii.gz')
        img_itk = sitk.ReadImage(train_img)
        new_itk = transform(img_itk, [3.22, 1.62, 1.62], sitk.sitkBSpline)
        sitk.WriteImage(new_itk, join(task_path, 'imagesTr', 'kits_' + case_name + '.nii.gz'))

        train_label = join(train_dir, 'segmentation.nii.gz')
        label_itk = sitk.ReadImage(train_label)
        new_itk = transform(label_itk, [3.22, 1.62, 1.62])
        sitk.WriteImage(new_itk, join(task_path, 'labelsTr', 'kits_' + case_name + '.nii.gz'))

        dataset_json["training"].append({"image":'./imagesTr/kits_' + case_name + '.nii.gz', "label":'./labelsTr/kits_' + case_name + '.nii.gz'})

    logging.info("训练集重采样完成 ✅")

    # 创建测试集
    """
    for test_dir in test_dirs:
        case_name = os.path.basename(test_dir)
        test_img = join(test_dir, 'imaging.nii.gz')
        shutil.copy(test_img, join(task_path, 'imagesTs', 'kits_' + case_name + '.nii.gz'))
        
        dataset_json["test"].append('./imagesTs/kits_' + case_name + '.nii.gz')
    """
    for test_dir in tqdm(test_dirs, desc="复制测试集", ncols=100):
        case_name = os.path.basename(test_dir)
        test_img = join(test_dir, 'imaging.nii.gz')
        shutil.copy(test_img, join(task_path, 'imagesTs', 'kits_' + case_name + '.nii.gz'))

        dataset_json["test"].append('./imagesTs/kits_' + case_name + '.nii.gz')


    with open(join(task_path, "dataset.json"),'w') as file:
        json.dump(dataset_json,file,indent=4)
        
def main():
    """The MSD provides data as 4D Niftis with the modality being the first"""

    import argparse
    parser = argparse.ArgumentParser(description="The MSD provides data as 4D Niftis with the modality being the first"
                                                 " dimension. We think this may be cumbersome for some users and "
                                                 "therefore expect 3D niftixs instead, with one file per modality. "
                                                 "This utility will convert 4D MSD data into the format nnU-Net "
                                                 "expects")
    parser.add_argument("-r", help="original raw data path", required=True)
    parser.add_argument("-i", help="Input folder. Must point to a TaskXX_TASKNAME folder as downloaded from the MSD "
                                   "website", required=True)
    parser.add_argument("-p", required=False, default=default_num_threads, type=int,
                        help="Use this to specify how many processes are used to run the script. "
                             "Default is %d" % default_num_threads)
    parser.add_argument("-output_task_id", required=False, default=None, type=int,
                        help="If specified, this will overwrite the task id in the output folder. If unspecified, the "
                             "task id of the input folder will be used.")
    args = parser.parse_args()
    
    setup_logger("convert_task.log", level=logging.INFO)
    start_time = time.time()
    logging.info("===== 开始转换 KiTS19 数据集 =====")
    logging.info(f"原始数据目录: {args.r}")
    logging.info(f"目标任务目录: {args.i}")
    
    # 先将原始下载的kits19的数据组织结构调整成nnUNet的组织结构
    print('-----begin convert kist9 dirs architecture')
    normalized_task_path, inferred_task_id, task_suffix = normalize_task_directory(args.i)

    raw_convert_task_architecture(args.r, normalized_task_path)

    crawl_and_remove_hidden_from_decathlon(normalized_task_path)

    split_4d(normalized_task_path, args.p, args.output_task_id)
    output_task_id = args.output_task_id if args.output_task_id is not None else inferred_task_id
    update_dataset_json_with_modality_suffix(task_suffix, output_task_id)
    print('-----finish convert kits19 dirs architecture')

    end_time = time.time()
    elapsed = (end_time - start_time) / 60
    logging.info(f"转换完成 ✅ 总耗时: {elapsed:.2f} 分钟")
    logging.info("日志已保存至 convert_task.log")

if __name__ == "__main__":
    main()
