"""FastAPI application factory (build brief §4 `api/`)."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker

from intel import db as intel_db
from intel_api import auth
from intel_api.routes import briefs, ops, outreach, people
from intel_api.settings import ApiSettings


def create_app(
    api_settings: ApiSettings | None = None,
    session_factory: Callable[[], Session] | sessionmaker | None = None,
    mailer=None,
) -> FastAPI:
    app = FastAPI(title="1440 Intelligence API", version="0.1.0")
    app.state.api_settings = api_settings or ApiSettings.from_env()
    app.state.session_factory = session_factory or intel_db.get_sessionmaker()
    app.state.mailer = mailer

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[app.state.api_settings.origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def db_session(request: Request, call_next):
        session: Session = app.state.session_factory()
        request.state.db = session
        try:
            response = await call_next(request)
            if response.status_code < 400:
                session.commit()
            else:
                session.rollback()
            return response
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @app.get("/health")
    def health() -> dict:
        return {"ok": True}

    app.include_router(auth.router)
    app.include_router(briefs.router)
    app.include_router(people.router)
    app.include_router(outreach.router)
    app.include_router(ops.router)
    return app


app = None  # created lazily by `uvicorn intel_api.app:get_app --factory`


def get_app() -> FastAPI:
    global app
    if app is None:
        app = create_app()
    return app
