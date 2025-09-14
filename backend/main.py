from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import json
import os
import re

# OpenAI client (v1 SDK)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # friendly error if the package isn't installed

app = FastAPI(title="Car Finder API", version="1.0.0")

# --------------------------- CORS ---------------------------------
# For first deploy keep it permissive; later set ALLOW_ORIGINS env var
allow_origins_env = os.environ.get("ALLOW_ORIGINS")
if allow_origins_env:
    ORIGINS = [o.strip() for o in allow_origins_env.split(",") if o.strip()]
else:
    ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------- Models -------------------------------
class Car(BaseModel):
    id: str
    make: str
    model: str
    year: int
    price: int
    mileage: int
    color: str
    bodytype: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    filters: Dict[str, Any]
    cars_found: int

# --------------------------- Data --------------------------------
# carList.json must be next to this file after deploy
DATA_PATH = (Path(__file__).parent / "carList.json").resolve()

def load_cars() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_available_options() -> Dict[str, List[Any]]:
    cars = load_cars()
    makes = sorted({c["make"] for c in cars})
    models = sorted({c["model"] for c in cars})
    colors = sorted({c["color"] for c in cars})
    bodytypes = sorted({c["bodytype"] for c in cars})
    years = sorted({c["year"] for c in cars})
    return {
        "makes": makes,
        "models": models,
        "colors": colors,
        "bodytypes": bodytypes,
        "years": years,
    }

# ------------------------- Helpers -------------------------------
def extract_filters_from_ai_response(ai_response: str) -> Dict[str, Any]:
    """Pull the first {...} JSON block from the model response."""
    try:
        m = re.search(r"\{.*\}", ai_response, re.DOTALL)
        if not m:
            return {}
        return json.loads(m.group())
    except Exception:
        return {}

def apply_filters(cars: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = cars
    if filters.get("make"):
        out = [c for c in out if c["make"].lower() == str(filters["make"]).lower()]
    if filters.get("model"):
        out = [c for c in out if c["model"].lower() == str(filters["model"]).lower()]
    if filters.get("min_year") is not None:
        out = [c for c in out if c["year"] >= int(filters["min_year"])]
    if filters.get("max_year") is not None:
        out = [c for c in out if c["year"] <= int(filters["max_year"])]
    if filters.get("min_price") is not None:
        out = [c for c in out if c["price"] >= int(filters["min_price"])]
    if filters.get("max_price") is not None:
        out = [c for c in out if c["price"] <= int(filters["max_price"])]
    if filters.get("min_mileage") is not None:
        out = [c for c in out if c["mileage"] >= int(filters["min_mileage"])]
    if filters.get("max_mileage") is not None:
        out = [c for c in out if c["mileage"] <= int(filters["max_mileage"])]
    if filters.get("color"):
        out = [c for c in out if c["color"].lower() == str(filters["color"]).lower()]
    if filters.get("bodytype"):
        out = [c for c in out if c["bodytype"].lower() == str(filters["bodytype"]).lower()]
    return out

# -------------------------- Routes -------------------------------
@app.get("/")
def root():
    return {"message": "Car Finder API"}

@app.get("/health")
def health():
    return {"ok": True, "data_file_present": DATA_PATH.exists()}

@app.get("/cars", response_model=List[Car])
def get_cars(
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    min_year: Optional[int] = Query(None),
    max_year: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    min_mileage: Optional[int] = Query(None),
    max_mileage: Optional[int] = Query(None),
    color: Optional[str] = Query(None),
    bodytype: Optional[str] = Query(None),
):
    cars = load_cars()
    filters = {
        "make": make,
        "model": model,
        "min_year": min_year,
        "max_year": max_year,
        "min_price": min_price,
        "max_price": max_price,
        "min_mileage": min_mileage,
        "max_mileage": max_mileage,
        "color": color,
        "bodytype": bodytype,
    }
    return apply_filters(cars, filters)

@app.get("/filters")
def filter_options():
    return get_available_options()

@app.post("/ai-chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    """
    Convert user's free text to structured filters with OpenAI, then filter cars.
    """
    try:
        if OpenAI is None:
            raise RuntimeError("openai package not installed")

        api_key = os.environ.get("OPENAI_API_KEY") 
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        client = OpenAI(api_key=api_key)

        opts = get_available_options()
        system_prompt = (
            "You are a helpful car search assistant. Convert user descriptions into a JSON "
            "object with keys: make, model, min_year, max_year, min_price, max_price, "
            "min_mileage, max_mileage, color, bodytype.\n\n"
            f"Available makes: {', '.join(opts['makes'])}\n"
            f"Available models: {', '.join(opts['models'])}\n"
            f"Available colors: {', '.join(opts['colors'])}\n"
            f"Available body types: {', '.join(opts['bodytypes'])}\n"
            f"Year range: {min(opts['years'])}..{max(opts['years'])}\n\n"
            "Heuristics:\n"
            '- "low mileage" → max_mileage=50000\n'
            '- "high mileage" → min_mileage=100000\n'
            '- "cheap/affordable/budget" → max_price=15000 (budget→10000)\n'
            '- "expensive/luxury/premium" → min_price=30000 (expensive→25000)\n'
            '- "new/newer/recent" → min_year=2020\n'
            '- "older/vintage" → max_year=2015\n\n'
            "Return ONLY the JSON object. No extra text."
        )

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
            max_tokens=200,
            temperature=0.1,
        )

        ai_text = resp.choices[0].message.content.strip()
        filters = extract_filters_from_ai_response(ai_text)

        cars = load_cars()
        filtered = apply_filters(cars, filters)

        parts = []
        if filters.get("make"): parts.append(f"Make: {filters['make']}")
        if filters.get("model"): parts.append(f"Model: {filters['model']}")
        if filters.get("color"): parts.append(f"Color: {filters['color']}")
        if filters.get("bodytype"): parts.append(f"Body Type: {filters['bodytype']}")
        if filters.get("min_year") or filters.get("max_year"):
            parts.append(f"Year: {filters.get('min_year','Any')} - {filters.get('max_year','Any')}")
        if filters.get("min_price") or filters.get("max_price"):
            parts.append(f"Price: {filters.get('min_price','Any')} - {filters.get('max_price','Any')}")
        if filters.get("min_mileage") or filters.get("max_mileage"):
            parts.append(f"Mileage: {filters.get('min_mileage','Any')} - {filters.get('max_mileage','Any')}")

        if parts:
            msg = f"I found {len(filtered)} cars matching: " + ", ".join(parts)
        else:
            msg = f"I found {len(filtered)} cars in our database. Try adding more details."

        return ChatResponse(message=msg, filters=filters, cars_found=len(filtered))

    except Exception as e:
        print(f"[ai-chat] error: {e}")
        return ChatResponse(message="Sorry, there was a problem.", filters={}, cars_found=0)

# Local dev (not used on EB)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
