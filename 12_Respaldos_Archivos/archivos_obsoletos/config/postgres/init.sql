-- 🌾 METGO 3D - PostgreSQL Initialization
-- Sistema Meteorológico Agrícola Quillota - Base de Datos

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS metgo3d;

-- Usar la base de datos
\c metgo3d;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Tabla de datos meteorológicos
CREATE TABLE IF NOT EXISTS datos_meteorologicos (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperatura DECIMAL(5,2),
    precipitacion DECIMAL(8,2),
    viento_velocidad DECIMAL(5,2),
    viento_direccion DECIMAL(5,2),
    humedad DECIMAL(5,2),
    presion DECIMAL(7,2),
    radiacion_solar DECIMAL(8,2),
    punto_rocio DECIMAL(5,2),
    fuente VARCHAR(50) DEFAULT 'sintetico',
    calidad DECIMAL(3,2) DEFAULT 1.0,
    procesado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de datos IoT
CREATE TABLE IF NOT EXISTS datos_iot (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    valor DECIMAL(10,4) NOT NULL,
    unidad VARCHAR(20),
    bateria DECIMAL(5,2),
    senal DECIMAL(5,2),
    ubicacion JSONB,
    procesado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de predicciones ML
CREATE TABLE IF NOT EXISTS predicciones_ml (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    variable VARCHAR(50) NOT NULL,
    prediccion DECIMAL(10,4) NOT NULL,
    confianza DECIMAL(3,2),
    horizonte INTEGER,
    procesado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nivel VARCHAR(20) NOT NULL,
    mensaje TEXT NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    procesada BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de métricas del sistema
CREATE TABLE IF NOT EXISTS metricas_sistema (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    componente VARCHAR(50) NOT NULL,
    metrica VARCHAR(100) NOT NULL,
    valor DECIMAL(15,4),
    unidad VARCHAR(20),
    tags JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs del sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    nivel VARCHAR(20) NOT NULL,
    componente VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    contexto JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de configuración del sistema
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    tipo VARCHAR(20) DEFAULT 'string',
    descripcion TEXT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'usuario',
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP WITH TIME ZONE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones
CREATE TABLE IF NOT EXISTS sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expira TIMESTAMP WITH TIME ZONE NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_datos_meteorologicos_timestamp ON datos_meteorologicos(timestamp);
CREATE INDEX IF NOT EXISTS idx_datos_meteorologicos_temperatura ON datos_meteorologicos(temperatura);
CREATE INDEX IF NOT EXISTS idx_datos_meteorologicos_precipitacion ON datos_meteorologicos(precipitacion);
CREATE INDEX IF NOT EXISTS idx_datos_meteorologicos_procesado ON datos_meteorologicos(procesado);

CREATE INDEX IF NOT EXISTS idx_datos_iot_timestamp ON datos_iot(timestamp);
CREATE INDEX IF NOT EXISTS idx_datos_iot_sensor_id ON datos_iot(sensor_id);
CREATE INDEX IF NOT EXISTS idx_datos_iot_tipo ON datos_iot(tipo);
CREATE INDEX IF NOT EXISTS idx_datos_iot_procesado ON datos_iot(procesado);

CREATE INDEX IF NOT EXISTS idx_predicciones_ml_timestamp ON predicciones_ml(timestamp);
CREATE INDEX IF NOT EXISTS idx_predicciones_ml_modelo ON predicciones_ml(modelo);
CREATE INDEX IF NOT EXISTS idx_predicciones_ml_variable ON predicciones_ml(variable);
CREATE INDEX IF NOT EXISTS idx_predicciones_ml_procesado ON predicciones_ml(procesado);

CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas(tipo);
CREATE INDEX IF NOT EXISTS idx_alertas_nivel ON alertas(nivel);
CREATE INDEX IF NOT EXISTS idx_alertas_activa ON alertas(activa);

CREATE INDEX IF NOT EXISTS idx_metricas_sistema_timestamp ON metricas_sistema(timestamp);
CREATE INDEX IF NOT EXISTS idx_metricas_sistema_componente ON metricas_sistema(componente);
CREATE INDEX IF NOT EXISTS idx_metricas_sistema_metrica ON metricas_sistema(metrica);

CREATE INDEX IF NOT EXISTS idx_logs_sistema_timestamp ON logs_sistema(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_sistema_nivel ON logs_sistema(nivel);
CREATE INDEX IF NOT EXISTS idx_logs_sistema_componente ON logs_sistema(componente);

CREATE INDEX IF NOT EXISTS idx_configuracion_sistema_clave ON configuracion_sistema(clave);
CREATE INDEX IF NOT EXISTS idx_configuracion_sistema_activa ON configuracion_sistema(activa);

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token);
CREATE INDEX IF NOT EXISTS idx_sesiones_usuario_id ON sesiones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sesiones_activa ON sesiones(activa);

-- Funciones para actualizar timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar timestamps
CREATE TRIGGER update_datos_meteorologicos_updated_at 
    BEFORE UPDATE ON datos_meteorologicos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datos_iot_updated_at 
    BEFORE UPDATE ON datos_iot 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predicciones_ml_updated_at 
    BEFORE UPDATE ON predicciones_ml 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alertas_updated_at 
    BEFORE UPDATE ON alertas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configuracion_sistema_updated_at 
    BEFORE UPDATE ON configuracion_sistema 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at 
    BEFORE UPDATE ON usuarios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Datos iniciales de configuración
INSERT INTO configuracion_sistema (clave, valor, tipo, descripcion) VALUES
('sistema.version', '2.0', 'string', 'Versión del sistema'),
('sistema.nombre', 'METGO 3D', 'string', 'Nombre del sistema'),
('sistema.descripcion', 'Sistema Meteorológico Agrícola Quillota', 'string', 'Descripción del sistema'),
('quillota.latitud', '-32.8833', 'decimal', 'Latitud de Quillota'),
('quillota.longitud', '-71.2333', 'decimal', 'Longitud de Quillota'),
('quillota.altitud', '127', 'integer', 'Altitud de Quillota'),
('meteorologia.frecuencia_muestreo', '3600', 'integer', 'Frecuencia de muestreo en segundos'),
('meteorologia.retencion_datos', '365', 'integer', 'Retención de datos en días'),
('alertas.niveles', '["critica", "alta", "media", "baja"]', 'json', 'Niveles de alerta'),
('apis.timeout', '30', 'integer', 'Timeout de APIs en segundos'),
('apis.max_reintentos', '3', 'integer', 'Máximo número de reintentos'),
('ml.modelos', '["lstm", "transformer", "random_forest", "gradient_boosting"]', 'json', 'Modelos de ML disponibles'),
('visualizacion.tipos', '["2d", "3d", "interactiva", "estatica"]', 'json', 'Tipos de visualización'),
('iot.protocolos', '["mqtt", "http", "udp"]', 'json', 'Protocolos IoT soportados'),
('seguridad.autenticacion', 'true', 'boolean', 'Habilitar autenticación'),
('seguridad.autorizacion', 'true', 'boolean', 'Habilitar autorización'),
('monitoreo.frecuencia', '60', 'integer', 'Frecuencia de monitoreo en segundos'),
('backup.frecuencia', 'diaria', 'string', 'Frecuencia de respaldos'),
('backup.retencion', '30', 'integer', 'Retención de respaldos en días'),
('performance.cache', 'true', 'boolean', 'Habilitar cache'),
('performance.paralelismo', 'true', 'boolean', 'Habilitar paralelismo')
ON CONFLICT (clave) DO NOTHING;

-- Usuario administrador por defecto
INSERT INTO usuarios (username, email, password_hash, rol) VALUES
('admin', 'admin@metgo3d.cl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Comentarios en las tablas
COMMENT ON TABLE datos_meteorologicos IS 'Datos meteorológicos del sistema METGO 3D';
COMMENT ON TABLE datos_iot IS 'Datos de sensores IoT del sistema';
COMMENT ON TABLE predicciones_ml IS 'Predicciones generadas por modelos de ML';
COMMENT ON TABLE alertas IS 'Alertas del sistema meteorológico';
COMMENT ON TABLE metricas_sistema IS 'Métricas de rendimiento del sistema';
COMMENT ON TABLE logs_sistema IS 'Logs del sistema';
COMMENT ON TABLE configuracion_sistema IS 'Configuración del sistema';
COMMENT ON TABLE usuarios IS 'Usuarios del sistema';
COMMENT ON TABLE sesiones IS 'Sesiones de usuarios';

-- Vistas útiles
CREATE OR REPLACE VIEW vista_datos_recientes AS
SELECT 
    dm.*,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - dm.timestamp)) as segundos_desde_lectura
FROM datos_meteorologicos dm
WHERE dm.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY dm.timestamp DESC;

CREATE OR REPLACE VIEW vista_alertas_activas AS
SELECT 
    a.*,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.timestamp)) as segundos_desde_alerta
FROM alertas a
WHERE a.activa = TRUE
ORDER BY a.timestamp DESC;

CREATE OR REPLACE VIEW vista_metricas_recientes AS
SELECT 
    ms.*,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ms.timestamp)) as segundos_desde_metrica
