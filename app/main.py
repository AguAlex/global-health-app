from fastapi import FastAPI

app = FastAPI(title="Global Health Data Platform API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Global Health Data Platform API is running!"}