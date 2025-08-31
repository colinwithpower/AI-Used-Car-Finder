import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [cars, setCars] = useState([])
  const [filterOptions, setFilterOptions] = useState({})
  const [filters, setFilters] = useState({
    make: '',
    model: '',
    minYear: '',
    maxYear: '',
    minPrice: '',
    maxPrice: '',
    minMileage: '',
    maxMileage: '',
    color: '',
    bodytype: ''
  })
  const [loading, setLoading] = useState(true)
  
  // AI Chat states
  const [chatInput, setChatInput] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const API_BASE = 'http://localhost:8000'

  useEffect(() => {
    fetchFilterOptions()
    fetchCars()
  }, [])

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_BASE}/filters`)
      const data = await response.json()
      console.log('Filter options received:', data)
      setFilterOptions(data)
    } catch (error) {
      console.error('Error fetching filter options:', error)
    }
  }

  const fetchCars = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== '' && value !== 'Any') {
          // Convert frontend camelCase to backend snake_case
          let backendKey = key
          if (key === 'minYear') backendKey = 'min_year'
          if (key === 'maxYear') backendKey = 'max_year'
          if (key === 'minPrice') backendKey = 'min_price'
          if (key === 'maxPrice') backendKey = 'max_price'
          if (key === 'minMileage') backendKey = 'min_mileage'
          if (key === 'maxMileage') backendKey = 'max_mileage'
          
          // Convert numeric fields to integers (both dropdowns and input fields)
          if (['minYear', 'maxYear', 'minPrice', 'maxPrice', 'minMileage', 'maxMileage'].includes(key)) {
            const numValue = parseInt(value, 10)
            if (!isNaN(numValue)) {
              params.append(backendKey, numValue.toString())
            }
          } else {
            params.append(backendKey, value)
          }
        }
      })
      
      console.log('Sending filters:', Object.fromEntries(params))
      
      const response = await fetch(`${API_BASE}/cars?${params}`)
      const data = await response.json()
      setCars(data)
    } catch (error) {
      console.error('Error fetching cars:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleApplyFilters = () => {
    console.log('Current filters state:', filters)
    fetchCars()
  }

  const handleClearFilters = () => {
    setFilters({
      make: '',
      model: '',
      minYear: '',
      maxYear: '',
      minPrice: '',
      maxPrice: '',
      minMileage: '',
      maxMileage: '',
      color: '',
      bodytype: ''
    })
  }

  // AI Chat functions
  const handleChatSubmit = async (e) => {
    e.preventDefault()
    if (!chatInput.trim() || isSubmitting) return

    const userMessage = chatInput.trim()
    setChatInput('')
    setIsSubmitting(true)

    // Add user message to chat history
    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString()
    }
    
    setChatHistory(prev => [...prev, newUserMessage])

    try {
      // Call the AI endpoint
      const response = await fetch(`${API_BASE}/ai-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI response')
      }

      const aiData = await response.json()
      
      // Add AI response to chat history
      const aiResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiData.message,
        timestamp: new Date().toLocaleTimeString()
      }
      setChatHistory(prev => [...prev, aiResponse])

      // Apply the AI-generated filters to the main filter state
      if (aiData.filters) {
        const newFilters = {
          make: aiData.filters.make || '',
          model: aiData.filters.model || '',
          minYear: aiData.filters.min_year || '',
          maxYear: aiData.filters.max_year || '',
          minPrice: aiData.filters.min_price || '',
          maxPrice: aiData.filters.max_price || '',
          minMileage: aiData.filters.min_mileage || '',
          maxMileage: aiData.filters.max_mileage || '',
          color: aiData.filters.color || '',
          bodytype: aiData.filters.bodytype || ''
        }
        
        setFilters(newFilters)
        // The useEffect will automatically fetch cars when filters change
      }
    } catch (error) {
      console.error('Error calling AI endpoint:', error)
      
      // Add error response to chat history
      const errorResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, I encountered an error processing your request. Please try again or use the manual filters.',
        timestamp: new Date().toLocaleTimeString()
      }
      setChatHistory(prev => [...prev, errorResponse])
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const formatMileage = (mileage) => {
    return new Intl.NumberFormat('en-US').format(mileage)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🚗 AI Used Car Finder</h1>
        <p>Find your perfect used car with AI-powered search and advanced filtering</p>
      </header>

      <div className="container">
        {/* AI Chat Section */}
        <div className="ai-section">
          <h2>AI Assistant</h2>
          <p className="ai-description">Describe your ideal car and I'll help you find it!</p>
          
          {/* Chat Input */}
          <form onSubmit={handleChatSubmit} className="chat-input-form">
            <div className="chat-input-container">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="e.g., 'I want a red SUV under $20,000 with less than 50,000 miles'"
                className="chat-input"
                disabled={isSubmitting}
              />
              <button 
                type="submit" 
                className="chat-submit-btn"
                disabled={!chatInput.trim() || isSubmitting}
              >
                {isSubmitting ? '...' : 'Send'}
              </button>
            </div>
          </form>

          {/* Chat History */}
          <div className="chat-history">
            {chatHistory.length === 0 ? (
              <div className="empty-chat">
                <p>Start a conversation with me to find your perfect car!</p>
                <p>Try asking: "I need a reliable sedan under $15,000"</p>
              </div>
            ) : (
              <div className="chat-messages">
                {chatHistory.map((message) => (
                  <div 
                    key={message.id} 
                    className={`chat-message ${message.type}`}
                  >
                    <div className="message-header">
                      <span className="message-author">
                        {message.type === 'user' ? 'You' : 'AI Assistant'}
                      </span>
                      <span className="message-time">{message.timestamp}</span>
                    </div>
                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                ))}
                {isSubmitting && (
                  <div className="chat-message ai">
                    <div className="message-header">
                      <span className="message-author">AI Assistant</span>
                    </div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Filters Section */}
        <div className="filters-section">
          <h2>Filters</h2>
          <div className="filters-grid">
            <div className="filter-group">
              <label>Make:</label>
              <select 
                value={filters.make} 
                onChange={(e) => handleFilterChange('make', e.target.value)}
              >
                <option value="">All Makes</option>
                {filterOptions.makes?.map(make => (
                  <option key={make} value={make}>{make}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Model:</label>
              <select 
                value={filters.model} 
                onChange={(e) => handleFilterChange('model', e.target.value)}
              >
                <option value="">All Models</option>
                {filterOptions.models?.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Color:</label>
              <select 
                value={filters.color} 
                onChange={(e) => handleFilterChange('color', e.target.value)}
              >
                <option value="">All Colors</option>
                {filterOptions.colors?.map(color => (
                  <option key={color} value={color}>{color}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Body Type:</label>
              <select 
                value={filters.bodytype} 
                onChange={(e) => handleFilterChange('bodytype', e.target.value)}
              >
                <option value="">All Types</option>
                {filterOptions.bodytypes?.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Min Year:</label>
              <select 
                value={filters.minYear} 
                onChange={(e) => handleFilterChange('minYear', e.target.value)}
              >
                <option value="">Any</option>
                {filterOptions.years?.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Max Year:</label>
              <select 
                value={filters.maxYear} 
                onChange={(e) => handleFilterChange('maxYear', e.target.value)}
              >
                <option value="">Any</option>
                {filterOptions.years?.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Min Price:</label>
              <input 
                type="number" 
                placeholder="Min Price"
                value={filters.minPrice} 
                onChange={(e) => handleFilterChange('minPrice', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Max Price:</label>
              <input 
                type="number" 
                placeholder="Max Price"
                value={filters.maxPrice} 
                onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Min Mileage:</label>
              <input 
                type="number" 
                placeholder="Min Mileage"
                value={filters.minMileage} 
                onChange={(e) => handleFilterChange('minMileage', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Max Mileage:</label>
              <input 
                type="number" 
                placeholder="Max Mileage"
                value={filters.maxMileage} 
                onChange={(e) => handleFilterChange('maxMileage', e.target.value)}
              />
            </div>
          </div>

          <div className="filter-buttons">
            <button onClick={handleApplyFilters} className="btn-primary">
              Apply Filters
            </button>
            <button onClick={handleClearFilters} className="btn-secondary">
              Clear All
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="results-section">
          <div className="results-header">
            <h2>Results ({cars.length} cars found)</h2>
            {loading && <div className="loading">Loading...</div>}
          </div>

          {cars.length === 0 && !loading ? (
            <div className="no-results">
              <p>No cars found matching your criteria.</p>
              <p>Try adjusting your filters or ask the AI for help!</p>
            </div>
          ) : (
            <div className="cars-grid">
              {cars.map(car => (
                <div key={car.id} className="car-card">
                  <div className="car-header">
                    <h3>{car.make} {car.model}</h3>
                    <span className="car-id">{car.id}</span>
                  </div>
                  <div className="car-details">
                    <div className="car-attribute">
                      <span className="label">Year:</span>
                      <span className="value">{car.year}</span>
                    </div>
                    <div className="car-attribute">
                      <span className="label">Price:</span>
                      <span className="value price">{formatPrice(car.price)}</span>
                    </div>
                    <div className="car-attribute">
                      <span className="label">Mileage:</span>
                      <span className="value">{formatMileage(car.mileage)} mi</span>
                    </div>
                    <div className="car-attribute">
                      <span className="label">Color:</span>
                      <span className="value">{car.color}</span>
                    </div>
                    <div className="car-attribute">
                      <span className="label">Body Type:</span>
                      <span className="value">{car.bodytype}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
