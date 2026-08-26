<template>
  <div class="anchorage-map">
    <div class="panel-header">
      <Map class="panel-icon" :size="16" />
      <span class="panel-title">Fondeo de Naves ({{ port?.name || 'Iquique' }})</span>
      <span class="panel-coords">{{ formattedCoords }}</span>
    </div>

    <div class="map-viewport">
      <svg viewBox="0 0 320 220" class="map-svg" xmlns="http://www.w3.org/2000/svg">
        <!-- Sea background -->
        <rect x="0" y="0" width="320" height="220" fill="rgba(5,20,50,0.6)" rx="8"/>

        <!-- Depth contours (stylized) -->
        <ellipse cx="160" cy="110" rx="130" ry="90" fill="none" stroke="rgba(40,100,200,0.12)" stroke-width="1"/>
        <ellipse cx="160" cy="110" rx="100" ry="68" fill="none" stroke="rgba(40,100,200,0.10)" stroke-width="1"/>
        <ellipse cx="160" cy="110" rx="70"  ry="46" fill="none" stroke="rgba(40,100,200,0.08)" stroke-width="1"/>

        <!-- Mole / Quay (solid land-pier) -->
        <rect x="10" y="80" width="14" height="90" fill="rgba(150,140,120,0.55)" rx="2"/>
        <rect x="10" y="158" width="90" height="14" fill="rgba(150,140,120,0.55)" rx="2"/>
        <!-- Pier extensions -->
        <rect x="24" y="100" width="40" height="8"  fill="rgba(150,140,120,0.4)" rx="2"/>
        <rect x="24" y="140" width="40" height="8"  fill="rgba(150,140,120,0.4)" rx="2"/>

        <!-- Coastline hint -->
        <path d="M 0 0 L 10 0 L 10 220 L 0 220 Z" fill="rgba(160,140,100,0.30)"/>

        <!-- Anchorage zones -->
        <ellipse
          v-for="zone in anchorageZones"
          :key="zone.id"
          :cx="zone.cx" :cy="zone.cy" :rx="zone.rx" :ry="zone.ry"
          :fill="zone.fill"
          :stroke="zone.stroke"
          stroke-width="1"
          stroke-dasharray="4 3"
        />
        <text v-for="zone in anchorageZones" :key="'lbl-'+zone.id"
          :x="zone.cx" :y="zone.cy + 4"
          text-anchor="middle"
          class="zone-label"
        >{{ zone.label }}</text>

        <!-- Vessels -->
        <g v-for="vessel in vessels" :key="vessel.id"
          :transform="`translate(${vessel.x},${vessel.y}) rotate(${vessel.heading})`"
          class="vessel-group"
        >
          <!-- Ship hull shape -->
          <polygon
            :points="vesselPoints(vessel.length, vessel.beam)"
            :fill="vessel.fill"
            :stroke="vessel.stroke"
            stroke-width="1.2"
            opacity="0.92"
          />
          <!-- Crane indicator dot -->
          <circle v-if="vessel.hasCrane" cx="0" cy="-4" r="2.5" fill="#f59e0b" opacity="0.9"/>
        </g>

        <!-- Vessel labels -->
        <text v-for="vessel in vessels" :key="'vlbl-'+vessel.id"
          :x="vessel.x + 14" :y="vessel.y - 6"
          class="vessel-label"
        >{{ vessel.name }}</text>

        <!-- Wind arrow indicator -->
        <g transform="translate(288, 28)">
          <circle cx="0" cy="0" r="16" fill="rgba(10,20,50,0.7)" stroke="rgba(100,160,255,0.25)" stroke-width="1"/>
          <text x="0" y="4" text-anchor="middle" font-size="7" fill="rgba(120,180,255,0.5)">N</text>
          <line x1="0" y1="-10" x2="0" y2="-3"
            stroke="#7ab0e8" stroke-width="1.5" stroke-linecap="round"
            :transform="`rotate(${windDir})`"
          />
        </g>
        <text x="288" y="52" text-anchor="middle" class="wind-badge">{{ windSpeed }}kt</text>

        <!-- Scale bar -->
        <line x1="220" y1="205" x2="300" y2="205" stroke="rgba(120,160,220,0.4)" stroke-width="1.5"/>
        <text x="260" y="214" text-anchor="middle" class="scale-label">500m</text>
      </svg>

      <!-- Legend -->
      <div class="legend">
        <div class="legend-item" v-for="item in legend" :key="item.label">
          <span class="legend-dot" :style="{ background: item.color }"/>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Map } from 'lucide-vue-next'

