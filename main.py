import re
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from core.error_handlers import register_error_handlers, validation_error_handler
from services.genderize_service import fetch_genderize_property
from services.agify_service import fetch_Agify_property
from services.nationalize_service import fetch_nationalize_property
from core.exceptions import NotFoundException, BadRequestException, UnprocessableException
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from functools import lru_cache
from core import config
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from config.database import collection
from config.model import extract_gender, create_profile, create_profile_list_item
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.limiter = limiter
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan, title="Classification App")
register_error_handlers(app)

app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"status": "error", "message": "Too many requests, please slow down."},
))


@lru_cache
def get_settings():
    return config.Settings()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Payload(BaseModel):
    name: str = Field(..., description="A non-empty string value")


@app.get("/")
async def home():
    return JSONResponse(content={
        "status": "success",
        "message": {
            "title": "Classification App",
            "about": "A RESTful API that predicts gender, age, and nationality from a name.",
        }
    }, status_code=200)


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "success", "message": "Ok"}, status_code=200)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@limiter.limit("8/minute")
@app.post("/api/profiles")
async def create_new_profile(request: Request, body: Payload):
    profile_name = body.name

    if profile_name == "":
        raise BadRequestException("Missing or empty name")

    parsed_name = re.sub(r'[^a-zA-Z]', '', profile_name).lower()

    if parsed_name == "":
        raise UnprocessableException("name is not a string")

    existing = collection.find_one({"name": parsed_name})
    if existing:
        return JSONResponse(content={
            "status": "success",
            "message": "Profile already exists",
            "data": create_profile(existing),
        }, status_code=200)

    genderize_response, nationalize_response, agify_response = await asyncio.gather(
        fetch_genderize_property(parsed_name),
        fetch_nationalize_property(parsed_name),
        fetch_Agify_property(parsed_name),
    )

    profile_id = str(uuid.uuid7())
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    doc = {
        "id": profile_id,
        **extract_gender(genderize_response, nationalize_response, agify_response),
        "created_at": created_at,
    }

    collection.insert_one(doc)

    return JSONResponse(content={
        "status": "success",
        "data": create_profile(doc),
    }, status_code=201)


@app.get("/api/profiles")
async def get_all_profiles(
    gender: str | None = Query(default=None),
    country_id: str | None = Query(default=None),
    age_group: str | None = Query(default=None),
):
    query = {}
    if gender:
        query["gender"] = gender.lower()
    if country_id:
        query["country_id"] = country_id.upper()
    if age_group:
        query["age_group"] = age_group.lower()

    docs = list(collection.find(query))
    return JSONResponse(content={
        "status": "success",
        "count": len(docs),
        "data": [create_profile_list_item(d) for d in docs],
    }, status_code=200)


@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str):
    doc = collection.find_one({"id": profile_id})
    if not doc:
        raise NotFoundException("Profile not found")
    return JSONResponse(content={
        "status": "success",
        "data": create_profile(doc),
    }, status_code=200)


@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    result = collection.delete_one({"id": profile_id})
    if result.deleted_count == 0:
        raise NotFoundException("Profile not found")
    return Response(status_code=204)
