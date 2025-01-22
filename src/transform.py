import logging.config
from collections.abc import Mapping, Sequence
from typing import Any

from config.config import LOG_FILE_PATH, LOGGING_CONFIG_FILE
from src.extract import (
    get_product_category,
    get_user_carts,
    get_user_country,
)

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def get_user_data(
        user: Mapping[str, Any]
) -> dict[str, Any]:
    """
    Get user data with additional information.

    Parameters
    ----------
    user : Mapping[str, Any]
        Dictionary containing user information.

    Returns
    -------
    dict[str, Any]
        User data with added details.
    """
    user_id = user.get("id")
    if not user_id:
        logger.error("User ID is missing.")
        raise ValueError("User ID is missing.")

    first_name = user.get("firstName")
    last_name = user.get("lastName")
    age = user.get("age")
    gender = user.get("gender")

    coordinates = user.get("address", {}).get("coordinates", {})
    lat = coordinates.get("lat")
    lng = coordinates.get("lng")
    country = get_user_country(lat, lng) if lat and lng else None

    carts = get_user_carts(user_id).get("carts", [])
    products = extract_products_from_carts(carts)
    grouped_products = group_products_by_category(products)
    favorite_category = get_most_common_category(grouped_products)

    return {
        "firstName": first_name,
        "lastName": last_name,
        "age": age,
        "gender": gender,
        "country": country,
        "faveCategory": favorite_category
    }


def get_most_common_category(
       products: Mapping[str, int]
) -> str | None:
    """
    Get the category with the highest quantity.

    Parameters
    ----------
    products : Mapping[str, int]
        A dictionary where the keys are product categories and the
        values are the total quantities of products in each category.

    Returns
    -------
    str
        The category with the highest quantity.
    """
    return max(products, key=products.get) if products else None


def group_products_by_category(
        products: Sequence[Mapping[str, Any]]
) -> dict[str, int]:
    """
    Group products by their categories and sums the quantities.

    Parameters
    ----------
    products : Sequence[Mapping[str, Any]]
        A sequence of dictionaries, where each dictionary
        represents a product with keys 'category' and 'quantity'.

    Returns
    -------
    dict[str, int]
        A dictionary where the keys are product categories
        and the values are the total quantities
        of products in each category.
    """
    grouped = {}
    for product in products:
        category = product.get("category")
        quantity = product.get("quantity")
        grouped[category] = grouped.get(category, 0) + quantity
    return grouped


def extract_products_from_carts(
        carts: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """
    Extract products from the carts.

    Return products in the following format:
    [{'id': ..., 'quantity': ..., 'category': ...}, ...]

    Parameters
    ----------
    carts : Sequence[Mapping[str, Any]]
        A sequence representing the user's carts.

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries, where each dictionary
        represents a product.
    """
    return [product for cart in carts
            for product in extract_products_from_cart(cart)]


def extract_products_from_cart(
        cart: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """
    Extract products from the cart.

    Return products in following format:
    [{'id': ..., 'quantity': ..., 'category': ...}, ...]

    Parameters
    ----------
    cart : Mapping[str, Any]
        A dictionary representing the user's cart.

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries, where
        each dictionary represents a product.
    """
    products = cart.get("products")
    result = []

    for product in products:
        product_id = product.get("id")
        product_category = get_product_category(product_id)
        result.append({
            "id": product_id,
            "quantity": product.get("quantity"),
            "category": product_category
        })

    return result
