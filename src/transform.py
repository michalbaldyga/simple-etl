"""
products = [
    {'id': 1, 'quantity': 5, 'category': 'mobile'}
]
"""
from src.extract import get_product_category

def group_products_by_category(products):
    grouped = {}
    for product in products:
        category = product.get('category')
        quantity = product.get('quantity')
        grouped[category] = grouped.get(category, 0) + quantity
    return grouped


def extract_products_from_carts(carts):
    return [product for cart in carts
            for product in extract_products_from_cart(cart)]


def extract_products_from_cart(cart):
    products = cart.get('products')
    result = []

    for product in products:
        product_id = product.get('id')
        product_category = get_product_category(product_id)
        result.append({
            'id': product_id,
            'quantity': product.get('quantity'),
            'category': product_category
        })

    return result
