<script setup>
import { ref } from 'vue'
import { submitLeadData } from '@/api/metgoApi'
import { Leaf } from 'lucide-vue-next'
import CommercialLayout from '@/components/layout/CommercialLayout.vue'

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

<template>
  <CommercialLayout
    brandName="METGO3D"
    brandSub="QUILLOTA"
    :brandIcon="Leaf"
    accentColor="#00ffaa"
    seoTitle="Contacto | METGO3D Quillota"
    seoDescription="Agenda una demo gratuita o solicita acceso piloto para tu operación."
  >

    <main class="commercial-wrap commercial-section">
      <div class="commercial-grid-2">
        <div>
          <h2>Conversemos sobre tu faena</h2>
          <p class="subtitle" style="color: var(--muted); line-height: 1.6;">
            Agenda una demo gratuita o solicita acceso piloto para tu operación. 
            Te responderemos en menos de 24 horas.
          </p>
          
          <div style="margin-top: 3rem;">
            <h3>Soporte directo</h3>
            <p style="color: var(--muted); margin-bottom: 1rem;">
              ¿Necesitas ayuda inmediata o hablar con un especialista?
            </p>
            <p><strong>Email:</strong> <a href="mailto:miguel.lucero@metgo3d.com" style="color: var(--accent);">miguel.lucero@metgo3d.com</a></p>
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

            <button type="submit" class="btn btn-primary" style="width: 100%; height: 48px; font-size: 15px;" :disabled="loading">
              {{ loading ? 'Enviando...' : 'Solicitar Demo' }}
            </button>
            
            <div v-if="success" style="margin-top: 1rem; color: var(--accent); text-align: center;">
              ¡Mensaje enviado! Te contactaremos pronto.
            </div>
            <div v-if="error" style="margin-top: 1rem; color: var(--red); text-align: center;">
              Hubo un error al enviar. Por favor, intenta de nuevo o escríbenos a miguel.lucero@metgo3d.com.
            </div>
          </form>
        </div>
      </div>
    </main>
  </CommercialLayout>
</template>

<style scoped>

.commercial-wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 4rem 28px;
}

h2 {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.5px;
  margin-bottom: 1rem;
}

.commercial-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 4rem;
  margin-top: 2rem;
}

/* Form Styles */
.commercial-form {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--surface-2-color);
  color: var(--text);
  font-family: inherit;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(0, 255, 170, 0.2);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

::placeholder {
  color: var(--muted);
  opacity: 0.7;
}
</style>

