from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Car Finder API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Car model
class Car(BaseModel):
    id: str
    make: str
    model: str
    year: int
    price: int
    mileage: int
    color: str
    bodytype: str

# Load car data
def load_cars():
    with open("../carList.json", "r") as f:
        return json.load(f)

@app.get("/")
def read_root():
    return {"message": "Car Finder API"}

@app.get("/cars", response_model=List[Car])
def get_cars(
    make: Optional[str] = Query(None, description="Filter by car make"),
    model: Optional[str] = Query(None, description="Filter by car model"),
    min_year: Optional[int] = Query(None, description="Minimum year"),
    max_year: Optional[int] = Query(None, description="Maximum year"),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    min_mileage: Optional[int] = Query(None, description="Minimum mileage"),
    max_mileage: Optional[int] = Query(None, description="Maximum mileage"),
    color: Optional[str] = Query(None, description="Filter by color"),
    bodytype: Optional[str] = Query(None, description="Filter by body type")
):
    cars = load_cars()
    
    # Apply filters
    filtered_cars = cars
    
    # Debug: Print received parameters
    print(f"Received filters: make={make}, model={model}, min_year={min_year}, max_year={max_year}, min_price={min_price}, max_price={max_price}, min_mileage={min_mileage}, max_mileage={max_mileage}, color={color}, bodytype={bodytype}")
    
    if make and make.strip():
        filtered_cars = [car for car in filtered_cars if car["make"].lower() == make.lower().strip()]
    
    if model and model.strip():
        filtered_cars = [car for car in filtered_cars if car["model"].lower() == model.lower().strip()]
    
    if min_year is not None:
        filtered_cars = [car for car in filtered_cars if car["year"] >= min_year]
    
    if max_year is not None:
        filtered_cars = [car for car in filtered_cars if car["year"] <= max_year]
    
    if min_price is not None:
        filtered_cars = [car for car in filtered_cars if car["price"] >= min_price]
    
    if max_price is not None:
        filtered_cars = [car for car in filtered_cars if car["price"] <= max_price]
    
    if min_mileage is not None:
        filtered_cars = [car for car in filtered_cars if car["mileage"] >= min_mileage]
    
    if max_mileage is not None:
        filtered_cars = [car for car in filtered_cars if car["mileage"] <= max_mileage]
    
    if color and color.strip():
        filtered_cars = [car for car in filtered_cars if car["color"].lower() == color.lower().strip()]
    
    if bodytype and bodytype.strip():
        filtered_cars = [car for car in filtered_cars if car["bodytype"].lower() == bodytype.lower().strip()]
    
    print(f"Filtered cars count: {len(filtered_cars)}")
    return filtered_cars

@app.get("/filters")
def get_filter_options():
    """Get available filter options for dropdowns"""
    cars = load_cars()
    
    makes = sorted(list(set(car["make"] for car in cars)))
    models = sorted(list(set(car["model"] for car in cars)))
    colors = sorted(list(set(car["color"] for car in cars)))
    bodytypes = sorted(list(set(car["bodytype"] for car in cars)))
    years = sorted(list(set(car["year"] for car in cars)))
    
    return {
        "makes": makes,
        "models": models,
        "colors": colors,
        "bodytypes": bodytypes,
        "years": years
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
