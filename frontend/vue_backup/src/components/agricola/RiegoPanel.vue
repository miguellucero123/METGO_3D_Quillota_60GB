<script setup>
const recomendaciones = [
  { cultivo: 'Palta', accion: 'Riego moderado', motivo: 'Humedad del suelo estable' },
  { cultivo: 'Cítricos', accion: 'Monitorear heladas', motivo: 'Temperatura mínima prevista 4°C' },
  { cultivo: 'Vid', accion: 'Sin riego', motivo: 'Precipitación esperada 8 mm' },
]
</script>

<template>
  <div class="card">
    <h3>Recomendaciones agrícolas (demo)</h3>
    <table class="tabla">
      <thead>
        <tr>
          <th>Cultivo</th>
          <th>Acción</th>
          <th>Motivo</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in recomendaciones" :key="r.cultivo">
          <td>{{ r.cultivo }}</td>
          <td>{{ r.accion }}</td>
          <td>{{ r.motivo }}</td>
        </tr>
      </tbody>
    </table>
    <p class="hint">Conectar con <code>02_Sistema_Agricola/scripts/</code> vía API.</p>
  </div>
</template>

<style scoped>
.tabla {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.75rem;
}
.tabla th,
.tabla td {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}
.hint {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--metgo-muted);
}
</style>
