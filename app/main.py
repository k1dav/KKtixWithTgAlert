from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

from .core.config import (ALLOWED_HOSTS, API_PREFIX, DEBUG,
                          POSTGRES_CONNECTION, PROJECT_NAME, VERSION)
from .core.events import create_start_app_handler, create_stop_app_handler
from .router import router as api_router

# NOTE: 架構參考：https://github.com/nsidnev/fastapi-realworld-example-app


def get_application(uri: str = POSTGRES_CONNECTION) -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    application.add_event_handler("startup", create_start_app_handler(application, uri))
    application.add_event_handler("shutdown", create_stop_app_handler(application))
    application.include_router(api_router, prefix=API_PREFIX)
    return application


app = get_application()
