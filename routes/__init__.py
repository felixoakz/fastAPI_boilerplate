from .auth import auth_router
from .users import user_router

all_routes =[
    auth_router,
    user_router,
]
