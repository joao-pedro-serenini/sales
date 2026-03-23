"""Fábrica da aplicação."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.controllers.customer_controller import router as customer_router


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI.

    Retorna:
        Uma instância configurada de :class:`fastapi.FastAPI`.
    """
    app = FastAPI(title="Sales API")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": detail},
        )

    app.include_router(customer_router)
    return app
