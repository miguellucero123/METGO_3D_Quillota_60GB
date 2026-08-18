import { onMounted, onUnmounted, watchEffect } from 'vue'

export function useSeo({ title, description, keywords }) {
  const updateMeta = (name, content) => {
    if (!content) return
    let el = document.querySelector(`meta[name="${name}"]`)
    if (!el) {
      el = document.createElement('meta')
      el.setAttribute('name', name)
      document.head.appendChild(el)
    }
    el.setAttribute('content', content)
  }

  const applySeo = () => {
    if (title) document.title = title
    if (description) updateMeta('description', description)
    if (keywords) updateMeta('keywords', keywords)
  }

  onMounted(() => {
    applySeo()
  })

  // Watchers to update if reactive refs are passed
  watchEffect(() => {
    applySeo()
  })
}
