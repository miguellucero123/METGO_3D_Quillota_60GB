/** Exportar SVG o instancia ECharts a PNG desde el cliente. */

export function exportarSvgPng(svgElement, nombreArchivo = 'grafico') {
  if (!svgElement) return
  const clone = svgElement.cloneNode(true)
  const bbox = svgElement.getBoundingClientRect()
  const w = Math.max(640, Math.round(bbox.width) || 640)
  const h = Math.max(200, Math.round(bbox.height) || 240)
  clone.setAttribute('width', String(w))
  clone.setAttribute('height', String(h))
  if (!clone.getAttribute('xmlns')) {
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  }
  const svgData = new XMLSerializer().serializeToString(clone)
  const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = w
    canvas.height = h
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#0b1120'
    ctx.fillRect(0, 0, w, h)
    ctx.drawImage(img, 0, 0, w, h)
    canvas.toBlob((png) => {
      if (!png) return
      const a = document.createElement('a')
      a.href = URL.createObjectURL(png)
      a.download = `${nombreArchivo}.png`
      a.click()
      URL.revokeObjectURL(a.href)
    })
    URL.revokeObjectURL(url)
  }
  img.src = url
}

/** @param {import('echarts').EChartsType | null | undefined} chartInstance */
export function exportarEchartsPng(chartInstance, nombreArchivo = 'grafico') {
  if (!chartInstance || typeof chartInstance.getDataURL !== 'function') return
  const url = chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#0b1120',
  })
  const a = document.createElement('a')
  a.href = url
  a.download = `${nombreArchivo}.png`
  a.click()
}
