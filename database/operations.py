from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from database.models import Book, Review
from typing import List
import aioredis



redis = aioredis.from_url("redis://ip:<port>", decode_responses=True)


async def create_book(db: AsyncSession, book_data: dict) -> Book:
    new_book = Book(**book_data)
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

async def get_books(db: AsyncSession) -> List[Book]:
    result = await db.execute(select(Book))
    return result.scalars().all()

async def get_book(db: AsyncSession, book_id: int) -> Book:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalars().one_or_none()

async def update_book(db: AsyncSession, book_id: int, book_data: dict) -> Book:
    book = await get_book(db, book_id)
    if not book:
        raise NoResultFound(f"Book with id {book_id} not found.")
    
    for key, value in book_data.items():
        setattr(book, key, value)

    await db.commit()
    return book

async def delete_book(db: AsyncSession, book_id: int) -> None:
    book = await get_book(db, book_id)
    if not book:
        raise NoResultFound(f"Book with id {book_id} not found.")
    
    await db.delete(book)
    await db.commit()


async def create_review(db: AsyncSession, book_id: int, review_data: dict) -> Review:
    new_review = Review(**review_data, book_id=book_id)
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review

async def get_reviews(db: AsyncSession, book_id: int) -> List[Review]:
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    return result.scalars().all()






async def calculate_user_recommendations(db: AsyncSession, user_id: int, genre_preference: str) -> List[Book]:
    """
    Calculate book recommendations for a user based on their genre preferences and reviews,
    with caching support.

    Args:
        db: AsyncSession instance for database operations.
        user_id: ID of the user requesting recommendations.
        genre_preference: Genre preference for filtering recommendations.

    Returns:
        A list of recommended Book instances.
    """

    
    cache_key = f"user:{user_id}:recommendations:{genre_preference}"
    cached_recommendations = await redis.get(cache_key)
    
    if cached_recommendations:
        return eval(cached_recommendations)  

  
    recommendations = await db.execute(
        select(Book)
        .join(Review)
        .where(Book.genre == genre_preference)
        .group_by(Book.id)
        .having(func.avg(Review.rating) >= 4.0)  
    )

    recommendations_list = recommendations.scalars().all()

    
    await redis.set(cache_key, str(recommendations_list), ex=3600)

    return recommendations_list

async def get_user_reviews(db: AsyncSession, user_id: int) -> List[Review]:
    """
    Get reviews written by a specific user.
    
    Args:
        db: AsyncSession instance for database operations.
        user_id: ID of the user whose reviews we want to fetch.
        
    Returns:
        A list of Review instances written by the user.
    """
    result = await db.execute(select(Review).where(Review.user_id == user_id))
    return result.scalars().all()
