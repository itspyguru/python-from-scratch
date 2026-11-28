from fastapi import FastAPI

from .database import Base, engine
from .routers import accounts, auth, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="pyGuru Bank")

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/")
def home():
    return {"message": "pyGuru Bank is running"}
