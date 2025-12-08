<script setup lang="ts">
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NMenu } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'
import { computed, h, ref } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'

const route = useRoute()
const router = useRouter()

// 菜单项
const menuOptions = [
  {
    label: '首页',
    key: '/',
    icon: () => h('div', { class: 'i-carbon-home text-lg' }),
  },
  {
    label: '影像查看',
    key: '/viewer',
    icon: () => h('div', { class: 'i-carbon-image-medical text-lg' }),
  },
  {
    label: '历史记录',
    key: '/history',
    icon: () => h('div', { class: 'i-carbon-time text-lg' }),
  },
  {
    label: '关于',
    key: '/about',
    icon: () => h('div', { class: 'i-carbon-information text-lg' }),
  },
]

const activeKey = computed(() => {
  if (route.path.startsWith('/viewer')) return '/viewer'
  return route.path
})

const handleMenuSelect = (key: string) => {
  router.push(key)
}

// 侧边栏折叠状态
const collapsed = ref(false)
</script>

<template>
  <NLayout has-sider class="h-full">
    <!-- 侧边栏 -->
    <NLayoutSider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      class="bg-white dark:bg-gray-900"
    >
      <!-- Logo -->
      <div class="h-14 flex-center border-b border-gray-200 dark:border-gray-700">
        <div v-if="!collapsed" class="flex items-center gap-2">
          <div class="i-carbon-analytics text-2xl text-blue-500" />
          <span class="font-bold text-lg">KidneyTumorAI</span>
        </div>
        <div v-else class="i-carbon-analytics text-2xl text-blue-500" />
      </div>

      <!-- 导航菜单 -->
      <NMenu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="20"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />
    </NLayoutSider>

    <!-- 主内容区 -->
    <NLayout>
      <NLayoutHeader bordered class="h-14 px-4 flex-between bg-white dark:bg-gray-900">
        <AppHeader />
      </NLayoutHeader>

      <NLayoutContent class="p-4 bg-gray-50 dark:bg-gray-800" content-style="min-height: calc(100vh - 56px);">
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </NLayoutContent>
    </NLayout>
  </NLayout>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
