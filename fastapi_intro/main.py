from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ReadingCreate, ReadingResponse



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sensor_readings: list[dict] = [
    {
        "id" : 1,
        "sensor" : "temp",
        "content" : 21.0,
        "date_timestamp" : "Sept 24, 2026, 11:30"
    },
    {
        "id" : 2,
        "sensor" : "lux",
        "content" : 100,
        "date_timestamp" : "Sept 24, 2026, 11:33"
    },
]

@app.get("/",  include_in_schema=False, name="home")
@app.get("/sensor_readings", include_in_schema=False, name="sensor_readings")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"sensor_readings" : sensor_readings, "title": "Sensor Readings"})

@app.get("/sensor_reading/{sensor_reading_id}", include_in_schema=False)
def sensor_reading_page(request:Request, sensor_reading_id:int):
    for sensor_reading in sensor_readings:
        if sensor_reading.get("id") == sensor_reading_id:
            title = sensor_reading['sensor'][:50]
            return templates.TemplateResponse(request, "sensor_reading.html", {"sensor_reading":sensor_reading, "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor reading id not found")


@app.get("/api/sensor_readings", response_model=list[ReadingResponse])
def get_sensor_readings():
    return sensor_readings


@app.get("/api/sensor_reading/{sensor_reading_id}", response_model=ReadingResponse)
def get_sensor_reading(sensor_reading_id:int):
    for sensor_reading in sensor_readings:
        if sensor_reading['id'] == sensor_reading_id:
            return sensor_reading
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor reading id not found")

@app.post("/api/reading", response_model=ReadingResponse, status_code = status.HTTP_201_CREATED)
def create_reading(reading: ReadingCreate):
    new_id = max(r["id"] for r in sensor_readings) + 1 if sensor_readings else 1
    new_post = {
        "id": new_id,
        "sensor": reading.sensor,
        "content": reading.content,
        "date_timestamp": "Oct 2, 2026, 12:00"
    }
    sensor_readings.append(new_post)
    return new_post


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request:Request, exception:StarletteHTTPException):
    message = {
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again"
    }
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = exception.status_code,
            content = {"detail": message}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
        "status_code": exception.status_code,
         "title": exception.status_code,
         "message":exception.detail,
         },
        status_code = exception.status_code,
    )
    
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request:Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
                content = {"detail": exception.errors()}
            )
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
