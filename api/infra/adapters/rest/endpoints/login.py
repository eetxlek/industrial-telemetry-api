from fastapi import APIRouter
from infra.config.security import create_access_token

router = APIRouter()

@router.post("/login")
async def login():
    # Para demo: usuario hardcodeado
    user_data = {"sub": "demo_user", "roles": ["admin"]}
    token = create_access_token(user_data)
    return {"access_token": token, "token_type": "bearer"}


#protege po ejemplo desactivar sensor