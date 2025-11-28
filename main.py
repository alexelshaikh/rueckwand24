from fastapi import FastAPI
from contextlib import asynccontextmanager
import sqlalchemy.exc
import asyncio
from core.database_core import engine
from models.db_models.db_base import Base
from api_routes.auth import router as auth_router
from api_routes.users import router as users_router
from api_routes.material import router as material_router
from api_routes.product_types import router as product_type_router
from api_routes.items import router as catalog_router

max_attempts = 16
delay_seconds = 2

@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database connected successfully! :)")
            break
        except sqlalchemy.exc.OperationalError as e:
            print(f"DB is still waking up... (attempt {attempt}/{max_attempts}): {e}")
            if attempt == max_attempts:
                print("DB is too slow or dead!")
                raise
            await asyncio.sleep(delay_seconds)

    yield

app = FastAPI(lifespan=lifespan)


app.include_router(auth_router) # login/logout and token session endpoints
app.include_router(users_router) # user CRUD endpoints
app.include_router(material_router) # material endpoints
app.include_router(product_type_router) # product type endpoints
app.include_router(catalog_router) # catalog (items) endpoints
