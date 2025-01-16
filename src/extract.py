from collections.abc import Sequence

import httpx

USERS_ENDPOINT = "https://dummyjson.com/users"


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
        Dict[str, str]: A dictionary containing users data.
    """
    try:
        query_params = get_query_params(limit, skip, select)
        resp = httpx.get(USERS_ENDPOINT, params=query_params)
        resp.raise_for_status()
    except ValueError as exc:
        print(exc)
        return
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        return
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting "
              f"{exc.request.url!r}.")
        return
    else:
        return resp.json()


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
