from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from book.views import router as book_router

app = FastAPI(
    title="Book Management System API",
    description="API for managing books, reviews, and recommendations",
    version="1.0.0",
    docs_url="/docs",             
    redoc_url="/redoc",           
    openapi_url="/openapi.json"   
)

app.include_router(book_router, prefix="/api/v1/")











def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Book Management System API",
        version="1.0.0",
        description="This is the API for managing books and reviews",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
