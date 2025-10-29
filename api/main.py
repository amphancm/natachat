from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from libs.db import init_db
from router import auth, chat, ws_chat, ui, setting, document
from dependency import get_db
from router.auth import get_user, get_password_hash
from schemas.models import UserAccount, Setting
from sqlalchemy.orm import Session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    # Create default user
    db: Session = next(get_db())
    if not get_user(db, "admin"):
        init_setting = Setting()
        db.add(init_setting)
        db.commit()
        db.refresh(init_setting)

        new_user = UserAccount(
            username="admin",
            password=get_password_hash("admin"),
            setting_id=init_setting.id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

# This regex allows requests from localhost, 127.0.0.1, and local IP addresses.
allow_origin_regex = r"http://(localhost|127\.0\.0\.1|192\.168\..*):\d+"

app.add_middleware(
	CORSMiddleware,
	allow_origin_regex=allow_origin_regex,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(ws_chat.router)
app.include_router(ui.router)  
app.include_router(setting.router)
app.include_router(document.router)
