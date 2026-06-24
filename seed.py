"""Popula o banco com produtos reais da DummyJSON (eletrônicos + acessórios)."""

import requests

BASE = "http://localhost:8000"
DUMMY = "https://dummyjson.com"

# Mapeamento de categoria DummyJSON → nome no nosso banco
CATEGORY_MAP = {
    "smartphones":          "Celulares",
    "laptops":              "Eletrônicos",
    "tablets":              "Eletrônicos",
    "mobile-accessories":   "Acessórios",
    "computer-accessories": "Acessórios",
    "sports-accessories":   "Esportes",
    "home-decoration":      "Casa e Decoração",
    "furniture":            "Casa e Decoração",
    "skin-care":            "Beleza e Saúde",
    "fragrances":           "Beleza e Saúde",
}

OUR_CATEGORIES = sorted(set(CATEGORY_MAP.values()))

# --- 1. Criar categorias ---
print("Criando categorias...")
cat_ids: dict[str, str] = {}
for name in OUR_CATEGORIES:
    r = requests.post(f"{BASE}/categories/", json={"name": name})
    if r.status_code in (200, 201):
        cat_ids[name] = r.json()["id"]
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name}: {r.text}")

# --- 2. Buscar produtos da DummyJSON ---
print("\nBuscando produtos da DummyJSON...")
dummy_products: list[dict] = []
for slug in CATEGORY_MAP:
    r = requests.get(f"{DUMMY}/products/category/{slug}?limit=5")
    if r.ok:
        dummy_products.extend(r.json().get("products", []))
        print(f"  ✓ {slug} ({len(r.json().get('products', []))} produtos)")
    else:
        print(f"  ✗ {slug}: {r.status_code}")

# --- 3. Inserir produtos ---
print(f"\nInserindo {len(dummy_products)} produtos...")
ok = 0
for p in dummy_products:
    slug = p.get("category", "")
    our_cat = CATEGORY_MAP.get(slug)
    cat_id = cat_ids.get(our_cat) if our_cat else None
    if not cat_id:
        continue

    # Pega a primeira imagem disponível
    images = p.get("images") or []
    thumbnail = p.get("thumbnail")
    image_url = images[0] if images else thumbnail

    # Converte preço de USD para BRL (aproximado)
    price_brl = round(p["price"] * 5.7, 2)

    payload = {
        "category_id": cat_id,
        "name": p["title"],
        "description": p.get("description", ""),
        "price": price_brl,
        "quantity_available": p.get("stock", 10),
        "image_url": image_url,
    }
    r = requests.post(f"{BASE}/products/", json=payload)
    if r.status_code in (200, 201):
        ok += 1
        print(f"  ✓ {p['title']}")
    else:
        print(f"  ✗ {p['title']}: {r.text}")

print(f"\nPronto! {ok}/{len(dummy_products)} produtos inseridos.")
