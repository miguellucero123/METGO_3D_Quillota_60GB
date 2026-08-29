-- Script para crear vistas optimizadas en la base de datos METGO 3D
-- Propósito: Optimizar los tiempos de consulta para los dashboards (Streamlit y Vue)
-- y prevenir la edición accidental de datos históricos críticos.

-- 1. Vista Optimizada para el Dashboard Principal (Solo datos esenciales)
CREATE OR REPLACE VIEW v_climate_dashboard_summary AS
SELECT 
    id,
    zone_name,
    timestamp,
    temperature,
    humidity,
    wind_speed,
    precipitation,
    data_source
FROM climate_data
WHERE is_forecast = false;

-- 2. Vista Específica para Izajes (Ventora) y Operaciones Portuarias
-- Filtra solo las variables críticas para el viento y ráfagas.
CREATE OR REPLACE VIEW v_port_lifting_conditions AS
SELECT 
    zone_name,
    timestamp,
    wind_speed as v_ref_kmh,
    wind_gust as gust_kmh,
    wind_direction,
    temperature,
    pressure
FROM climate_data
WHERE timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- 3. Vista de Pronóstico Activo (Solo el pronóstico más reciente emitido)
-- Usando un subquery para obtener siempre la última corrida del modelo (issued_at)
CREATE OR REPLACE VIEW v_latest_forecast AS
SELECT f.*
FROM forecast_data f
INNER JOIN (
    SELECT zone_name, MAX(issued_at) as max_issued
    FROM forecast_data
    GROUP BY zone_name
) latest ON f.zone_name = latest.zone_name AND f.issued_at = latest.max_issued;

-- 4. Vista de Análisis de Alertas (Para el reporte de efectividad)
CREATE OR REPLACE VIEW v_alert_effectiveness AS
SELECT 
    a.zone,
    a.alert_type,
    a.threshold,
    COUNT(al.id) as total_triggers,
    SUM(CASE WHEN al.user_acknowledged = true THEN 1 ELSE 0 END) as acknowledged_triggers
FROM alerts a
LEFT JOIN alert_logs al ON a.id = al.alert_id
GROUP BY a.zone, a.alert_type, a.threshold;
