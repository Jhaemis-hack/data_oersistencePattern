from services.http_client import safe_http_request
from functools import lru_cache
from core import config
from typing import Any
from core.exceptions import  BadRequestException


@lru_cache
def get_settings():
    return config.Settings()


async def fetch_name_properties(name: str):
    settings = get_settings()
    
    if settings is None:
        raise BadRequestException("base Url is missing.")
    
    url = settings.genderize_api
    properties: dict[str, Any] = await safe_http_request("GET", f"{url}/?name={name}", timeout=3000)
    
    count = properties["count"]
    name = properties["name"]
    gender = properties["gender"]
    prob = properties["probability"]
    
    if gender == None and count == 0:
        return {
            "success": False,
            "message": "No prediction available for the provided name"
        }
        
    is_confident = count >=100 and prob >=0.7
    
    data = {
        "success": True,
        "name": name,
        "gender": gender,
        "probability": prob,
        "sample_size": count,
        "is_confident": is_confident,
    }

    return data
