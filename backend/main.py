from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional
from pydantic import BaseModel
import openai

app = FastAPI(title="Car Finder API", version="1.0.0")

# OpenAI API configuration
OPENAI_API_KEY = "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"

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite default port and alternative
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

# AI Chat request model
class ChatRequest(BaseModel):
    message: str

# AI Chat response model
class ChatResponse(BaseModel):
    message: str
    filters: dict
    cars_found: int

# Load car data
def load_cars():
    with open("../carList.json", "r") as f:
        return json.load(f)

def extract_filters_from_ai_response(ai_response: str) -> dict:
    """
    Extract structured filters from AI response.
    The AI should return filters in a specific format that we can parse.
    """
    try:
        # Try to parse JSON from the AI response
        # Look for JSON-like structure in the response
        import re
        
        # Find JSON-like structure in the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            filters_json = json_match.group()
            filters = json.loads(filters_json)
            return filters
        else:
            # If no JSON found, return empty filters
            return {}
    except:
        return {}

def get_available_options():
    """Get available filter options for AI context"""
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

@app.post("/ai-chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    """
    AI endpoint that converts user description into structured filters
    """
    try:
        # Get available options for context
        available_options = get_available_options()
        
        # Create system prompt with available options
        system_prompt = f"""You are a helpful car search assistant. Convert user descriptions into structured filters.

Available options in our database:
- Makes: {', '.join(available_options['makes'])}
- Models: {', '.join(available_options['models'])}
- Colors: {', '.join(available_options['colors'])}
- Body Types: {', '.join(available_options['bodytypes'])}
- Years: {min(available_options['years'])} to {max(available_options['years'])}

Extract filters from user input and return ONLY a JSON object with these fields:
{{
    "make": "string or null",
    "model": "string or null", 
    "min_year": "integer or null",
    "max_year": "integer or null",
    "min_price": "integer or null",
    "max_price": "integer or null",
    "min_mileage": "integer or null",
    "max_mileage": "integer or null",
    "color": "string or null",
    "bodytype": "string or null"
}}

Only include fields that are explicitly mentioned or can be reasonably inferred from the user's request.
For price and mileage, extract numeric values and convert to integers.
For body types, use: "suv", "sedan", "truck", "coupe", "convertible", "wagon", "hatchback"
Return ONLY the JSON object, no additional text."""

        # Call OpenAI API using the new format
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract filters from AI response
        filters = extract_filters_from_ai_response(ai_response)
        
        # Apply filters to get cars
        cars = load_cars()
        filtered_cars = cars
        
        # Apply each filter
        if filters.get("make"):
            filtered_cars = [car for car in filtered_cars if car["make"].lower() == filters["make"].lower()]
        
        if filters.get("model"):
            filtered_cars = [car for car in filtered_cars if car["model"].lower() == filters["model"].lower()]
        
        if filters.get("min_year"):
            filtered_cars = [car for car in filtered_cars if car["year"] >= filters["min_year"]]
        
        if filters.get("max_year"):
            filtered_cars = [car for car in filtered_cars if car["year"] <= filters["max_year"]]
        
        if filters.get("min_price"):
            filtered_cars = [car for car in filtered_cars if car["price"] >= filters["min_price"]]
        
        if filters.get("max_price"):
            filtered_cars = [car for car in filtered_cars if car["price"] <= filters["max_price"]]
        
        if filters.get("min_mileage"):
            filtered_cars = [car for car in filtered_cars if car["mileage"] >= filters["min_mileage"]]
        
        if filters.get("max_mileage"):
            filtered_cars = [car for car in filtered_cars if car["mileage"] <= filters["max_mileage"]]
        
        if filters.get("color"):
            filtered_cars = [car for car in filtered_cars if car["color"].lower() == filters["color"].lower()]
        
        if filters.get("bodytype"):
            filtered_cars = [car for car in filtered_cars if car["bodytype"].lower() == filters["bodytype"].lower()]
        
        # Create user-friendly message
        applied_filters = []
        if filters.get("make"): applied_filters.append(f"Make: {filters['make']}")
        if filters.get("model"): applied_filters.append(f"Model: {filters['model']}")
        if filters.get("color"): applied_filters.append(f"Color: {filters['color']}")
        if filters.get("bodytype"): applied_filters.append(f"Body Type: {filters['bodytype']}")
        if filters.get("min_year") or filters.get("max_year"):
            year_range = f"Year: {filters.get('min_year', 'Any')} - {filters.get('max_year', 'Any')}"
            applied_filters.append(year_range)
        if filters.get("min_price") or filters.get("max_price"):
            price_range = f"Price: ${filters.get('min_price', 'Any')} - ${filters.get('max_price', 'Any')}"
            applied_filters.append(price_range)
        if filters.get("min_mileage") or filters.get("max_mileage"):
            mileage_range = f"Mileage: {filters.get('min_mileage', 'Any')} - {filters.get('max_mileage', 'Any')} miles"
            applied_filters.append(mileage_range)
        
        if applied_filters:
            message = f"I found {len(filtered_cars)} cars matching your criteria: {', '.join(applied_filters)}"
        else:
            message = f"I found {len(filtered_cars)} cars in our database. Try being more specific with your requirements!"
        
        return ChatResponse(
            message=message,
            filters=filters,
            cars_found=len(filtered_cars)
        )
        
    except Exception as e:
        print(f"Error in AI chat: {str(e)}")
        return ChatResponse(
            message="Sorry, I encountered an error processing your request. Please try again or use the manual filters.",
            filters={},
            cars_found=0
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
