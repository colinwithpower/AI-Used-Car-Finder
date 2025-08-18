# 🚗 AI Used Car Finder

A modern web application for filtering and displaying used car listings with a beautiful React frontend and FastAPI backend.

## Features

- **Advanced Filtering**: Filter cars by make, model, year, price, mileage, color, and body type
- **Real-time Results**: Instant filtering with live result updates
- **Modern UI**: Beautiful, responsive design with smooth animations
- **RESTful API**: FastAPI backend with comprehensive filtering endpoints
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **CSS3** - Modern styling with gradients and animations

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Python runtime
- **Uvicorn** - ASGI server for running FastAPI

## Project Structure

```
AI Used Car Finder (new)/
├── carList.json          # Car data source
├── frontend/             # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   └── App.css       # Styling
│   └── package.json
├── backend/              # FastAPI backend
│   ├── main.py           # FastAPI application
│   └── venv/             # Python virtual environment
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn
   ```

4. **Run the backend server:**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   
   You can also view the interactive API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## API Endpoints

### GET `/cars`
Returns filtered car listings with optional query parameters:

- `make` - Filter by car make
- `model` - Filter by car model  
- `min_year` - Minimum year
- `max_year` - Maximum year
- `min_price` - Minimum price
- `max_price` - Maximum price
- `min_mileage` - Minimum mileage
- `max_mileage` - Maximum mileage
- `color` - Filter by color
- `bodytype` - Filter by body type

**Example:**
```
GET /cars?make=BMW&min_price=5000&max_price=15000
```

### GET `/filters`
Returns available filter options for dropdowns:
- `makes` - List of all car makes
- `models` - List of all car models
- `colors` - List of all colors
- `bodytypes` - List of all body types
- `years` - List of all years

## Car Data Structure

Each car object contains:
```json
{
  "id": "car_001",
  "make": "BMW",
  "model": "X3",
  "year": 2017,
  "price": 7253,
  "mileage": 55722,
  "color": "Red",
  "bodytype": "suv"
}
```

## Usage

1. **Start both servers** (backend and frontend) as described above
2. **Open your browser** and navigate to `http://localhost:5173`
3. **Use the filters** on the left sidebar to narrow down your search:
   - Select specific makes, models, colors, or body types
   - Set price and mileage ranges
   - Choose year ranges
4. **View results** in the main area showing car cards with all details
5. **Apply or clear filters** using the buttons at the bottom of the filter panel

## Development

### Adding New Features
- **Frontend**: Edit `frontend/src/App.jsx` for React components
- **Backend**: Edit `backend/main.py` for API endpoints
- **Styling**: Edit `frontend/src/App.css` for visual changes

### Data Source
The application reads from `carList.json` in the root directory. To add more cars, simply add new car objects to this JSON file following the same structure.

## Troubleshooting

### Common Issues

1. **Backend not starting**: Make sure you're in the virtual environment and have installed dependencies
2. **Frontend can't connect to backend**: Ensure the backend is running on port 8000
3. **CORS errors**: The backend is configured to allow requests from `http://localhost:5173`

### Port Conflicts
- Backend runs on port 8000 by default
- Frontend runs on port 5173 by default
- If these ports are in use, you can change them in the respective configuration files

## License

This project is open source and available under the MIT License.