import { computed } from 'vue'

const props = defineProps({
  port: { type: Object, default: null },
  windDir:   { type: Number, default: 215 },
  windSpeed: { type: Number, default: 14 },
})

const defaultVessels = [
  { id: 1, name: 'ANDES STAR',   x: 120, y: 90,  heading: -20, length: 36, beam: 10, fill: 'rgba(40,120,220,0.7)', stroke: '#4fc3f7', hasCrane: true },
  { id: 2, name: 'ATACAMA CL',   x: 190, y: 135, heading: 10,  length: 28, beam: 8,  fill: 'rgba(40,100,180,0.6)', stroke: '#60a5fa', hasCrane: false },
  { id: 3, name: 'MAIPO BULK',   x: 155, y: 60,  heading: 5,   length: 22, beam: 7,  fill: 'rgba(80,80,160,0.6)', stroke: '#a78bfa', hasCrane: false },
]

const vessels = computed(() => {
  // Simular barcos según la profundidad y boyas del puerto
  // En producción esto vendría del AIS
  return defaultVessels
})

const formattedCoords = computed(() => {
  if (!props.port || !props.port.coordinates) return "20°12′S 70°09′O"
  const [lat, lon] = props.port.coordinates
  
  const formatCoord = (coord, isLat) => {
    const absolute = Math.abs(coord)
    const deg = Math.floor(absolute)
    const min = Math.round((absolute - deg) * 60)
    let dir = ''
    if (isLat) dir = coord > 0 ? 'N' : 'S'
    else dir = coord > 0 ? 'E' : 'O'
    return `${deg}°${min}′${dir}`
  }
  
  return `${formatCoord(lat, true)} ${formatCoord(lon, false)}`
})

const anchorageZones = [
  { id: 'A', cx: 200, cy: 100, rx: 35, ry: 22, label: 'Z-A', fill: 'rgba(79,195,247,0.05)', stroke: 'rgba(79,195,247,0.35)' },
  { id: 'B', cx: 260, cy: 140, rx: 28, ry: 18, label: 'Z-B', fill: 'rgba(245,158,11,0.05)', stroke: 'rgba(245,158,11,0.30)' },
]

const legend = [
  { label: 'Activo STS',  color: '#4fc3f7' },
  { label: 'En espera',   color: '#60a5fa' },
  { label: 'Fondeo',      color: '#a78bfa' },
  { label: 'Grúa activa', color: '#f59e0b' },
]

function vesselPoints(len, beam) {
  const l = len / 2, b = beam / 2
  return `0,${-l} ${b},${-l*0.4} ${b},${l*0.6} 0,${l} ${-b},${l*0.6} ${-b},${-l*0.4}`
}
</script>

<style scoped>
.anchorage-map {
  background: rgba(10, 20, 40, 0.72);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(100, 160, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  color: #e2eaf6;
  font-family: 'JetBrains Mono', 'Fira Mono', monospace;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7ab0e8;
  border-bottom: 1px solid rgba(100, 160, 255, 0.1);
  padding-bottom: 8px;
}
.panel-coords { margin-left: auto; font-size: 0.65rem; color: rgba(120,160,220,0.45); }

.map-viewport { position: relative; }

.map-svg { width: 100%; border-radius: 8px; }

.zone-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 7px;
  fill: rgba(180,210,255,0.4);
  letter-spacing: 0.06em;
}

.vessel-group { cursor: default; transition: opacity 0.2s; }
.vessel-group:hover { opacity: 0.7; }

.vessel-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 7.5px;
  fill: rgba(200,220,255,0.7);
}

.wind-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 7px;
  fill: rgba(120,180,255,0.6);
}

.scale-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 7px;
  fill: rgba(120,160,220,0.4);
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  font-size: 0.65rem;
  color: rgba(160,200,240,0.6);
  padding-top: 6px;
}
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
</style>
