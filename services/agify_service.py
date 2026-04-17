from services.http_client import safe_http_request
from functools import lru_cache
from core import config
from typing import Any
from core.exceptions import  BadRequestException, ExternalServiceException


@lru_cache
def get_settings():
    return config.Settings()


async def fetch_Agify_property(name: str):
    settings = get_settings()
    
    if settings is None:
        raise BadRequestException("base Url is missing.")
    
    url = settings.agify_api
    response: dict[str, Any] = await safe_http_request("GET", f"{url}/?name={name}", timeout=3000)
    

    age = response["age"]
    age_group = ""
    
    if age == None or age < 0:
       raise ExternalServiceException("Agify returned an invalid response")
   
    AGE_GROUP_CHILD = 12
    AGE_GROUP_TEENAGE = 19
    AGE_GROUP_ADULT = 59
    
    if age <= AGE_GROUP_CHILD:
        age_group = "child"
    elif AGE_GROUP_CHILD < age <= AGE_GROUP_TEENAGE:
        age_group = "teenager"
    elif AGE_GROUP_TEENAGE < age <= AGE_GROUP_ADULT:
        age_group = "adult"
    else:
        age_group = "senior"    
    
    
    data = {
        "age": age,
        "age_group": age_group,
    }

    return data
