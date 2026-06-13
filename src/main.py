from fastapi import FastAPI
from src.utils.db import Base, engine
from src.user.routers import user_routers

Base.metadata.create_all(engine)
app = FastAPI()

app.include_router(user_routers)





