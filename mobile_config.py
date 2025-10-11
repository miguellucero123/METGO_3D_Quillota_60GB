# Configuración específica para optimización móvil
import streamlit as st

class MobileConfig:
    """Configuración optimizada para dispositivos móviles"""
    
    @staticmethod
    def setup_mobile_page_config():
        """Configura la página para optimización móvil"""
        st.set_page_config(
            page_title="METGO Mobile",
            page_icon="📱",
            layout="wide",
            initial_sidebar_state="collapsed",
            menu_items={
                'Get Help': 'https://metgo.cl/help',
                'Report a bug': 'https://metgo.cl/bug',
                'About': 'Sistema METGO - Optimizado para Móviles'
            }
        )
    
    @staticmethod
    def get_mobile_css():
        """CSS optimizado específicamente para móviles"""
        return """
        <style>
            /* Optimización móvil avanzada */
            .mobile-container {
                max-width: 100%;
                margin: 0 auto;
                padding: 0.5rem;
            }
            
            .mobile-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .mobile-card {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
                transition: transform 0.2s ease;
            }
            
            .mobile-card:active {
                transform: scale(0.98);
            }
            
            .mobile-metric {
                text-align: center;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 8px;
                margin: 0.25rem 0;
                border: 1px solid #e9ecef;
            }
            
            .mobile-number {
                font-size: 1.8rem;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }
            
            .mobile-label {
                color: #7f8c8d;
                font-size: 0.8rem;
                margin: 0.25rem 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .mobile-button {
                width: 100%;
                padding: 0.75rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 0.5rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
                font-size: 1rem;
            }
            
            .mobile-button:hover {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            .mobile-button:active {
                transform: translateY(0);
            }
            
            .mobile-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #e9ecef;
                padding: 0.5rem;
                z-index: 1000;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            }
            
            .mobile-nav-item {
                display: inline-block;
                text-align: center;
                padding: 0.5rem;
                margin: 0 0.25rem;
                border-radius: 8px;
                transition: background 0.3s ease;
                text-decoration: none;
                color: #7f8c8d;
                font-size: 0.8rem;
            }
            
            .mobile-nav-item.active {
                background: #667eea;
                color: white;
            }
            
            .mobile-nav-item:hover {
                background: #f8f9fa;
            }
            
            .mobile-swipe {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            
            .mobile-swipe::-webkit-scrollbar {
                display: none;
            }
            
            .mobile-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.5rem;
                margin: 1rem 0;
            }
            
            .mobile-grid-3 {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 0.5rem;
                margin: 1rem 0;
            }
            
            .mobile-full-width {
                width: 100%;
                margin: 0.5rem 0;
            }
            
            .mobile-chart {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                margin: 0.5rem 0;
            }
            
            .mobile-alert {
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid;
                animation: slideIn 0.3s ease;
            }
            
            .mobile-alert.success {
                background: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            
            .mobile-alert.warning {
                background: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            
            .mobile-alert.error {
                background: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            
            .mobile-alert.info {
                background: #d1ecf1;
                border-color: #17a2b8;
                color: #0c5460;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Mejoras para pantallas pequeñas */
            @media (max-width: 768px) {
                .mobile-container {
                    padding: 0.25rem;
                }
                
                .mobile-header {
                    padding: 0.75rem;
                    margin-bottom: 0.75rem;
                }
                
                .mobile-card {
                    padding: 0.75rem;
                    margin: 0.25rem 0;
                }
                
                .mobile-number {
                    font-size: 1.5rem;
                }
                
                .mobile-grid {
                    grid-template-columns: 1fr;
                }
                
                .mobile-grid-3 {
                    grid-template-columns: 1fr 1fr;
                }
            }
            
            @media (max-width: 480px) {
                .mobile-grid-3 {
                    grid-template-columns: 1fr;
                }
                
                .mobile-number {
                    font-size: 1.3rem;
                }
            }
            
            /* Optimización para touch */
            .mobile-touch-target {
                min-height: 44px;
                min-width: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Mejoras de accesibilidad */
            .mobile-focus:focus {
                outline: 2px solid #667eea;
                outline-offset: 2px;
            }
            
            /* Animaciones suaves */
            .mobile-smooth {
                transition: all 0.3s ease;
            }
            
            /* Modo oscuro móvil */
            @media (prefers-color-scheme: dark) {
                .mobile-card {
                    background: #2d3748;
                    color: #e2e8f0;
                }
                
                .mobile-metric {
                    background: #4a5568;
                    border-color: #718096;
                }
                
                .mobile-number {
                    color: #e2e8f0;
                }
                
                .mobile-label {
                    color: #a0aec0;
                }
            }
            
            /* Optimización de rendimiento */
            .mobile-lazy {
                opacity: 0;
                animation: fadeIn 0.5s ease forwards;
            }
            
            @keyframes fadeIn {
                to {
                    opacity: 1;
                }
            }
            
            /* Scroll personalizado */
            .mobile-scroll {
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
            }
        </style>
        """
    
    @staticmethod
    def get_mobile_js():
        """JavaScript para funcionalidades móviles avanzadas"""
        return """
        <script>
            // Detectar dispositivo móvil
            function isMobile() {
                return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            }
            
            // Detectar orientación
            function handleOrientationChange() {
                if (window.innerHeight > window.innerWidth) {
                    document.body.classList.add('portrait');
                } else {
                    document.body.classList.add('landscape');
                }
            }
            
            // Gestos táctiles
            let touchStartX = 0;
            let touchStartY = 0;
            
            document.addEventListener('touchstart', function(e) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
            });
            
            document.addEventListener('touchend', function(e) {
                const touchEndX = e.changedTouches[0].clientX;
                const touchEndY = e.changedTouches[0].clientY;
                const diffX = touchStartX - touchEndX;
                const diffY = touchStartY - touchEndY;
                
                // Swipe horizontal
                if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                    if (diffX > 0) {
                        // Swipe izquierda
                        console.log('Swipe izquierda');
                    } else {
                        // Swipe derecha
                        console.log('Swipe derecha');
                    }
                }
                
                // Swipe vertical
                if (Math.abs(diffY) > Math.abs(diffX) && Math.abs(diffY) > 50) {
                    if (diffY > 0) {
                        // Swipe arriba
                        console.log('Swipe arriba');
                    } else {
                        // Swipe abajo
                        console.log('Swipe abajo');
                    }
                }
            });
            
            // Optimización de scroll
            let ticking = false;
            function updateScrollPosition() {
                const scrollTop = window.pageYOffset;
                document.body.style.setProperty('--scroll-top', scrollTop + 'px');
                ticking = false;
            }
            
            document.addEventListener('scroll', function() {
                if (!ticking) {
                    requestAnimationFrame(updateScrollPosition);
                    ticking = true;
                }
            });
            
            // Lazy loading de imágenes
            function lazyLoadImages() {
                const images = document.querySelectorAll('img[data-src]');
                const imageObserver = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }
                    });
                });
                
                images.forEach(img => imageObserver.observe(img));
            }
            
            // Inicialización
            document.addEventListener('DOMContentLoaded', function() {
                if (isMobile()) {
                    document.body.classList.add('mobile');
                }
                
                handleOrientationChange();
                window.addEventListener('orientationchange', handleOrientationChange);
                lazyLoadImages();
                
                // Agregar clase de carga
                document.body.classList.add('loaded');
            });
            
            // PWA - Service Worker
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registrado'))
                    .catch(error => console.log('SW error:', error));
            }
            
            // Notificaciones push
            function requestNotificationPermission() {
                if ('Notification' in window && Notification.permission === 'default') {
                    Notification.requestPermission();
                }
            }
            
            // Vibración
            function vibrate(pattern) {
                if ('vibrate' in navigator) {
                    navigator.vibrate(pattern);
                }
            }
            
            // Función para feedback táctil
            function hapticFeedback() {
                vibrate([50]);
            }
            
            // Exportar funciones globalmente
            window.MobileUtils = {
                isMobile: isMobile,
                vibrate: vibrate,
                hapticFeedback: hapticFeedback,
                requestNotificationPermission: requestNotificationPermission
            };
        </script>
        """
    
    @staticmethod
    def apply_mobile_optimizations():
        """Aplica todas las optimizaciones móviles"""
        MobileConfig.setup_mobile_page_config()
        st.markdown(MobileConfig.get_mobile_css(), unsafe_allow_html=True)
        st.markdown(MobileConfig.get_mobile_js(), unsafe_allow_html=True)
        
        # Configurar columnas para móvil
        st.markdown("""
        <style>
            .stApp > div {
                padding-top: 1rem;
                padding-bottom: 5rem; /* Espacio para navegación móvil */
            }
            
            .stSidebar > div {
                padding-top: 1rem;
            }
            
            /* Optimizar elementos de Streamlit */
            .stSelectbox > div > div {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-height: 44px;
            }
            
            .stButton > button {
                width: 100%;
                min-height: 44px;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: bold;
            }
            
            .stTextInput > div > div > input {
                min-height: 44px;
                border-radius: 8px;
                border: 2px solid #e9ecef;
            }
            
            /* Optimizar gráficos para móvil */
            .js-plotly-plot {
                width: 100% !important;
                height: auto !important;
            }
            
            /* Mejorar legibilidad en móvil */
            .stMarkdown {
                font-size: 1rem;
                line-height: 1.5;
            }
            
            /* Optimizar tablas para móvil */
            .stDataFrame {
                font-size: 0.9rem;
            }
            
            /* Scroll horizontal para tablas */
            .stDataFrame > div {
                overflow-x: auto;
            }
        </style>
        """, unsafe_allow_html=True)
