/** Exportación CSV/JSON desde el cliente. */

export function exportarDatosCSV(rows, nombreArchivo) {
  if (!rows?.length) return
  const keys = Object.keys(rows[0])
  const lines = [keys.join(',')]
  for (const r of rows) {
    lines.push(keys.map((k) => JSON.stringify(r[k] ?? '')).join(','))
  }
  descargarBlob(lines.join('\n'), `${nombreArchivo}.csv`, 'text/csv')
}

export function exportarDatosJSON(rows, nombreArchivo) {
  descargarBlob(JSON.stringify(rows, null, 2), `${nombreArchivo}.json`, 'application/json')
}

function descargarBlob(contenido, nombre, tipo) {
  const blob = new Blob([contenido], { type: tipo })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = nombre
  a.click()
  URL.revokeObjectURL(url)
}
