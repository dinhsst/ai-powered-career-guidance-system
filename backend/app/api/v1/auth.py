from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.core.security import create_access_token, get_password_hash, verify_password, verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# In-memory store for demo — replace with database in production
fake_users_db: dict = {}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=201)
async def register(request: RegisterRequest):
    if request.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    fake_users_db[request.email] = {
        "email": request.email,
        "full_name": request.full_name,
        "hashed_password": get_password_hash(request.password),
    }
    return {"message": "Đăng ký thành công"}


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    token = create_access_token({"sub": user["email"]})
    return TokenResponse(access_token=token)


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    email = payload.get("sub")
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    return {"email": user["email"], "full_name": user["full_name"]}
