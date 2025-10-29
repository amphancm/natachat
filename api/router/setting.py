from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.models import UserAccount, Setting
from router.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from dependency import get_db

router = APIRouter(prefix="/setting", tags=["setting"])

class SettingModel(BaseModel):
    isLocal: Optional[bool] = True
    isApi: Optional[bool] = False
    domainName: Optional[str] = None         
    apiKey: Optional[str] = None
    modelName: Optional[str] = None
    temperature: Optional[float] = 0.7
    systemPrompt: Optional[str] = None

    class Config:
        orm_mode = True

@router.get("/", response_model=SettingModel)
def get_setting(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    if not current_user.setting_id:
        raise HTTPException(status_code=404, detail="No setting assigned to this user")
    setting = db.query(Setting).filter(Setting.id == current_user.setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found in DB")
    return setting

@router.post("/", response_model=SettingModel)
def create_setting(
    setting_data: SettingModel,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    if current_user.setting_id:
        raise HTTPException(status_code=400, detail="User already has a setting")

    new_setting = Setting(**setting_data.dict())
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    current_user.setting_id = new_setting.id
    db.commit()
    return new_setting

@router.put("/", response_model=SettingModel)
def update_setting(
    setting_data: SettingModel,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    setting = db.query(Setting).filter(Setting.id == current_user.setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    update_data = setting_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(setting, key, value)
    db.commit()
    db.refresh(setting)
    return setting

@router.delete("/")
def delete_setting(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    setting = db.query(Setting).filter(Setting.id == current_user.setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    current_user.setting_id = None
    db.commit()
    return {"message": "Setting deleted successfully"}
