from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from database.operations import Book, Review
from book.models import BookSchema, ReviewSchema
from database.db import get_db
import datetime

router = APIRouter()

class DefaultResponse(BaseModel):
    success: bool = Field(True, description="Return success if request processed successfully", example=True)
    currentDT: str = Field(datetime.datetime.utcnow().isoformat(), example=datetime.datetime.utcnow().isoformat(), description="Return current date with time")
    resultBody: Optional[Dict] = Field({}, example={"ABCD": "ABC", "ED": "EIK"})
    serverIp: str = Field("127.0.0.1", example="127.0.0.1", description="Return server IP address")
    message: Optional[str] = Field(None, example="This is a message", description="Return message response from API")
    environment: str = Field("development", example="development")
    roleName: str = Field("book_management", example="book_management")

@router.post("/books", response_model=DefaultResponse)
async def create_book(book: BookSchema, db: AsyncSession = Depends(get_db)):
    new_book = Book(**book.dict())
    db.add(new_book)
    await db.commit()
    return DefaultResponse(message="Book created successfully", resultBody={"book": book})

@router.get("/books", response_model=DefaultResponse)
async def get_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return DefaultResponse(resultBody={"books": books})

@router.get("/books/{book_id}", response_model=DefaultResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return DefaultResponse(resultBody={"book": book})

@router.put("/books/{book_id}", response_model=DefaultResponse)
async def update_book(book_id: int, book: BookSchema, db: AsyncSession = Depends(get_db)):
    existing_book = await db.get(Book, book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book.dict().items():
        setattr(existing_book, key, value)
    
    await db.commit()
    return DefaultResponse(message="Book updated successfully", resultBody={"book": existing_book})

@router.delete("/books/{book_id}", response_model=DefaultResponse)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(book)
    await db.commit()
    return DefaultResponse(message="Book deleted successfully")

@router.post("/books/{book_id}/reviews", response_model=DefaultResponse)
async def create_review(book_id: int, review: ReviewSchema, db: AsyncSession = Depends(get_db)):
    new_review = Review(**review.dict(), book_id=book_id)
    db.add(new_review)
    await db.commit()
    return DefaultResponse(message="Review added successfully")

@router.get("/books/{book_id}/reviews", response_model=DefaultResponse)
async def get_reviews(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    reviews = result.scalars().all()
    return DefaultResponse(resultBody={"reviews": reviews})

@router.get("/books/{book_id}/summary", response_model=DefaultResponse)
async def get_summary(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")


    summary = generate_summary_with_llama3(book.summary)
    return DefaultResponse(resultBody={"book_summary": summary})

@router.get("/recommendations", response_model=DefaultResponse)
async def get_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    
    recommendations = calculate_user_recommendations(user_id)
    return DefaultResponse(resultBody={"recommendations": recommendations})

@router.post("/generate-summary", response_model=DefaultResponse)
async def generate_summary(content: str):
    summary = generate_summary_with_llama3(content)
    return DefaultResponse(resultBody={"summary": summary})

