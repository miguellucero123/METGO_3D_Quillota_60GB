import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler, setForbiddenHandler } from './api/metgoApi'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

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