FROM metricas_sistema ms
WHERE ms.timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
ORDER BY ms.timestamp DESC;

-- Función para limpiar datos antiguos
CREATE OR REPLACE FUNCTION limpiar_datos_antiguos()
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER := 0;
BEGIN
    -- Eliminar datos meteorológicos antiguos (más de 1 año)
    DELETE FROM datos_meteorologicos 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    
    -- Eliminar datos IoT antiguos (más de 6 meses)
    DELETE FROM datos_iot 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '6 months';
    
    -- Eliminar predicciones antiguas (más de 3 meses)
    DELETE FROM predicciones_ml 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '3 months';
    
    -- Eliminar alertas procesadas antiguas (más de 1 mes)
    DELETE FROM alertas 
    WHERE procesada = TRUE AND timestamp < CURRENT_TIMESTAMP - INTERVAL '1 month';
    
    -- Eliminar métricas antiguas (más de 1 mes)
    DELETE FROM metricas_sistema 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 month';
    
    -- Eliminar logs antiguos (más de 1 mes)
    DELETE FROM logs_sistema 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 month';
    
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas del sistema
CREATE OR REPLACE FUNCTION obtener_estadisticas_sistema()
RETURNS JSON AS $$
DECLARE
    resultado JSON;
BEGIN
    SELECT json_build_object(
        'datos_meteorologicos', (SELECT COUNT(*) FROM datos_meteorologicos),
        'datos_iot', (SELECT COUNT(*) FROM datos_iot),
        'predicciones_ml', (SELECT COUNT(*) FROM predicciones_ml),
        'alertas_activas', (SELECT COUNT(*) FROM alertas WHERE activa = TRUE),
        'usuarios_activos', (SELECT COUNT(*) FROM usuarios WHERE activo = TRUE),
        'ultima_actualizacion', CURRENT_TIMESTAMP
    ) INTO resultado;
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- Crear usuario para la aplicación
CREATE USER metgo3d_app WITH PASSWORD 'metgo3d_app_2024_secure';
GRANT CONNECT ON DATABASE metgo3d TO metgo3d_app;
GRANT USAGE ON SCHEMA public TO metgo3d_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO metgo3d_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO metgo3d_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO metgo3d_app;

-- Configurar permisos por defecto
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO metgo3d_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO metgo3d_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO metgo3d_app;
