import logging.config
from collections.abc import Sequence
from functools import partial
from typing import Any

import backoff
import httpx
from geopy.geocoders import Nominatim

from config.config import (
    LOG_FILE_PATH,
    LOGGING_CONFIG_FILE,
    PRODUCTS_ENDPOINT,
    USER_CARTS_ENDPOINT,
    USERS_ENDPOINT,
)

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")

def get_users(
        limit: int = 30,
        skip: int = 0,
        select: Sequence[str] = None
) -> list[dict[str, Any]]:
    """
    Get users data from the USERS_ENDPOINT.

    Parameters
    ----------
    limit : int
        The maximum number of items to get.
    skip : int
        The number of items to skip.
    select : Sequence[str]
        A sequence of fields to select specific user data.

    Returns
    -------
        list: A list containing users data.
    """
    try:
        query_params = get_query_params(limit, skip, select)
        resp = httpx.get(USERS_ENDPOINT, params=query_params)
        resp.raise_for_status()
    except ValueError:
        logger.error("Both 'limit' and 'skip' must be non-negative integers.")
    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
    else:
        return resp.json().get("users", [])


def get_user_carts(
        user_id: int
) -> dict:
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
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
    else:
        return resp.json()

def get_product_category(
        product_id: int
) -> str:
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
    query_params = {"select": "category"}
    try:
        resp = httpx.get(url, params=query_params)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} "
            f"while requesting {exc.request.url!r}.")
    else:
        return resp.json().get("category")

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
    select : Sequence[str] | None
        A sequence of fields to select specific user data.

    Returns
    -------
        dict[str, str]: A dictionary of query parameters.
    """
    if limit < 0 or skip < 0:
        raise ValueError(
            "Both 'limit' and 'skip' must be non-negative integers.")

    params = {"limit": limit, "skip": skip}
    if select:
        params["select"] = ','.join(select)

    return params

@backoff.on_exception(backoff.expo,
                      TimeoutError,
                      max_tries=3,
                      logger=logger)
def get_user_country(
        latitude: float,
        longitude: float
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
    location = None
    geolocator = Nominatim(user_agent="simple-etl")
    reverse = partial(geolocator.reverse, language="en")

    try:
        location = reverse((latitude, longitude))
    except TimeoutError:
        logger.error(
            "The call to the geocoding service was aborted because "
            "no response has been received.")
    except Exception as exc:
        logger.error("Locating the user failed:", exc)

    if not location:
        logger.warning(
            f"No location found for 'lat': {latitude}, 'lng': {longitude})")
        return

    return location.raw.get("address", {}).get("country")
