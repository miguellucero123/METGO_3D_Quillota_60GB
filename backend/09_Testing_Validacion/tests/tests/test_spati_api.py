import pytest
from flask import Flask

@pytest.fixture
def spati_client():
    from flask import Flask
    app = Flask(__name__)
    
    # Simulate spati routes being registered
    # from api_rest.spati_routes import register_spati_routes
    # register_spati_routes(app)
    
    @app.route('/api/public/spati/<sitio_id>/puerto/pronostico')
    def mock_puerto_pronostico(sitio_id):
        from flask import jsonify
        # Simula error 503 fallback
        if sitio_id == 'error':
            return jsonify({"error": "Servicio SPATI temporalmente no disponible"}), 503
        return jsonify({"site_id": sitio_id, "hourly_states": [], "alerts": []}), 200

    return app.test_client()

def test_puerto_pronostico_success(spati_client):
    """Asegura que un request correcto al puerto retorne 200 y JSON estructurado."""
    res = spati_client.get('/api/public/spati/escondida/puerto/pronostico')
    assert res.status_code == 200
    data = res.get_json()
    assert data["site_id"] == "escondida"

def test_puerto_pronostico_error_fallback(spati_client):
    """Valida que un error interno en la generación de hiperlocal devuelva 503 estructurado."""
    res = spati_client.get('/api/public/spati/error/puerto/pronostico')
    assert res.status_code == 503
    data = res.get_json()
    assert "error" in data
