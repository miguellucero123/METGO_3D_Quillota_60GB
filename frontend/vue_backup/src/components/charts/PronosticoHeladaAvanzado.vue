<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoHeladaAvanzado } from '@/api/metgoApi'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
])

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])
const resumen = ref(null)
const umbrales = ref(null)
const criteriosBoletin = ref(null)
const expandidoIdx = ref(-1)
const cultivo = ref('palto')
const humedadSuelo = ref(null)
const sueloDescubierto = ref(false)

async function cargar() {
  cargando.value = true
  try {
    const extras = {}
    if (humedadSuelo.value != null && humedadSuelo.value !== '') {
      extras.humedad_suelo = Number(humedadSuelo.value)
    }
    if (sueloDescubierto.value) extras.suelo_descubierto = true
    const res = await fetchPronosticoHeladaAvanzado(
      store.estacionActiva,
      7,
      cultivo.value,
      extras,
    )
    datos.value = res.pronosticos_helada ?? []
    resumen.value = res.resumen ?? null
    umbrales.value = res.umbrales_cultivo ?? null
    criteriosBoletin.value = res.criterios_boletin ?? null
  } catch {
    datos.value = []
    resumen.value = null
    umbrales.value = null
  } finally {
    cargando.value = false
  }
}

watch(
  [() => store.estacionActiva, cultivo, humedadSuelo, sueloDescubierto],
  cargar,
  { immediate: true },
)

