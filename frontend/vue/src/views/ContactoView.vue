<template>
  <div class="commercial-page">
    <header class="top">
      <nav class="nav" aria-label="Principal">
        <router-link to="/" class="brand">
          <span class="brand-text">
            <span class="brand-name">METGO</span>
            <span class="brand-sub">3D</span>
          </span>
        </router-link>
        <div class="nav-links">
          <router-link to="/planes">Planes</router-link>
          <router-link to="/izaje">Izaje</router-link>
          <router-link to="/mineria">Minería</router-link>
          <router-link to="/calidad-del-aire">Calidad del Aire</router-link>
        </div>
        <div class="nav-cta">
          <router-link class="btn btn-ghost" to="/login">Ingresar</router-link>
        </div>
      </nav>
    </header>

    <main class="commercial-wrap commercial-section">
      <div class="commercial-grid-2">
        <div>
          <h2>Conversemos sobre tu faena</h2>
          <p class="subtitle">
            Agenda una demo gratuita o solicita acceso piloto para tu operación. 
            Te responderemos en menos de 24 horas.
          </p>
          
          <div style="margin-top: 3rem;">
            <h3>Soporte directo</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
              ¿Necesitas ayuda inmediata o hablar con un especialista?
            </p>
            <p><strong>Email:</strong> <a href="mailto:miguel.lucero@metgo3d.com">miguel.lucero@metgo3d.com</a></p>
            <p><strong>Ubicación:</strong> Quillota, Región de Valparaíso, Chile</p>
          </div>
        </div>

        <div>
          <form class="commercial-form" @submit.prevent="submitLead">
            <div class="form-group">
              <label for="nombre">Nombre completo</label>
              <input type="text" id="nombre" v-model="form.nombre" required placeholder="Ej: Juan Pérez">
            </div>
            
            <div class="form-group">
              <label for="empresa">Empresa</label>
              <input type="text" id="empresa" v-model="form.empresa" required placeholder="Tu empresa o faena">
            </div>

            <div class="form-group">
              <label for="sector">Sector</label>
              <select id="sector" v-model="form.sector" required>
                <option value="" disabled>Selecciona tu sector...</option>
                <option value="agricultura">Agricultura</option>
                <option value="mineria">Minería y Alta Montaña</option>
                <option value="izaje">Izaje y Construcción</option>
                <option value="calidad-aire">Calidad del Aire / Municipio</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div class="form-group">
              <label for="email">Correo corporativo</label>
              <input type="email" id="email" v-model="form.email" required placeholder="correo@empresa.cl">
            </div>

            <div class="form-group">
              <label for="telefono">Teléfono / WhatsApp</label>
              <input type="tel" id="telefono" v-model="form.telefono" placeholder="+56 9 1234 5678">
            </div>

            <div class="form-group">
              <label for="mensaje">Mensaje (opcional)</label>
              <textarea id="mensaje" v-model="form.mensaje" placeholder="¿En qué te podemos ayudar?"></textarea>
            </div>

            <button type="submit" class="commercial-btn primary" style="width: 100%;" :disabled="loading">
              {{ loading ? 'Enviando...' : 'Solicitar Demo' }}
            </button>
            
            <div v-if="success" style="margin-top: 1rem; color: var(--accent-secondary); text-align: center;">
              ¡Mensaje enviado! Te contactaremos pronto.
            </div>
            <div v-if="error" style="margin-top: 1rem; color: #ef5b5b; text-align: center;">
              Hubo un error al enviar. Por favor, intenta de nuevo o escríbenos a miguel.lucero@metgo3d.com.
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitLeadData } from '@/api/metgoApi'

const form = ref({
  nombre: '',
  empresa: '',
  sector: '',
  email: '',
  telefono: '',
  mensaje: ''
})

const loading = ref(false)
const success = ref(false)
const error = ref(false)

const submitLead = async () => {
  loading.value = true
  success.value = false
  error.value = false
  
  try {
    await submitLeadData(form.value)
    success.value = true
    form.value = { nombre: '', empresa: '', sector: '', email: '', telefono: '', mensaje: '' }
  } catch (err) {
    error.value = true
    console.error('Error al enviar lead:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: rgba(8, 12, 20, 0.82);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
}
.nav {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 28px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-links {
  display: none;
  gap: 1.5rem;
}
@media (min-width: 768px) {
  .nav-links {
    display: flex;
  }
}
.nav-links a {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
  text-decoration: none;
}
.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--text-primary);
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  text-decoration: none;
}
.brand-name {
  font-weight: 700;
  letter-spacing: 0.05em;
}
.brand-sub {
  color: var(--accent-primary);
  font-weight: 700;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-weight: 600;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-ghost {
  color: var(--text-primary);
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
