from services.http_client import safe_http_request
from functools import lru_cache
from core import config
from typing import Any
from core.exceptions import  BadRequestException, ExternalServiceException


@lru_cache
def get_settings():
    return config.Settings()


async def fetch_genderize_property(name: str):
    settings = get_settings()
    
    if settings is None:
        raise BadRequestException("base Url is missing.")
    
    url = settings.genderize_api
    properties: dict[str, Any] = await safe_http_request("GET", f"{url}/?name={name}", timeout=3000)
    
    count = properties["count"]
    name = properties["name"]
    gender = properties["gender"]
    prob = properties["probability"]
    
    if gender == None or count == 0:
        raise ExternalServiceException("Genderize returned an invalid response")
        
    
    data = {
        "name": name,
        "gender": gender,
        "gender_probability": prob,
        "sample_size": count,
    }

    return data
