<script setup lang="ts">
import { NCard, NGrid, NGi, NTag, NA } from 'naive-ui'
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- 项目介绍 -->
    <NCard class="mb-6">
      <div class="text-center py-4">
        <div class="i-carbon-analytics text-6xl text-blue-500 mx-auto mb-4" />
        <h1 class="text-2xl font-bold mb-2">KidneyTumorAI</h1>
        <p class="text-gray-500 mb-4">
          基于 MindSpore + nnU-Net 的肾脏肿瘤智能分割系统
        </p>
        <div class="flex-center gap-2">
          <NTag type="info">Vue 3</NTag>
          <NTag type="success">TypeScript</NTag>
          <NTag type="warning">MindSpore</NTag>
          <NTag type="error">nnU-Net</NTag>
        </div>
      </div>
    </NCard>

    <!-- 技术架构 -->
    <NGrid :cols="2" :x-gap="16" class="mb-6">
      <NGi>
        <NCard title="前端技术栈">
          <ul class="space-y-2 text-sm">
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              Vue 3 + TypeScript + Vite
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              Naive UI 组件库
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              NiiVue 医学影像可视化
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              Pinia 状态管理
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              UnoCSS 原子化样式
            </li>
          </ul>
        </NCard>
      </NGi>
      <NGi>
        <NCard title="后端技术栈">
          <ul class="space-y-2 text-sm">
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              MindSpore GPU 深度学习框架
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              nnU-Net 医学影像分割架构
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              3D Full Resolution U-Net
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              KiTS19 肾脏肿瘤数据集
            </li>
            <li class="flex items-center gap-2">
              <div class="i-carbon-checkmark text-green-500" />
              CUDA 11.6 + cuDNN 8.4.1
            </li>
          </ul>
        </NCard>
      </NGi>
    </NGrid>

    <!-- 功能特性 -->
    <NCard title="功能特性" class="mb-6">
      <NGrid :cols="3" :x-gap="16" :y-gap="16">
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-cloud-upload text-4xl text-blue-500 mb-3" />
            <h3 class="font-bold mb-1">影像上传</h3>
            <p class="text-gray-500 text-sm">支持 NIfTI 格式 CT 影像</p>
          </div>
        </NGi>
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-machine-learning-model text-4xl text-green-500 mb-3" />
            <h3 class="font-bold mb-1">AI 分割</h3>
            <p class="text-gray-500 text-sm">自动识别肾脏和肿瘤区域</p>
          </div>
        </NGi>
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-cube text-4xl text-purple-500 mb-3" />
            <h3 class="font-bold mb-1">3D 可视化</h3>
            <p class="text-gray-500 text-sm">体渲染和多平面重建</p>
          </div>
        </NGi>
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-analytics text-4xl text-orange-500 mb-3" />
            <h3 class="font-bold mb-1">定量分析</h3>
            <p class="text-gray-500 text-sm">自动计算体积统计</p>
          </div>
        </NGi>
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-time text-4xl text-cyan-500 mb-3" />
            <h3 class="font-bold mb-1">历史记录</h3>
            <p class="text-gray-500 text-sm">管理分析历史</p>
          </div>
        </NGi>
        <NGi>
          <div class="text-center p-4">
            <div class="i-carbon-download text-4xl text-pink-500 mb-3" />
            <h3 class="font-bold mb-1">结果导出</h3>
            <p class="text-gray-500 text-sm">下载分割结果</p>
          </div>
        </NGi>
      </NGrid>
    </NCard>

    <!-- 参考资源 -->
    <NCard title="参考资源">
      <ul class="space-y-2">
        <li>
          <NA href="https://kits19.grand-challenge.org/" target="_blank">
            KiTS19 Challenge - 肾脏肿瘤分割挑战赛
          </NA>
        </li>
        <li>
          <NA href="https://github.com/MIC-DKFZ/nnUNet" target="_blank">
            nnU-Net - 自适应医学影像分割框架
          </NA>
        </li>
        <li>
          <NA href="https://www.mindspore.cn/" target="_blank">
            MindSpore - 华为深度学习框架
          </NA>
        </li>
        <li>
          <NA href="https://github.com/niivue/niivue" target="_blank">
            NiiVue - WebGL 医学影像可视化
          </NA>
        </li>
      </ul>
    </NCard>
  </div>
</template>