function fmt(fechaStr) {
  return new Date(fechaStr).toLocaleDateString('es-CL', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

function tempClass(t) {
  if (t == null || Number.isNaN(t)) return 'ok'
  const crit = umbrales.value?.critico ?? 0
  if (t <= crit - 2) return 'ext'
  if (t <= crit) return 'crit'
  if (t <= (umbrales.value?.alto ?? 2)) return 'riesgo'
  return 'ok'
}

function thClass(t) {
  if (t == null || Number.isNaN(t)) return 'ok'
  if (t <= 0) return 'crit'
  if (t <= 2) return 'riesgo'
  return 'ok'
}

function popColor(p) {
  if (p >= 90) return CHART_COLORS.rojo
  if (p > 66) return '#f97316'
  if (p > 20) return CHART_COLORS.ambar
  return '#22c55e'
}

function boletinLabel(d) {
  const b = d.probabilidad_boletin
  if (b === 'alta') return 'Alta (≥90%)'
  if (b === 'media') return 'Media'
  if (b === 'baja') return 'Baja'
  return d.nivel_riesgo || '—'
}

const umbralMark = computed(() => umbrales.value?.critico ?? 0)

const chartOption = computed(() => {
  const labels = datos.value.map((d) => fmt(d.fecha_pronostico || d.fecha))
  const pops = datos.value.map((d) => d.probabilidad_helada)
  const tmins = datos.value.map((d) => d.temperatura_minima_esperada)
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        const u = p.seriesName.includes('Prob') ? '%' : ' °C'
        html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${p.value ?? '—'}${u}</b></div>`
      })
      return html
    }),
    legend: leyendaSuperior(['Prob. helada', 'T. mínima']),
    grid: grillaBase(),
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Prob (%)', CHART_COLORS.rojo, {
        max: 100,
        position: 'left',
        axisLabel: { formatter: '{value}%', color: CHART_COLORS.texto },
      }),
      ejeValor('Temp (°C)', CHART_COLORS.verde, {
        position: 'right',
        splitLine: { show: false },
        axisLabel: { formatter: '{value} °C', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      {
        name: 'Prob. helada',
        type: 'bar',
        yAxisIndex: 0,
        data: pops.map((v) => ({
          value: v,
          itemStyle: { color: popColor(v), borderRadius: [4, 4, 0, 0] },
        })),
        barMaxWidth: 28,
        markLine: {
          silent: true,
          data: [
            { yAxis: 66, name: 'Media' },
            { yAxis: 90, name: 'Alta' },
          ],
          lineStyle: { type: 'dashed', color: '#94a3b8' },
          label: { color: CHART_COLORS.texto, fontSize: 10 },
        },
      },
      serieLineaVerde('T. mínima', tmins, {
        yAxisIndex: 1,
        markLine: {
          silent: true,
          data: [
            { yAxis: 0, name: 'Meteo' },
            { yAxis: umbralMark.value, name: 'Cultivo' },
          ],
          lineStyle: { color: CHART_COLORS.rojo, type: 'dashed' },
          label: { formatter: '{b}', color: CHART_COLORS.texto },
        },
      }),
    ],
  }
})
</script>

<template>
  <div class="helada-av">
    <header class="helada-av__head">
      <div>
        <h3>Pronóstico de helada radiativa</h3>
        <p class="sub">
          Umbrales por cultivo · boletín ≤66% / 66–90% / ≥90% · psicrómetro Td/Th ·
          oquedad y humedad de suelo
        </p>
      </div>
      <div class="controles">
        <select v-model="cultivo" class="cultivo-sel">
          <option value="palto">Palto</option>
          <option value="vid">Vid</option>
          <option value="citricos">Cítricos</option>
          <option value="tomate">Tomate</option>
          <option value="lechuga">Lechuga</option>
        </select>
        <label class="hs-lab">
          Hum. suelo %
          <input
            v-model.number="humedadSuelo"
            type="number"
            min="0"
            max="100"
            step="1"
            placeholder="auto"
            class="hs-input"
          />
        </label>
        <label class="chk">
          <input v-model="sueloDescubierto" type="checkbox" />
          Suelo descubierto
        </label>
      </div>
    </header>

    <div v-if="umbrales" class="umbrales">
      <span>Crítico ≤ {{ umbrales.critico }}°C</span>
      <span>Alto ≤ {{ umbrales.alto }}°C</span>
      <span>Moderado ≤ {{ umbrales.moderado }}°C</span>
      <span>Meteo ≤ 0°C</span>
    </div>

    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <div v-if="resumen" class="resumen">
        <div class="card sev">
          <strong>{{ resumen.dias_prob_alta ?? resumen.dias_riesgo_severo }}</strong>
          <span>Prob. alta</span>
        </div>
        <div class="card mod">
          <strong>{{ resumen.dias_alerta_cultivo ?? resumen.dias_riesgo_moderado }}</strong>
          <span>Alerta cultivo</span>
        </div>
        <div class="card min">
          <strong>{{ resumen.temperatura_minima_7d }}°C</strong>
          <span>T° mín 7d</span>
        </div>
      </div>

      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>

      <table class="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>T° mín</th>
            <th>Td</th>
            <th>Th</th>
            <th>PoP</th>
            <th>Boletín</th>
            <th>Tipo</th>
            <th>Riesgo</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(d, i) in datos" :key="i">
            <tr
              :class="{ alto: d.riesgo_severo || d.riesgo_inminente || d.alerta_cultivo }"
              @click="expandidoIdx = expandidoIdx === i ? -1 : i"
            >
              <td>{{ fmt(d.fecha_pronostico || d.fecha) }}</td>
              <td>
                <span class="badge" :class="tempClass(d.temperatura_minima_esperada)">
                  {{ d.temperatura_minima_esperada }}°C
                </span>
              </td>
              <td>
                <span class="badge" :class="tempClass(d.punto_rocio_atardecer ?? d.punto_rocio)">
                  {{ d.punto_rocio_atardecer ?? d.punto_rocio ?? '—'
                  }}{{ (d.punto_rocio_atardecer ?? d.punto_rocio) != null ? '°C' : '' }}
                </span>
              </td>
              <td>
                <span class="badge" :class="thClass(d.bulbo_humedo_atardecer ?? d.bulbo_humedo)">
                  {{ d.bulbo_humedo_atardecer ?? d.bulbo_humedo ?? '—'
                  }}{{ (d.bulbo_humedo_atardecer ?? d.bulbo_humedo) != null ? '°C' : '' }}
                </span>
              </td>
              <td>{{ d.probabilidad_helada }}%</td>
              <td>{{ boletinLabel(d) }}</td>
              <td>{{ d.tipo_helada || d.dano_cultivo?.tipo_helada || '—' }}</td>
              <td>{{ d.nivel_riesgo || '—' }}</td>
            </tr>
            <tr v-if="expandidoIdx === i" class="detalle-row">
              <td colspan="8">
                <p>
                  {{
                    d.recomendacion ||
                    d.criterio_psicrometro?.mensaje ||
                    d.descripcion ||
                    'Sin detalle adicional'
                  }}
                </p>
                <p v-if="d.factor_oquedad?.mensaje" class="extra">
                  {{ d.factor_oquedad.mensaje }}
                </p>
                <p v-if="d.factor_humedad_suelo?.mensaje" class="extra">
                  {{ d.factor_humedad_suelo.mensaje }}
                </p>
                <ul v-if="d.factores_contribuyentes?.length" class="factores">
                  <li v-for="(f, fi) in d.factores_contribuyentes" :key="fi">{{ f }}</li>
                </ul>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>
    <p v-else class="empty">Sin pronóstico de helada</p>
  </div>
</template>

<style scoped>
.helada-av {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1rem;
}
.helada-av__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}
.helada-av__head h3 { margin: 0; font-size: 1rem; }
.sub { margin: 0.25rem 0 0; font-size: 0.72rem; color: #94a3b8; max-width: 32rem; }
.controles { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
.cultivo-sel,
.hs-input {
  font-size: 0.8rem;
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}
.hs-lab { font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 0.3rem; }
.hs-input { width: 4.2rem; }
.chk { font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 0.25rem; }
.umbrales {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.85rem;
  font-size: 0.72rem;
  color: #94a3b8;
  margin-bottom: 0.65rem;
}
.resumen { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 0.75rem; }
.card {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  padding: 0.5rem;
  text-align: center;
  border-left: 3px solid #0284c7;
}
.card strong { display: block; font-size: 1.1rem; color: #38bdf8; }
.card span { font-size: 0.72rem; color: #94a3b8; }
.card.sev { border-color: #ef4444; }
.card.mod { border-color: #f59e0b; }
.chart-wrap { width: 100%; height: 300px; margin-bottom: 0.75rem; }
.chart { width: 100%; height: 100%; }
.tabla { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.tabla th,
.tabla td {
  padding: 0.4rem 0.35rem;
  border-bottom: 1px solid var(--color-border, #334155);
  text-align: left;
}
.tabla th { color: #94a3b8; font-weight: 500; }
.tabla tr { cursor: pointer; }
.tabla tr.alto { background: rgba(239, 68, 68, 0.08); }
.detalle-row td { font-size: 0.75rem; color: #94a3b8; }
.detalle-row p { margin: 0 0 0.35rem; }
.extra { opacity: 0.9; }
.factores { margin: 0; padding-left: 1.1rem; }
.badge { padding: 0.1rem 0.35rem; border-radius: 4px; font-weight: 600; }
.badge.ok { color: #22c55e; }
.badge.riesgo { color: #fbbf24; }
.badge.crit { color: #f87171; }
.badge.ext { color: #ef4444; }
.loading,
.empty { text-align: center; padding: 1.5rem; color: #94a3b8; }
</style>
