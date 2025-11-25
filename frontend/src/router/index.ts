import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/HomePage.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/viewer',
    name: 'Viewer',
    component: () => import('@/pages/ViewerPage.vue'),
    meta: { title: '影像查看' },
  },
  {
    path: '/viewer/:taskId',
    name: 'ViewerWithTask',
    component: () => import('@/pages/ViewerPage.vue'),
    meta: { title: '查看结果' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/pages/HistoryPage.vue'),
    meta: { title: '历史记录' },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/pages/AboutPage.vue'),
    meta: { title: '关于' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'KidneyTumorAI'} - 肾脏肿瘤AI分割系统`
  next()
})

export default router
