import uvicorn
from fastapi import FastAPI

from src.routers.main import router as main_router
from src.start_app import lifespan
from src.utils.common import get_app_version

app_version = get_app_version()

app = FastAPI(title="Warehouse API", lifespan=lifespan, version=app_version, root_path="/api")

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
