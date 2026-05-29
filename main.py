from fastapi import FastAPI

app = FastAPI(title="Shopping Cart API", description="API for managing a shopping cart", version="1.0.0")

@app.get("/")
def read_root():
    return {"Hello": "World"}