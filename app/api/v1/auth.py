from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schema.user import UserCreate, UserResponse
from app.schema.token import Token
from app.crud.user import user_crud
from app.core.security import create_access_token
from app.config import settings
from app.core.limiter import limiter
from app.core.notifier import send_welcome_email, send_login_notification


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    
    # Check if email already exists
    existing_user = user_crud.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the user
    db_user = user_crud.create(db, user=user)
    db.commit()
    db.refresh(db_user)
    
    background_tasks.add_task(send_welcome_email, user_email=db_user.email, user_name=db_user.name)
    
    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):

    # Authenticate user
    user = user_crud.authenticate(
        db,
        email=form_data.username,  # OAuth2 form uses 'username' field
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    background_tasks.add_task(send_login_notification, user_email=user.email, ip_address=request.client.host)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.value,
        "name": user.name,
        "id": str(user.id)
    }