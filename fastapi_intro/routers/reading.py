from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import models
from database import get_db
from schemas import ReadingResponse, ReadingCreate, ReadingUpdate

router = APIRouter()

@router.get("", response_model=list[ReadingResponse])
async def get_sensor_readings(reading: ReadingCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Reading).options(selectinload(models.Reading.author)))
    sensor_readings = result.scalars().all()
    return sensor_readings


@router.get("/{sensor_reading_id}", response_model=ReadingResponse)
async def get_sensor_reading(sensor_reading_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Reading).where(models.Reading.id == sensor_reading_id).options(selectinload(models.Reading.author)))
    reading = result.scalars().first()
    if reading:
        return reading
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor reading not found")

@router.post("", response_model=ReadingResponse, status_code = status.HTTP_201_CREATED)
async def create_reading(reading: ReadingCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == reading.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_reading = models.Reading(
        sensor = reading.sensor,
        content = reading.content,
        user_id = reading.user_id
    )
    db.add(new_reading)
    await db.commit()
    await db.refresh(new_reading, attribute_names=["author"])
    return new_reading


@router.put("/{reading_id}", response_model = ReadingResponse)
async def update_reading_full(
    reading_id: int,
    reading_data: ReadingCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Reading).where(models.Reading.id == reading_id))
    reading = result.scalars().first()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")
    if reading_data.user_id != reading.user_id:
        result = await db.execute(select(models.User).where(models.User.id == reading_data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    reading.sensor = reading_data.sensor
    reading.content = reading_data.content
    reading.user_id = reading_data.user_id
    await db.commit()
    await db.refresh(reading, attribute_names=["author"])
    return reading


@router.patch("/{reading_id}", response_model=ReadingResponse)
async def update_reading_partial(
    reading_id: int, 
    reading_data: ReadingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Reading).where(models.Reading.id == reading_id))
    reading = result.scalars().first()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")
    update_data = reading_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reading, field, value)
    await db.commit()
    await db.refresh(reading, attribute_names=["author"])
    return reading


@router.delete("/{reading_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_reading(reading_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Reading).where(models.Reading.id == reading_id))
    reading = result.scalars().first()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")
    await db.delete(reading)
    await db.commit()