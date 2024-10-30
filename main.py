from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import users, auth


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

app.include_router(users.router)
app.include_router(auth.router)
