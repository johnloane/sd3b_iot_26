from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db
from contextlib import asynccontextmanager
from fastapi.exception_handlers import (http_exception_handler, request_validation_exception_handler)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from routers import user, reading


@asynccontextmanager
async def lifespan(_app : FastAPI):
    #Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(reading.router, prefix="/api/reading", tags=["reading"])


@app.get("/",  include_in_schema=False, name="home")
@app.get("/sensor_readings", include_in_schema=False, name="sensor_readings")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Reading).options(selectinload(models.Reading.author)))
    sensor_readings = result.scalars().all()
    return templates.TemplateResponse(request, "home.html", {"sensor_readings" : sensor_readings, "title": "Sensor Readings"})

@app.get("/sensor_reading/{sensor_reading_id}", include_in_schema=False)
async def sensor_reading_page(request:Request, sensor_reading_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Reading).where(models.Reading.id == sensor_reading_id).options(selectinload(models.Reading.author)))
    sensor_reading = result.scalars().first()
    if sensor_reading:
        title = sensor_reading.sensor[:50]
        return templates.TemplateResponse(request, "sensor_reading.html", {"sensor_reading":sensor_reading, "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor reading not found")


@app.get("/user/{user_id}/readings", include_in_schema=False, name="user_readings")
async def user_readings_page(request:Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 
    result = await db.execute(select(models.Reading).where(models.Reading.user_id == user_id).options(selectinload(models.Reading.author)))
    readings = result.scalars().all()
    return templates.TemplateResponse(request, "user_readings.html", {"readings":readings, "user":user, "title":f"{user.username}'s Readings"})

    
        




@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request:Request, exception:StarletteHTTPException):
    
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    message = (
            exception.detail
            if exception.detail
            else "An error occurred. Please check your request and try again"
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
        "status_code": exception.status_code,
         "title": exception.status_code,
         "message":message,
         },
        status_code = exception.status_code,
    )
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    return templates.TemplateResponse(
        request,
        "error.html",
        {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message":"Invalid request. Please check your input and try again",
            },
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
