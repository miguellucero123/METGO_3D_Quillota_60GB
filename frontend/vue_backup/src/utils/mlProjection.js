/**
 * Normaliza filas de POST /api/ml/predict/batch para MlProjectionChart.
 * Usa valor_actual del mismo resumen OpenMeteo que alimentó el modelo.
 */

const ML_VAR_META = {
  temperatura_max: { label: 'T. máx', unidad: '°C', field: 'temperatura_max' },
  temperatura_min: { label: 'T. mín', unidad: '°C', field: 'temperatura_min' },
  humedad: { label: 'Humedad', unidad: '%', field: 'humedad' },
  precipitacion: { label: 'Lluvia', unidad: 'mm', field: 'precipitacion' },
  presion: { label: 'Presión', unidad: 'hPa', field: 'presion' },
  viento: { label: 'Viento', unidad: 'km/h', field: 'viento' },
}

export function mapMlProjectionItems(batchRows, fallbackMeteo = null) {
  const rows = Array.isArray(batchRows) ? batchRows : batchRows?.resultados || []
  const out = []

  for (const hit of rows) {
    const varKey = hit?.variable
    const meta = ML_VAR_META[varKey] || {
      label: varKey,
      unidad: '',
      field: varKey,
    }
    const predObj = hit?.prediccion
    if (!predObj || typeof predObj !== 'object' || predObj.error) continue

    const val =
      predObj.prediccion ?? predObj.valor ?? hit.prediccion
    if (val == null || Number.isNaN(Number(val))) continue

    const actual =
      predObj.valor_actual ??
      hit.valor_actual ??
      (fallbackMeteo ? fallbackMeteo[meta.field] : null)

    out.push({
      variable: varKey,
      label: meta.label,
      unidad: meta.unidad,
      actual: actual != null ? Number(actual) : null,
      prediccion: Number(val),
      tipoDato: predObj.tipo_dato,
      fechaReferencia: predObj.fecha_referencia,
    })
  }
  return out
}

export const ML_VARS_DASHBOARD = Object.entries(ML_VAR_META).map(([variable, m]) => ({
  variable,
  label: m.label,
  unidad: m.unidad,
  field: m.field,
}))
