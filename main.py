from fastapi import FastAPI,HTTPException
from contextlib import asynccontextmanager
from apps.user.domain.service import create_db_and_tables,create_default_superuser
from apps.user.interface import user_router as auth_router
from apps.posts.interface import post_router as post_router
from apps.custom_admin.interface import custom_admin_router as admin_router
from apps.user.middleware import ErrorMiddleware, ResponseMiddleware,http_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    for loadiing resources that need to be present before the start of the application
    """

    await create_db_and_tables()
    await create_default_superuser()
    yield


app = FastAPI(lifespan=lifespan)

#Middlewares
app.add_middleware(ErrorMiddleware)
app.add_exception_handler(HTTPException,http_exception_handler)
app.add_middleware(ResponseMiddleware)

app.include_router(auth_router.router, prefix="/auth")
app.include_router(post_router.router, prefix="/posts" , tags=["Posts"])
app.include_router(admin_router.router, prefix="/custom_admin" , tags=["Custom Admin"])

