from config.config import USERS_ENDPOINT
from src.extract import get_users


def test_get_users_default(httpx_mock):
    httpx_mock.add_response(
        url=f"{USERS_ENDPOINT}?limit=1&skip=0",
        json={"users": [{"name": "Michael"}]},
    )
    result = get_users(1, 0)
    assert result == [{"name": "Michael"}]

def test_get_users_error_status_code(httpx_mock):
    httpx_mock.add_response(
        url=f"{USERS_ENDPOINT}?limit=1&skip=0",
        status_code=404
    )
    result = get_users(1, 0)
    assert result is None
