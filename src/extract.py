import logging.config
import os
from collections.abc import Sequence
from functools import partial
from geopy.geocoders import Nominatim

import httpx

USERS_ENDPOINT = "https://dummyjson.com/users"
USER_CARTS_ENDPOINT = "https://dummyjson.com/carts/user"
PRODUCTS_ENDPOINT = "https://dummyjson.com/products"

log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
)
logging.config.fileConfig(
    "config/logging.conf",
    defaults={"logfilename": repr(log_file_path)}
)
logger = logging.getLogger("logger_file")

def get_users(
        limit: int = 30,
        skip: int = 0,
        select: Sequence[str] | None = None
) -> dict | None:
    """
    Get users data from the USERS_ENDPOINT.

    Parameters
    ----------
    limit : int
        The maximum number of items to get.
    skip : int
        The number of items to skip.
    select : Optional[Sequence[str]]
        A sequence of fields to select specific user data.

    Returns
    -------
        dict: A dictionary containing users data.
    """
    try:
        query_params = get_query_params(limit, skip, select)
        resp = httpx.get(USERS_ENDPOINT, params=query_params)
        resp.raise_for_status()
    except ValueError as exc:
        logger.error(exc)
        return
    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting {exc.request.url!r}.")
        return
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
        return
    else:
        return resp.json()


def get_user_carts(
        user_id: int
) -> dict | None:
    """
    Get user carts from the USER_CARTS_ENDPOINT.

    Parameters
    ----------
    user_id : int
        The unique id of the user.

    Returns
    -------
        dict: A dictionary containing user carts data.
    """
    url = f"{USER_CARTS_ENDPOINT}/{user_id}"
    try:
        resp = httpx.get(url)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting {exc.request.url!r}.")
        return
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
        return
    else:
        return resp.json()

def get_product_category(
        product_id: int
) -> str | None:
    """
    Get product category from the PRODUCTS_ENDPOINT.

    Parameters
    ----------
    product_id : int
        The unique id of the product.

    Returns
    -------
        str: The category of the product.
    """
    url = f"{PRODUCTS_ENDPOINT}/{product_id}"
    query_params = {'select': 'category'}
    try:
        resp = httpx.get(url, params=query_params)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting {exc.request.url!r}.")
        return
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
        return
    else:
        return resp.json().get('category')

def get_query_params(
        limit: int,
        skip: int,
        select: Sequence[str] | None
) -> dict[str, str]:
    """
    Generate a dictionary of query parameters.

    Parameters
    ----------
    limit : int
        The maximum number of items to get.
    skip : int
        The number of items to skip.
    select : Optional[Sequence[str]]
        A sequence of fields to select specific user data.

    Returns
    -------
        Dict[str, str]: A dictionary of query parameters.
    """
    if limit < 0 or skip < 0:
        raise ValueError(
            "Both 'limit' and 'skip' must be non-negative integers.")

    params = {
        'limit': limit,
        'skip': skip
    }

    if select:
        params['select'] = ','.join(select)

    return params

def get_user_country(
        latitude,
        longitude
) -> str | None:
    """
    Get the user's country based on coordinates.

    Parameters
    ----------
    latitude : float
        The latitude where the user is located.
    longitude : float
        The longitude where the user is located.

    Returns
    -------
        str: User country.
    """
    geolocator = Nominatim(user_agent="simple-etl")
    reverse = partial(geolocator.reverse, language="en")

    try:
        location = reverse((latitude, longitude))
    except TimeoutError as exc:
        logger.error(exc)
        return

    if  not location:
        logger.warning(
            f"No location found for 'lat': {latitude}, 'lng': {longitude})")
        return

    return location.raw.get('address', {}).get('country')
