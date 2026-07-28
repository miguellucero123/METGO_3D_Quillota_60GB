import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import site from './site.config'
import { applySiteTheme } from './utils/applySiteTheme'
import { initSentry } from './utils/sentry'
import i18n, { setLocale } from './i18n'
import './styles/main.css'

applySiteTheme(site)

const app = createApp(App)
app.provide('site', site)
app.config.globalProperties.$site = site
app.use(router)
app.use(i18n)
setLocale(i18n.global.locale.value)
void initSentry(app, router, site.sitio)
app.mount('#app')
