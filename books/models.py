from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()




class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    summary = Column(Text)
    reviews = relationship("Review", back_populates="book")

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    content = Column(Text)
    rating = Column(Integer)

    book = relationship("Book", back_populates="reviews")


class BookSchema(BaseModel):
    title: str = Field(..., example="The Great Gatsby")
    author: str = Field(..., example="F. Scott Fitzgerald")
    summary: str = Field(..., example="A novel about the American dream.")

    class Config:
        orm_mode = True

class ReviewSchema(BaseModel):
    content: str = Field(..., example="An excellent read!")
    rating: int = Field(..., example=5)

    class Config:
        orm_mode = True
