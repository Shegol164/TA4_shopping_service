from pydantic import BaseModel, EmailStr, validator
import re

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Phone must start with +7 and contain 10 digits')
        return v

class UserCreate(UserBase):
    password: str
    password_confirm: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.match(r'^[a-zA-Z]', v):
            raise ValueError('Password must contain only latin characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[$%&!:]', v):
            raise ValueError('Password must contain at least one special character ($%&!:)')
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    login: str  # email or phone
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None