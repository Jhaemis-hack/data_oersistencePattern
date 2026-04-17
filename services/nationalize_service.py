from services.http_client import safe_http_request
from functools import lru_cache
from core import config
from typing import Any
from core.exceptions import  BadRequestException, ExternalServiceException


@lru_cache
def get_settings():
    return config.Settings()


async def fetch_nationalize_property(name: str):
    settings = get_settings()
    
    if settings is None:
        raise BadRequestException("base Url is missing.")
    
    url = settings.nationalize_api
    response: dict[str, Any] = await safe_http_request("GET", f"{url}/?name={name}", timeout=3000)
    
    countries = response["country"]
    country_id = ""
    highest_prob = 0
    
    if len(countries) < 1:
        raise ExternalServiceException("Nationalize returned an invalid response")
    
    for country in countries:
        id: str = country["country_id"]
        prob: int = country["probability"]
        
        if highest_prob < prob:
            highest_prob = prob
            country_id = id
    
    data = {
        "country_id": country_id,
        "country_probability": highest_prob,
    }

    return data
