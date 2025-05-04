import os
import io
import requests
from google.cloud import vision

# Ensure environment variable for Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "superb-webbing-455211-d7-2e140293e808.json"

# Google Vision API client
client = vision.ImageAnnotatorClient()

# Label-to-category mapping
categories = {
    "Dog": "Kutya",
    "Cat": "Macska",
    "Rabbit": "Kisemlősök",
    "Hamster": "Kisemlősök",
    "Guinea pig": "Kisemlősök",
    "Ferret": "Kisemlősök",
    "Mouse": "Kisemlősök",
    "Rat": "Kisemlősök",
    "Gerbil": "Kisemlősök",
    "Fish": "Halak, hüllők",
    "Reptile": "Halak, hüllők",
    "Lizard": "Halak, hüllők",
    "Turtle": "Halak, hüllők",
    "Snake": "Halak, hüllők",
    "Frog": "Halak, hüllők"
}

# Hotcakes API details
API_KEY = "1-288389cf-7bc1-48bc-be62-f5d43693d830"
BASE_URL = "http://rendfejl1003.northeurope.cloudapp.azure.com:8080/DesktopModules/Hotcakes/API/rest/v1"

def detect_animal_from_bytes(image_bytes: bytes):
    image = vision.Image(content=image_bytes)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    detected_labels = [label.description for label in labels]
    matched = list({categories[label] for label in detected_labels if label in categories})

    return matched, detected_labels

def get_category_bvin(animal_name):
    url = f"{BASE_URL}/categories?key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    categories_data = data.get("Content", [])

    for category in categories_data:
        if animal_name.lower() in category.get('Name', '').lower():
            return category.get('Bvin')
    
    return None

def get_products_by_category_bvin(bvin):
    url = f"{BASE_URL}/products?key={API_KEY}&bycategory={bvin}&page=1&pagesize=16"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    products = data.get("Content", {}).get("Products", [])
    return products

def get_products_from_image(image_bytes):
    matched_categories, detected_labels = detect_animal_from_bytes(image_bytes)
    if not matched_categories:
        return {
            "error": "Nem található megfelelő állatkategória.",
            "detected_labels": detected_labels
        }

    results = []
    for category_name in matched_categories:
        bvin = get_category_bvin(category_name)
        if bvin:
            products = get_products_by_category_bvin(bvin)
            results.extend(products)

    return results

# Example usage for testing locally
if __name__ == "__main__":
    with open("kutya.jpg", "rb") as f:
        image_data = f.read()
    result = get_products_from_image(image_data)
    if isinstance(result, dict) and "error" in result:
        print(f"Hiba: {result['error']}")
        print(f"Felismerhető címkék: {', '.join(result['detected_labels'])}")
    else:
        for product in result:
            print(f"- {product.get('ProductName')} (SKU: {product.get('Sku')})")