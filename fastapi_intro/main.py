from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
    return templates.TemplateResponse(request, "home.html", {"readings" : sensor_readings, "title": "Sensor Readings"})


@app.get("/api/sensor_readings")
def get_sensor_readings():
    return sensor_readings


@app.get("/api/sensor_readings/{sensor_reading_id}")
def get_sensor_reading(sensor_reading_id:int):
    for sensor_reading in sensor_readings:
        if sensor_reading['id'] == sensor_reading_id:
            return sensor_reading
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor reading id not found")