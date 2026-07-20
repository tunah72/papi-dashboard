"""Entrypoint FastAPI local: ``uvicorn server.main:app --host 127.0.0.1 --port 8000``."""
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server import services
from server.schemas import (
    DimensionsResponse, DynamicsResponse, ErrorResponse, GeojsonResponse,
    MetadataResponse, OverviewResponse, ProvincesResponse, TrendsResponse,
)

Scale = Literal["six", "eight"]


def create_app() -> FastAPI:
    app = FastAPI(title="PAPI Dashboard Local API", version="1.0.0", description="Dashboard data API Phase 1; chưa có AI/executor HTTP.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=False, allow_methods=["GET"], allow_headers=["*"],
    )

    @app.exception_handler(services.ContractError)
    async def contract_error(_: Request, exc: services.ContractError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        fields = {".".join(str(part) for part in item["loc"][1:]): "Giá trị không hợp lệ." for item in exc.errors()}
        return JSONResponse(status_code=422, content={"detail": "Tham số truy vấn không hợp lệ.", "fields": fields})

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok", "service": "papi-local-api", "bindTarget": "127.0.0.1"}

    @app.get("/api/v1/metadata", response_model=MetadataResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_metadata(): return services.metadata()

    @app.get("/api/v1/geojson", response_model=GeojsonResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_geojson(): return services.geojson()

    @app.get("/api/v1/overview", response_model=OverviewResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_overview(scale: Scale = "six", year: int | None = None): return services.overview(scale, year)

    @app.get("/api/v1/trends", response_model=TrendsResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_trends(
        scale: Scale = "six",
        from_: Annotated[int | None, Query(alias="from")] = None,
        to: int | None = None,
    ): return services.trends(scale, from_, to)

    @app.get("/api/v1/provinces", response_model=ProvincesResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_provinces(scale: Scale = "six", year: int | None = None, region: str | None = None, province: str | None = None): return services.provinces(scale, year, region, province)

    @app.get("/api/v1/dimensions", response_model=DimensionsResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_dimensions(scale: Scale = "six", year: int | None = None, x: str | None = None, y: str | None = None): return services.dimensions_view(scale, year, x, y)

    @app.get("/api/v1/dynamics", response_model=DynamicsResponse, responses={422: {"model": ErrorResponse}}, tags=["dashboard"])
    def get_dynamics(
        scale: Scale = "six",
        from_: Annotated[int | None, Query(alias="from")] = None,
        to: int | None = None,
    ): return services.dynamics_view(scale, from_, to)

    return app


app = create_app()
