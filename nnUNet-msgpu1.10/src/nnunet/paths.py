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

"""paths module"""

import json
import os
from pathlib import Path

from batchgenerators.utilities.file_and_folder_operations import maybe_mkdir_p, join

# do not modify these unless you know what you are doing
my_output_identifier = "nnUNet"
default_plans_identifier = "nnUNetPlansv2.1"
default_data_identifier = 'nnUNetData_plans_v2.1'
default_trainer = "nnUNetTrainerV2"
default_cascade_trainer = "nnUNetTrainerV2CascadeFullRes"

"""
PLEASE READ paths.md FOR INFORMATION TO HOW TO SET THIS UP
"""

def _load_paths_from_config():
    """
    Read default nnU-Net paths from path_config.json so users do not need to export env vars.
    Environment variables still override these values if present.
    """
    config_file = Path(__file__).resolve().parents[2] / "path_config.json"
    if not config_file.exists():
        return {}
    try:
        config_data = json.loads(config_file.read_text())
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Could not read path config {config_file}: {exc}")
        return {}

    resolved = {}
    for key in ("nnUNet_raw_data_base", "nnUNet_preprocessed", "RESULTS_FOLDER"):
        value = config_data.get(key)
        if not value:
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (config_file.parent / path).resolve()
        resolved[key] = str(path)
    return resolved


config_paths = _load_paths_from_config()
base = os.environ.get("nnUNet_raw_data_base") or config_paths.get("nnUNet_raw_data_base")
preprocessing_output_dir = os.environ.get("nnUNet_preprocessed") or config_paths.get("nnUNet_preprocessed")
network_training_output_dir_base = os.environ.get("RESULTS_FOLDER") or config_paths.get("RESULTS_FOLDER")

if base is not None:
    nnUNet_raw_data = join(base, "nnUNet_raw_data")
    nnUNet_cropped_data = join(base, "nnUNet_cropped_data")
    maybe_mkdir_p(nnUNet_raw_data)
    maybe_mkdir_p(nnUNet_cropped_data)
else:
    print("nnUNet_raw_data_base is not defined. Set it in path_config.json or export the env var.")
    nnUNet_cropped_data = nnUNet_raw_data = None

if preprocessing_output_dir is not None:
    maybe_mkdir_p(preprocessing_output_dir)
else:
    print("nnUNet_preprocessed is not defined. Set it in path_config.json or export the env var.")
    preprocessing_output_dir = None

if network_training_output_dir_base is not None:
    network_training_output_dir = join(network_training_output_dir_base, my_output_identifier)
    maybe_mkdir_p(network_training_output_dir)
else:
    print("RESULTS_FOLDER is not defined. Set it in path_config.json or export the env var.")
    network_training_output_dir = None
