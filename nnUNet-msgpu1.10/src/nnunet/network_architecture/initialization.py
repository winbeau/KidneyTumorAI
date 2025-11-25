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

"""init network weights"""

import mindspore.nn as nn
from mindspore.common.initializer import initializer, HeNormal

class InitWeights_He():
    """init weights using kaiming normal"""
    def __init__(self, neg_slope=1e-2):
        self.neg_slope = neg_slope

    def __call__(self, module):
        if isinstance(module, (nn.Conv3d, nn.Conv2d, nn.Conv2dTranspose, nn.Conv3dTranspose)):
            # MindSpore compatible initialization
            if hasattr(module, 'weight') and module.weight is not None:
                module.weight.set_data(initializer(HeNegative(self.neg_slope), module.weight.shape))
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.set_data(initializer(0, module.bias.shape))

class HeNegative(HeNormal):
    """He initialization with negative slope for LeakyReLU"""
    def __init__(self, negative_slope=0.01):
        super().__init__()
        self.negative_slope = negative_slope

    def _initialize(self, arr):
        # Adjust He normal initialization for negative slope
        import math
        fan_in = arr.shape[1] if len(arr.shape) > 1 else arr.shape[0]
        scale = math.sqrt(2.0 / (1 + self.negative_slope ** 2) / fan_in)
        # Generate normal distribution with the calculated scale
        import numpy as np
        arr[:] = np.random.normal(0, scale, arr.shape)


class InitWeights_XavierUniform():
    """init weights using XavierUniform"""
    def __init__(self, gain=1):
        self.gain = gain

    def __call__(self, module):
        if isinstance(module, (nn.Conv3d, nn.Conv2d, nn.Conv2dTranspose, nn.Conv3dTranspose)):
            # MindSpore compatible Xavier initialization
            from mindspore.common.initializer import initializer, XavierUniform
            if hasattr(module, 'weight') and module.weight is not None:
                module.weight.set_data(initializer(XavierUniform(gain=self.gain), module.weight.shape))
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.set_data(initializer(0, module.bias.shape))
