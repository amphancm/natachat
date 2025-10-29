import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from dependency import get_db
from router.auth import get_current_user
from schemas.models import Document, UserAccount

router = APIRouter(prefix="/document", tags=["document"])

BASE_STORAGE_PATH = os.path.abspath(os.path.join("object-storage"))
os.makedirs(BASE_STORAGE_PATH, exist_ok=True)


class DocumentResponse(BaseModel):
    id: int
    fileName: str
    filePath: str

    class Config:
        orm_mode = True


@router.post("/upload", response_model=DocumentResponse)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    username = current_user.username
    user_folder = os.path.join(BASE_STORAGE_PATH, username)
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, file.filename)

    if os.path.exists(file_path):
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' already exists in your storage"
        )

    existing_doc = (
        db.query(Document)
        .filter(Document.username == username, Document.fileName == file.filename)
        .first()
    )
    if existing_doc:
        raise HTTPException(
            status_code=400,
            detail=f"Document record for '{file.filename}' already exists in database"
        )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(
        username=username,
        fileName=file.filename,
        filePath=file_path
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    docs = db.query(Document).filter(Document.username == current_user.username).all()
    return docs


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.username == current_user.username)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
def rename_document(
    doc_id: int,
    new_name: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.username == current_user.username)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    user_folder = os.path.dirname(doc.filePath)
    new_path = os.path.join(user_folder, new_name)
    if os.path.exists(new_path):
        raise HTTPException(
            status_code=400,
            detail=f"A file named '{new_name}' already exists"
        )

    if os.path.exists(doc.filePath):
        os.rename(doc.filePath, new_path)
    else:
        raise HTTPException(status_code=404, detail="File not found on server")

    doc.fileName = new_name
    doc.filePath = new_path
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.username == current_user.username)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.filePath):
        os.remove(doc.filePath)

    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.fileName}' deleted successfully"}
