from fastapi import FastAPI

app = FastAPI(title="Better Cotton Exercise API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Better Cotton Exercise API!"}
