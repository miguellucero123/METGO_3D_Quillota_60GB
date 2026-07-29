<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { HardHat } from 'lucide-vue-next'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { fetchMisFaenas, fetchMe, getToken, wakeApi } from '@/services/authApi'
import { useAuth } from '@/stores/auth'

const site = inject('site')
const router = useRouter()
const auth = useAuth()

const loading = ref(true)
const hub = ref(null)
const error = ref('')
const slugManual = ref('')

const catalog = computed(() => site.stations || [])

const visible = computed(() => {
  if (!hub.value) return []
  if (hub.value.catalogo_completo) return catalog.value
  const slugs = new Set((hub.value.faenas || []).map((f) => f.slug))
  return catalog.value.filter((s) => slugs.has(s.slug))
})

const isLoggedIn = computed(() => Boolean(getToken()))

onMounted(async () => {
  wakeApi().catch(() => {})
  if (!getToken()) {
    loading.value = false
    return
  }
  try {
    await auth.ensureValidSession()
    try {
      hub.value = await fetchMisFaenas()
    } catch {
      const me = await fetchMe()
      hub.value = me.hub || {
        catalogo_completo: ['admin', 'administrador'].includes(String(me.role || '').toLowerCase()),
        faenas: me.faena ? [{ slug: me.faena }] : me.faenas || [],
      }
    }
    // Una sola faena → entrar directo (no mostrar catálogo)
    if (!hub.value.catalogo_completo && (hub.value.faenas || []).length === 1) {
      const only = hub.value.faenas[0].slug
      await router.replace(`/f/${only}/`)
      return
    }
  } catch (e) {
    error.value = e.message || 'No se pudo cargar acceso'
  } finally {
    loading.value = false
  }
})

function irA(slug) {
  const s = String(slug || '').trim().toLowerCase().replace(/\s+/g, '_')
  if (!s) return
  router.push(`/f/${s}/login`)
}
</script>

<template>
  <div class="hub">
    <header>
      <ThemeToggle />
      <div class="brand">
        <HardHat :size="28" aria-hidden="true" />
        <div>
          <h1>{{ site.productName }} SPATI</h1>
          <p>
            Cada minera tiene su enlace, reglas y suscripción.
            Solo verá las faenas de su contrato.
          </p>
        </div>
      </div>
    </header>

    <!-- Público: sin listar el catálogo comercial -->
    <section v-if="!isLoggedIn" class="gate">
      <p>
        Si su operador le envió un enlace (p. ej.
        <code>/f/quebrada_blanca/login</code>), úselo.
        También puede indicar el código de faena:
      </p>
      <form class="gate-form" @submit.prevent="irA(slugManual)">
        <label>
          <span>Código de faena</span>
          <input
            v-model="slugManual"
            type="text"
            placeholder="quebrada_blanca"
            autocomplete="off"
            required
          />
        </label>
        <button type="submit" class="btn">Ir a ingreso</button>
      </form>
      <p class="hint">
        El listado completo de mineras no se muestra aquí por confidencialidad comercial.
        Plan Enterprise (multi-faena) o admin: tras iniciar sesión verá todas las habilitadas.
      </p>
    </section>

    <p v-else-if="loading">Cargando sus faenas…</p>
    <p v-else-if="error" class="err" role="alert">{{ error }}</p>

    <ul v-else-if="visible.length" class="list">
      <li v-for="f in visible" :key="f.slug">
        <router-link :to="`/f/${f.slug}/`">
          <strong>{{ f.nombre }}</strong>
          <span>{{ f.region }} · {{ f.altitud_msnm }} m</span>
          <em>/f/{{ f.slug }}/</em>
        </router-link>
        <div class="actions">
          <router-link :to="`/f/${f.slug}/`">Abrir</router-link>
        </div>
      </li>
    </ul>
    <p v-else-if="isLoggedIn" class="hint">
      No hay faenas asociadas a esta cuenta. Contacte a su administrador o
      regístrese en el enlace de su minera.
    </p>
  </div>
</template>

<style scoped>
.hub {
  min-height: 100vh;
  padding: 1.5rem;
  background: var(--color-bg);
  color: var(--color-text);
}
header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.brand {
  display: flex;
  gap: 0.85rem;
  align-items: center;
}
.brand h1 { margin: 0; font-size: 1.35rem; }
.brand p { margin: 0.25rem 0 0; color: var(--color-muted); font-size: 0.9rem; max-width: 36rem; }
.gate {
  max-width: 420px;
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: rgba(17, 24, 39, 0.55);
}
.gate-form {
  display: grid;
  gap: 0.75rem;
  margin-top: 1rem;
}
.gate-form label span {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-muted);
  margin-bottom: 0.25rem;
}
.gate-form input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: #0b1120;
  color: var(--color-text);
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.55rem 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-primary);
  color: #0b1120;
}
.hint { color: var(--color-muted); font-size: 0.85rem; margin-top: 1rem; max-width: 36rem; }
.err { color: var(--color-danger); }
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
  max-width: 820px;
}
.list li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.85rem 1rem;
  background: rgba(17, 24, 39, 0.55);
}
.list a { color: inherit; text-decoration: none; }
.list strong { display: block; }
.list span, .list em {
  display: block;
  font-size: 0.8rem;
  color: var(--color-muted);
  font-style: normal;
}
.actions {
  display: flex;
  gap: 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
}
.actions a { color: var(--color-primary); }
@media (max-width: 640px) {
  .list li { flex-direction: column; align-items: flex-start; }
}
</style>
