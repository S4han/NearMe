from fastapi import FastAPI

app = FastAPI(title="NearMe Backend", version="1.0.0")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "NearMe Backend"}
