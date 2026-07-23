import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import site from './site.config'
import { applySiteTheme } from './utils/applySiteTheme'
import './styles/main.css'

applySiteTheme(site)

const app = createApp(App)
app.provide('site', site)
app.config.globalProperties.$site = site
app.use(router)
app.mount('#app')
