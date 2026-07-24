import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import site from './site.config'
import { applySiteTheme } from './utils/applySiteTheme'
import { initSentry } from './utils/sentry'
import './styles/main.css'

applySiteTheme(site)

const app = createApp(App)
app.provide('site', site)
app.config.globalProperties.$site = site
app.use(router)
void initSentry(app, router, site.sitio)
app.mount('#app')
