from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse

from database import SessionLocal, engine, Base

from models.user_model import User
from models.document_model import Document

from schemas.user_schema import UserCreate, UserLogin

from services.pdf_service import (
    extract_text_from_pdf,
    create_chunks
)

from services.embedding_service import (
    store_embeddings,
    search_query
)

from services.auth_service import create_access_token

import shutil

app = FastAPI()

Base.metadata.create_all(bind=engine)


# ===================================
# HOME PAGE
# ===================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """

    <html>

    <head>

        <title>
        Financial Document Management
        </title>

    </head>

    <body style="
        font-family: Arial;
        text-align:center;
        margin-top:100px;
        background-color:#f4f4f4;
    ">

        <div style="
            background:white;
            width:60%;
            margin:auto;
            padding:40px;
            border-radius:10px;
            box-shadow:0px 0px 10px lightgray;
        ">

            <h1 style="color:#333;">
                Financial Document Management System
            </h1>

            <p style="
                font-size:18px;
                color:gray;
            ">

                AI-powered Financial Document
                Analysis using RAG, FastAPI,
                JWT Authentication and RBAC.

            </p>

            <br>

            <a href="/docs">

                <button style="
                    padding:15px 25px;
                    font-size:18px;
                    background-color:#007bff;
                    color:white;
                    border:none;
                    border-radius:8px;
                    cursor:pointer;
                ">

                    Open API Documentation

                </button>

            </a>

        </div>

    </body>

    </html>

    """


# ===================================
# REGISTER
# ===================================

@app.post("/register")
def register(user: UserCreate):

    db = SessionLocal()

    new_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


# ===================================
# LOGIN
# ===================================

@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if existing_user.password != user.password:

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token(
        data={"sub": existing_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ===================================
# UPLOAD DOCUMENT
# ===================================

@app.post("/upload-document")
def upload_document(
    title: str,
    company_name: str,
    document_type: str,
    file: UploadFile = File(...)
):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()

    new_document = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_path
    )

    db.add(new_document)

    db.commit()

    db.refresh(new_document)

    return {
        "message": "Document uploaded successfully"
    }


# ===================================
# EXTRACT TEXT
# ===================================

@app.get("/extract-text/{file_name}")
def extract_text(file_name: str):

    file_path = f"uploads/{file_name}"

    text = extract_text_from_pdf(file_path)

    return {
        "text": text
    }


# ===================================
# CREATE CHUNKS
# ===================================

@app.get("/create-chunks/{file_name}")
def chunk_text(file_name: str):

    file_path = f"uploads/{file_name}"

    text = extract_text_from_pdf(file_path)

    chunks = create_chunks(text)

    return {
        "chunks": chunks
    }


# ===================================
# STORE EMBEDDINGS
# ===================================

@app.get("/store-embeddings/{file_name}")
def generate_embeddings(file_name: str):

    file_path = f"uploads/{file_name}"

    text = extract_text_from_pdf(file_path)

    chunks = create_chunks(text)

    result = store_embeddings(chunks)

    return {
        "message": result
    }


# ===================================
# RAG SEARCH
# ===================================

@app.post("/rag/search")
def semantic_search(query: str):

    result = search_query(query)

    return {
        "query": query,
        "result": result
    }


# ===================================
# GET DOCUMENTS
# ===================================

@app.get("/documents")
def get_documents():

    db = SessionLocal()

    documents = db.query(Document).all()

    return documents


# ===================================
# DELETE DOCUMENT
# ===================================

@app.delete("/documents/{document_id}")
def delete_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:

        return {
            "message": "Document not found"
        }

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully"
    }


# ===================================
# RBAC PERMISSIONS
# ===================================

@app.get("/users/{email}/permissions")
def get_permissions(email: str):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    permissions = {

        "Admin": "Full access",

        "Financial Analyst":
        "Upload and edit documents",

        "Auditor":
        "Review documents",

        "Client":
        "View company documents"
    }

    return {
        "role": user.role,
        "permission": permissions.get(user.role)
    }


# ===================================
# GET USERS
# ===================================

@app.get("/users")
def get_users():

    db = SessionLocal()

    users = db.query(User).all()

    return users