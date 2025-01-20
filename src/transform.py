import logging.config
import os
from collections.abc import Sequence

from src.extract import get_product_category, get_user_carts, get_user_country

log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
)
logging.config.fileConfig(
    "config/logging.conf",
    defaults={"logfilename": repr(log_file_path)}
)
logger = logging.getLogger("logger_file")


def get_user_data(
        user: dict
) -> dict:
    """
    Get user data with additional information such as country
    and favorite product category.

    Args:
        user: dict
        Dictionary containing user information.

    Returns:
        Dict[str, Any]: Processed user data with added details.
    """
    user_id = user.get('id')
    if not user_id:
        logger.error("User ID is missing.")
        raise ValueError("User ID is missing.")

    first_name = user.get('firstName', "Unknown")
    last_name = user.get('lastName', "Unknown")
    age = user.get('age', "Unknown")
    gender = user.get('gender', "Unknown")

    coordinates = user.get('address', {}).get('coordinates', {})
    lat = coordinates.get('lat')
    lng = coordinates.get('lng')
    country = get_user_country(lat, lng) if lat and lng else "Unknown"

    carts = get_user_carts(user_id).get('carts', [])
    products = extract_products_from_carts(carts)
    grouped_products = group_products_by_category(products)
    favorite_category = get_most_common_category(grouped_products)

    return {
        'firstName': first_name,
        'lastName': last_name,
        'age': age,
        'gender': gender,
        'country': country,
        'faveCategory': favorite_category
    }


def get_most_common_category(
       products: dict[str, int]
) -> str | None:
    """
    Get the category with the highest quantity from a dictionary of products.

    Parameters
    ----------
    products : dict[str, int]
        A dictionary where the keys are product categories and the
        values are the total quantities of products in each category.

    Returns
    -------
    str: The category with the highest quantity.
    """
    return max(products, key=products.get) if products else "Unknown"


def group_products_by_category(
        products: Sequence[dict]
) -> dict[str, int]:
    """
    Groups products by their categories and sums the quantities.

    Parameters
    ----------
    products : Sequence[dict]
        A sequence of dictionaries, where each dictionary represents
        a product with keys 'category' and 'quantity'.

    Returns
    -------
    dict[str, int]: A dictionary where the keys are product categories and the
    values are the total quantities of products in each category.
    """
    grouped = {}
    for product in products:
        category = product.get('category')
        quantity = product.get('quantity')
        grouped[category] = grouped.get(category, 0) + quantity
    return grouped


def extract_products_from_carts(
        carts: Sequence[dict]
) -> list[dict]:
    """
    Extracts products from the carts and returns a list of dictionaries
    in the following format:

    [{'id': ..., 'quantity': ..., 'category': ...}, ...]

    Parameters
    ----------
    carts : Sequence[dict]
        A list representing the user's carts.

    Returns
    -------
    list[dict]: A list of dictionaries, where each dictionary represents
    a product.
    """
    return [product for cart in carts
            for product in extract_products_from_cart(cart)]


def extract_products_from_cart(
        cart: dict
) -> list[dict]:
    """
    Extracts products from the cart and returns a list of dictionaries
    in the following format:

    [{'id': ..., 'quantity': ..., 'category': ...}, ...]

    Parameters
    ----------
    cart : dict
        A dictionary representing the user's cart.

    Returns
    -------
    list[dict]: A list of dictionaries, where each dictionary represents
    a product.
    """
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
