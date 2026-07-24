import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n, { setLocale } from './i18n'
import { setUnauthorizedHandler, setForbiddenHandler } from './api/metgoApi'
import { initSentry } from './utils/sentry'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)

setLocale(i18n.global.locale.value)

void initSentry(app, router, 'quillota')

setUnauthorizedHandler(() => {
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
})

setForbiddenHandler(() => {
  if (router.currentRoute.value.name !== 'forbidden') {
    router.push({ name: 'forbidden' })
  }
})

app.mount('#app')
