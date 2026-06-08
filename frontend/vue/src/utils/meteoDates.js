/** Fecha calendario YYYY-MM-DD en zona Chile (America/Santiago). */
export function hoyChile() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Santiago',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date())
}

export function diaDeFila(row) {
  return String(row?.fecha ?? '').slice(0, 10)
}

/** Histórico: solo días ya ocurridos (≤ hoy Chile). */
export function filtrarHistoricoHastaHoy(rows) {
  const hoy = hoyChile()
  return (rows || []).filter((r) => {
    const d = diaDeFila(r)
    return d.length === 10 && d <= hoy
  })
}

/** Pronóstico: hoy y días siguientes. */
export function filtrarPronosticoDesdeHoy(rows) {
  const hoy = hoyChile()
  return (rows || []).filter((r) => {
    const d = diaDeFila(r)
    return d.length === 10 && d >= hoy
  })
}

/** Una fila por día, orden cronológico, últimos N días hasta hoy. */
export function seriesHistoricoPorDia(rows, dias = 30) {
  const porDia = new Map()
  for (const r of filtrarHistoricoHastaHoy(rows)) {
    const dia = diaDeFila(r)
    porDia.set(dia, { ...r, fecha: dia })
  }
  return [...porDia.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-dias)
    .map(([, r]) => r)
}

export function formatoDiaCorto(fecha) {
  const d = String(fecha ?? '').slice(0, 10)
  if (d.length < 10) return d
  const [, mm, dd] = d.split('-')
  return `${dd}/${mm}`
}
