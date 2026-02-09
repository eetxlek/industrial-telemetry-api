"""
Utilidades de seguridad y autenticación
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.infra.config import settings


# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticación Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera hash de una contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración (opcional)
        
    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verifica un token JWT
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Datos decodificados o None si el token es inválido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency para obtener el usuario actual desde el token
    
    Args:
        credentials: Credenciales de autenticación
        
    Returns:
        Datos del usuario
        
    Raises:
        HTTPException: Si el token es inválido
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def is_authorized_user(user: dict, required_roles: Optional[list] = None) -> bool:
    """
    Verifica si un usuario tiene los roles necesarios
    
    Args:
        user: Datos del usuario
        required_roles: Roles requeridos (opcional)
        
    Returns:
        True si está autorizado
    """
    if required_roles is None:
        return True
    
    user_roles = user.get("roles", [])
    return any(role in user_roles for role in required_roles)


# Para uso en endpoints que requieren autenticación
def require_auth(required_roles: Optional[list] = None):
    """
    Decorador/función para requerir autenticación
    
    Args:
        required_roles: Roles requeridos (opcional)
        
    Returns:
        Dependency que verifica autenticación y autorización
    """
    async def dependency(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        if not is_authorized_user(current_user, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes"
            )
        return current_user
    
    return dependency