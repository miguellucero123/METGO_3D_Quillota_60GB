# Sistema Unificado Autenticado - METGO 3D

## Descripción
Sistema completo con autenticación que integra TODOS los notebooks y archivos Python del proyecto METGO 3D.

## Características Principales

### 1. Autenticación de Usuario
- Sistema de login con usuario y contraseña
- Gestión de sesiones con tokens
- Control de permisos por rol
- Sesiones de 24 horas de duración

### 2. Integración Completa
- **27 notebooks** integrados
- **82 archivos Python** integrados
- **109 módulos totales** del proyecto
- Categorización automática por tipo

### 3. Funcionalidades

#### Dashboard Principal
- Vista general del sistema
- Métricas de módulos
- Distribución por categorías
- Estadísticas en tiempo real

#### Gestión de Notebooks
- Listado de todos los notebooks
- Filtrado por categoría
- Visualización de contenido
- Ejecución individual
- Estado de ejecución

#### Gestión de Archivos Python
- Listado de todos los archivos .py
- Filtrado por categoría
- Visualización de código
- Ejecución individual
- Monitoreo de resultados

#### Ejecutor de Módulos
- Selección de módulo específico
- Ejecución con captura de salida
- Manejo de errores
- Timeout configurado

#### Estadísticas
- Gráficos de distribución
- Resumen del sistema
- Información detallada

## Usuarios por Defecto

### Administrador
- **Usuario:** admin
- **Password:** admin123
- **Permisos:** ejecutar, ver, editar, eliminar

### Usuario Normal
- **Usuario:** usuario
- **Password:** usuario123
- **Permisos:** ejecutar, ver

## Cómo Usar

### 1. Iniciar el Sistema
```bash
python -m streamlit run sistema_unificado_autenticado.py --server.port 8504
```

### 2. Acceder al Dashboard
```
URL: http://localhost:8504
```

### 3. Iniciar Sesión
1. Ingresa usuario y contraseña
2. Click en "Iniciar Sesión"
3. Accede al dashboard completo

### 4. Navegar por el Sistema
- **Tab Dashboard:** Vista general
- **Tab Notebooks:** Gestión de notebooks
- **Tab Archivos Python:** Gestión de archivos .py
- **Tab Ejecutar Módulo:** Ejecutor de módulos
- **Tab Estadísticas:** Gráficos y estadísticas

## Módulos Integrados

### Notebooks (27)
- Sistema Principal
- Configuración
- Procesamiento de Datos
- Análisis Meteorológico
- Visualizaciones
- Modelos ML
- Dashboard Interactivo
- Reportes
- APIs Externas
- Testing
- Deployment
- Monitoreo
- Respaldos
- Optimización
- Y más...

### Archivos Python (82)
- Sistemas de autenticación
- Dashboards
- Integradores
- Orquestadores
- Pipelines
- Configuración
- Monitoreo
- Respaldos
- Testing
- IA/ML
- IoT
- Análisis
- Visualización
- APIs
- Deployment
- Gestión
- Y más...

## Categorías de Módulos

### Notebooks
- core
- config
- data
- analysis
- visualization
- ml
- dashboard
- reports
- api
- testing
- deployment
- monitoring
- backup
- optimization
- advanced_reports
- integration
- otros

### Archivos Python
- autenticacion
- dashboard
- sistema
- integracion
- orquestacion
- pipeline
- configuracion
- monitoreo
- respaldo
- testing
- ia_ml
- iot
- analisis
- visualizacion
- api
- deployment
- gestion
- otros

## Archivos del Sistema

### Principales
- `sistema_unificado_autenticado.py` - Sistema principal
- `auth_module.py` - Módulo de autenticación
- `integrador_modulos.py` - Integrador de módulos

### Configuración
- `config/usuarios.json` - Base de datos de usuarios
- `config/sesiones.json` - Sesiones activas

## Permisos

### Administrador
- ✅ Ejecutar módulos
- ✅ Ver contenido
- ✅ Editar configuración
- ✅ Eliminar módulos

### Usuario
- ✅ Ejecutar módulos
- ✅ Ver contenido
- ❌ Editar configuración
- ❌ Eliminar módulos

## Características Técnicas

### Seguridad
- Contraseñas hasheadas con SHA-256
- Tokens de sesión únicos
- Expiración de sesiones
- Control de permisos por rol

### Integración
- Escaneo automático de notebooks
- Escaneo automático de archivos .py
- Categorización inteligente
- Filtrado dinámico

### Ejecución
- Timeout configurado
- Captura de salida y errores
- Manejo de excepciones
- Logging estructurado

## Desarrollo Futuro

### Próximas Mejoras
1. Editor de código integrado
2. Sistema de notificaciones
3. Historial de ejecuciones
4. Gestión de dependencias
5. Sistema de plugins
6. API REST
7. Integración con Git
8. Sistema de tareas programadas

## Soporte Técnico

### Logs
Los logs del sistema se encuentran en:
- Consola de ejecución
- Archivos en `logs/`

### Errores Comunes
1. **Error de autenticación:** Verificar usuario y contraseña
2. **Error de ejecución:** Verificar permisos del usuario
3. **Timeout:** Aumentar tiempo de espera en configuración

## Conclusión

El Sistema Unificado Autenticado integra completamente todos los notebooks y archivos Python del proyecto METGO 3D en un solo dashboard con autenticación y control de acceso, permitiendo gestionar y ejecutar todos los módulos del proyecto de manera centralizada y segura.



