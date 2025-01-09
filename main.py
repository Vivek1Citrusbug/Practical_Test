from fastapi import FastAPI,HTTPException
from contextlib import asynccontextmanager
from apps.user.domain.service import create_db_and_tables
from apps.user.interface import user_router as auth_router
from apps.user.middleware import ErrorMiddleware,http_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    for loadiing resources that need to be present before the start of the application
    """

    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(ErrorMiddleware)
app.add_exception_handler(HTTPException,http_exception_handler)

app.include_router(auth_router.router, prefix="/auth")