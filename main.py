import re
from collections import Counter
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, Depends, Query
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.error_handlers import register_error_handlers, conditional_validation_handler
from fastapi.exceptions import RequestValidationError
from services.fetch_name_data import fetch_name_properties
from core.exceptions import NotFoundException, BadRequestException, UnprocessableException
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from functools import lru_cache
from typing_extensions import Annotated
from core import config
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("App starting up...")
    await startup_event()
    yield
    # Shutdown
    print("App shutting down...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan, title="My Profile App")
register_error_handlers(app)

# Register exception handlers
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"success": False, "error": "Too many requests, please slow down."},
))
app.add_exception_handler(RequestValidationError, conditional_validation_handler)


@lru_cache
def get_settings():
    return config.Settings()    


# Initialize the limiter
async def startup_event():
    app.state.limiter = limiter


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return JSONResponse(content={
        "success": True,
        "message": {
            "title": "Gender Analyzer",
            "about": "This is a RESTful API service that fetches and anlayze Name based property from genderize.io."
        }
    }, status_code=200, media_type="application/json")


@app.get("/health")
async def health_check():
    return JSONResponse(content={
        "success": True,
        "message": "Ok"
    }, status_code=200, media_type="application/json")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@limiter.limit("8/minute")
@app.get("/api/classify")
async def analyze_string(request: Request, name: Annotated[str, Query(description="Missing or empty name parameter")]):
    query_name = name
    
    if (query_name == ""):
        raise BadRequestException("Missing or empty name parameter")
    
    parsed_query_name = re.sub(r'[^a-zA-Z]', '', query_name).lower()
        
    if (parsed_query_name == ""):
        raise UnprocessableException("name is not a string")
        
    parsed_query_name = query_name.lower()

    props = await fetch_name_properties(parsed_query_name)
    
    if props["success"] == False:
        raise NotFoundException(props["message"])
    
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    data = {
        "status": "success",
        "data": {
            "name": props["name"],
            "gender": props["gender"],
            "probability": props["probability"],
            "sample_size": props["sample_size"],
            "is_confident": props["is_confident"],
            "processed_at": now_iso
        }
    }

    return JSONResponse(content=data, status_code=200, media_type="application/json")