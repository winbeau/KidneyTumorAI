<script setup lang="ts">
import { NBreadcrumb, NBreadcrumbItem, NButton, NTooltip } from 'naive-ui'
import { useRoute } from 'vue-router'

const route = useRoute()

// 面包屑
const breadcrumbs = computed(() => {
  const items = [{ title: '首页', path: '/' }]

  if (route.path !== '/') {
    const title = route.meta.title as string || route.name as string
    items.push({ title, path: route.path })
  }

  return items
})

// 切换主题 (预留)
const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}
</script>

<template>
  <div class="flex-between w-full">
    <!-- 面包屑 -->
    <NBreadcrumb>
      <NBreadcrumbItem v-for="item in breadcrumbs" :key="item.path">
        <RouterLink :to="item.path">{{ item.title }}</RouterLink>
      </NBreadcrumbItem>
    </NBreadcrumb>

    <!-- 右侧操作区 -->
    <div class="flex items-center gap-2">
      <NTooltip trigger="hover">
        <template #trigger>
          <NButton quaternary circle @click="toggleTheme">
            <template #icon>
              <div :class="isDark ? 'i-carbon-sun' : 'i-carbon-moon'" class="text-lg" />
            </template>
          </NButton>
        </template>
        {{ isDark ? '切换到亮色模式' : '切换到暗色模式' }}
      </NTooltip>

      <NTooltip trigger="hover">
        <template #trigger>
          <NButton quaternary circle tag="a" href="https://github.com" target="_blank">
            <template #icon>
              <div class="i-carbon-logo-github text-lg" />
            </template>
          </NButton>
        </template>
        GitHub
      </NTooltip>
    </div>
  </div>
</template>
