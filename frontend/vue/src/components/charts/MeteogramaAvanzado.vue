<template>
  <div class="meteograma-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart, CustomChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkAreaComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

// Registrar módulos ECharts
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  CustomChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkAreaComponent
]);

const props = defineProps({
  ensembleData: {
    type: Array,
    required: true,
    default: () => []
  }
});

const chartOption = ref({});

const initChart = () => {
  if (!props.ensembleData || props.ensembleData.length === 0) return;

  const dates = props.ensembleData.map(d => d.fecha);
  const tempMins = props.ensembleData.map(d => d.temperatura.min_mediana);
  const precips = props.ensembleData.map(d => d.precipitacion.mediana);
  const precipProb = props.ensembleData.map(d => d.precipitacion.probabilidad);

  chartOption.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', animation: false },
      backgroundColor: 'rgba(17, 24, 39, 0.9)',
      borderColor: 'rgba(0, 255, 170, 0.3)',
      textStyle: { color: '#f3f4f6' },
      formatter: function (params) {
        let html = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${params[0].axisValue}</div>`;
        params.forEach(p => {
          let unit = p.seriesName.includes('Temp') ? '°C' : (p.seriesName.includes('Precipitación') ? 'mm' : '%');
          html += `<div style="display:flex;justify-content:space-between;margin-top:2px;">
                     <span style="color:${p.color};margin-right:15px;">● ${p.seriesName}</span>
                     <b>${p.value} ${unit}</b>
                   </div>`;
        });
        return html;
      }
    },
    legend: {
      data: ['T. Mínima (Ensemble)', 'Precipitación', 'Probabilidad Lluvia'],
      textStyle: { color: '#9ca3af' },
      top: 0
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'filter'
      },
      {
        type: 'slider',
        xAxisIndex: 0,
        height: 25,
        bottom: 5,
        borderColor: 'rgba(0, 255, 170, 0.2)',
        textStyle: { color: '#9ca3af' }
      }
    ],
    grid: {
      top: '15%',
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9ca3af' }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: 'Temperatura (°C)',
        position: 'left',
        axisLine: { show: true, lineStyle: { color: '#00ffaa' } },
        splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
        axisLabel: { formatter: '{value} °C' }
      },
      {
        type: 'value',
        name: 'Lluvia (mm)',
        position: 'right',
        axisLine: { show: true, lineStyle: { color: '#0ea5e9' } },
        splitLine: { show: false },
        axisLabel: { formatter: '{value} mm' }
      },
      {
        type: 'value',
        name: 'Prob (%)',
        position: 'right',
        offset: 50,
        max: 100,
        axisLine: { show: true, lineStyle: { color: '#f59e0b' } },
        splitLine: { show: false },
        axisLabel: { show: false }
      }
    ],
    series: [
      {
        name: 'T. Mínima (Ensemble)',
        type: 'line',
        yAxisIndex: 0,
        data: tempMins,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#00ffaa' },
        lineStyle: { width: 3, shadowColor: 'rgba(0, 255, 170, 0.5)', shadowBlur: 10 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 255, 170, 0.3)' },
              { offset: 1, color: 'rgba(0, 255, 170, 0.0)' }
            ]
          }
        },
        markLine: {
          silent: true,
          data: [{ yAxis: 0, name: 'Helada' }],
          lineStyle: { color: '#ef4444', type: 'dashed' },
          label: { position: 'start', formatter: 'Helada (0°C)' }
        }
      },
      {
        name: 'Precipitación',
        type: 'bar',
        yAxisIndex: 1,
        data: precips,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#38bdf8' },
              { offset: 1, color: '#0284c7' }
            ]
          },
          borderRadius: [4, 4, 0, 0]
        },
        barMaxWidth: 30
      },
      {
        name: 'Probabilidad Lluvia',
        type: 'line',
        yAxisIndex: 2,
        data: precipProb,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' }
      }
    ]
  };
};

watch(() => props.ensembleData, initChart, { deep: true });
onMounted(initChart);
</script>

<style scoped>
.meteograma-container {
  width: 100%;
  height: 450px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem;
  box-shadow: var(--shadow-md);
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
