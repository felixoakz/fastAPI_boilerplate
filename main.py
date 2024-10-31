from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import all_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        # "http://localhost:8000",
        # "https://your-production-url.com",
    ],
)

for route in all_routes:
    app.inglude_router(route)
