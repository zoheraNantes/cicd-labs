"""Tests d'API — POINT DE DÉPART (Atelier 1, puis Atelier 9)."""

import pytest

pytestmark = pytest.mark.api


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_liste_produits(client):
    r = client.get("/products")
    assert r.status_code == 200
    assert {"mug", "tshirt"} <= {p["id"] for p in r.json()}


# TODO Atelier 9 : /products/{id} (200, 404), /cart/quote (200, 404, 422), /orders (201, 422), GET /orders/{id}

# """Tests d'API — Atelier 9, Partie A."""
# / products/{id} (200, 404)
def test_produit_existant_200(client):
    r = client.get("/products/mug")
    assert r.status_code == 200
    assert r.json()["id"] == "mug"

def test_produit_inexistant_404(client):
    r = client.get("/products/produit-inconnu")
    assert r.status_code == 404

# /cart/quote : 200
def test_cart_quote_200(client):
    panier = {"items": [{"product_id": "mug", "qty": 2}]}
    r = client.post("/cart/quote", json=panier)
    assert r.status_code == 200
    assert "total" in r.json()

# /cart/quote : 404
def test_cart_quote_404(client):
    panier = {"items": [{"product_id": "produit-inconnu", "qty": 2}]}
    r = client.post("/cart/quote", json=panier)
    assert r.status_code == 404

# /cart/quote : 422 (quantité 0)
def test_cart_quote_quantite_0(client):
    panier = {"items": [{"product_id": "mug", "qty": 0}]}
    r = client.post("/cart/quote", json=panier)
    assert r.status_code == 422

# /cart/quote : 422 (coupon inconnu)
def test_cart_quote_coupon_inconnu(client):
    panier = {
        "items": [{"product_id": "mug", "qty": 2}],
        "coupon": "COUPON_INCONNU"
    }
    r = client.post("/cart/quote", json=panier)
    assert r.status_code == 422

# /cart/quote : 422 (corps invalide)
def test_cart_quote_corps_invalide(client):
    r = client.post("/cart/quote", json={"items": "donnees-invalides"})
    assert r.status_code == 422

# /orders : 201 puis GET /orders/{id}
def test_orders_201(client):
    panier = {"items": [{"product_id": "mug", "qty": 2}]}

    r = client.post("/orders", json=panier)
    assert r.status_code == 201

    commande = r.json()
    r_get = client.get(f"/orders/{commande['id']}")
    assert r_get.json() == commande


# /orders : 422 (panier vide)
def test_orders_422(client):
    r = client.post("/orders", json={"items": []})
    assert r.status_code == 422


# /metrics : vérifier la présence de minishop_http_requests_total
def test_metrics(client):
    r = client.get("/metrics")
    assert "minishop_http_requests_total" in r.text
    


# Variante avec un serveur réel (Docker)
# Désactivée pour les tests avec TestClient

# Importe HTTPX pour envoyer des requêtes HTTP à un serveur réel
# import httpx

# Crée un client HTTP connecté à l'adresse de l'application (app_url)
# with httpx.Client(base_url=app_url) as client:
     # Envoie une requête GET pour récupérer les métriques de l'application
#     response = client.get("/metrics")



# ==================================================
# ATELIER 9 — PARTIE B : TEST DE CONTRAT
# ==================================================

# Vérifie que les routes publiques de MiniShop existent
def test_contrat_api(client):

    # Envoie une requête GET pour récupérer le contrat OpenAPI
    r = client.get("/openapi.json")

    # Vérifie que la requête a réussi (HTTP 200)
    assert r.status_code == 200

    # Convertit la réponse JSON en dictionnaire Python
    contrat = r.json()

    # Vérifie que la route de santé existe
    assert "/health" in contrat["paths"]

    # Vérifie que la route de liste des produits existe
    assert "/products" in contrat["paths"]

    # Vérifie que la route de consultation d'un produit existe
    assert "/products/{product_id}" in contrat["paths"]

    # Vérifie que la route de calcul du panier existe
    assert "/cart/quote" in contrat["paths"]

    # Vérifie que la route de création de commande existe
    assert "/orders" in contrat["paths"]

    # Vérifie que la route de consultation d'une commande existe
    assert "/orders/{order_id}" in contrat["paths"]

