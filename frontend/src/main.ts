import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// UnoCSS
import 'virtual:uno.css'
import '@unocss/reset/tailwind.css'

// 全局样式
import './assets/styles/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
