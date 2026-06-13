from fastapi import HTTPException, status, Request
from src.user.dtos import UserDTO, loginDTO
from sqlalchemy.orm import Session
from src.user.models import UserModel
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

password_hash = PasswordHash.recommended()

def get_hased_password(password):
    return password_hash.hash(password)
def verify_password(password, hashedPassword):
    return password_hash.verify(password, hashedPassword)

def register(body: UserDTO, db: Session): 
    ## 1. username validation
    is_user = db.query(UserModel).filter(UserModel.username == body.username).first()
    is_email = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(400, detail="Username already exists..")
    ## 2. Email validation
    if is_email:
        raise HTTPException(400, detail="Email already exists..")
    ## Password hashing
    hashed_password = get_hased_password(body.password)

    ## new user
    new_user = UserModel(
        name = body.name,
        username = body.username,
        hash_password = hashed_password,
        email = body.email ,
        mobile_number = body.mobile
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def loginUser(body: loginDTO, db: Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please enter valid email!")
    is_verified = verify_password(body.password, user.hash_password)
    if not is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Password, Please try again!")
    
    exp_time = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token = jwt.encode({"_id": user.id, "email": user.email, "exp": exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)
    return {"token": token}

def is_authenticated(req: Request, db: Session):
    token = req.headers.get("Authorization")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = token.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_email = payload.get("email")

        user = (
            db.query(UserModel)
            .filter(UserModel.email == user_email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )