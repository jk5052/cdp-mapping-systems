# NYC Wellness Route Navigator

**Final Project - Data Mapping Systems**

An interactive web application that generates personalized wellness routes through New York City by combining geospatial data analysis, social media sentiment analysis, and dynamic mapping visualization.

## 🎯 Project Overview

The NYC Wellness Route Navigator addresses the challenge of finding meaningful, personalized routes through New York City that promote mental wellness and cultural engagement. By analyzing geospatial data from NYC Open Data and incorporating social sentiment analysis, the system creates routes tailored to different personality types and wellness preferences.

### Key Features

- **🧠 Personality-Based Route Generation**: Routes optimized for Creative, Healing, Social, and Energetic personality types
- **🗺️ Multi-Modal Data Integration**: Combines NYC cultural institutions, parks, building footprints, and social media sentiment
- **📍 Interactive Visualization**: Dynamic Folium maps with route options and detailed place information
- **💬 Social Context Analysis**: Incorporates community sentiment and trending topics for each location
- **🎨 Art Map Generation**: Creates artistic visualizations of selected routes with custom styling

## 🛠️ Technical Implementation

### Data Sources
- **NYC Open Data**: Cultural institutions, parks, building footprints
- **NYC QGIS Data**: Geospatial layers for Manhattan
- **Social Media Analysis**: Simulated sentiment analysis for location context
- **Google Places API**: Additional venue information (optional)

### Technology Stack
- **Frontend**: Streamlit for interactive web interface
- **Mapping**: Folium for dynamic map visualization
- **Geospatial Analysis**: GeoPandas, Shapely for spatial operations
- **Data Processing**: Pandas, NumPy for data manipulation
- **Distance Calculations**: Geopy for route optimization

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps

1. **Clone or download the project files**
   ```bash
   cd Assignments/final
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

## 📋 Usage Guide

### Step 1: Select Your Wellness Story
Choose from four personality-based wellness approaches:
- **🎨 Creative Explorer**: Focus on art galleries, cultural spaces, and creative venues
- **🌿 Healing Seeker**: Emphasize parks, quiet spaces, and restorative environments  
- **👥 Social Connector**: Prioritize community spaces, cafes, and social venues
- **⚡ Energetic Adventurer**: Target dynamic spaces, active areas, and vibrant locations

### Step 2: Set Your Route
- **Start Location**: Enter your starting point (address or landmark)
- **End Location**: Enter your destination
- **Search Radius**: Adjust the area to search for wellness locations (1-5 km)

### Step 3: Generate Your Route
- Click "Generate Wellness Route" to create personalized route options
- The system analyzes 900+ NYC locations and finds the best matches
- View multiple route alternatives with different waypoints

### Step 4: Explore Route Options
- **Interactive Map**: Explore each route option on the dynamic map
- **Location Details**: Click markers to see detailed information about each place
- **Social Context**: View community sentiment and trending topics for locations
- **Route Selection**: Use radio buttons to switch between different route options

### Step 5: Create Art Map
- Click "🎨 Generate Art Map" for any route to create an artistic visualization
- Art maps feature custom styling, color schemes, and enhanced visual design
- Perfect for sharing or saving your personalized wellness journey

## 📊 Data Analysis Features

### Wellness Scoring Algorithm
Each location receives a wellness score based on:
- **Personality Match**: How well the location fits the selected wellness story
- **Proximity**: Distance from the planned route
- **Social Sentiment**: Community feedback and engagement levels
- **Venue Type**: Category-specific scoring (parks, museums, cafes, etc.)

### Route Optimization
- **Distance-Based Selection**: Optimizes waypoints along the route path
- **Diversity Scoring**: Ensures variety in location types and experiences
- **Social Integration**: Incorporates community preferences and trending locations

## 🎨 Visualization Features

### Interactive Maps
- **Custom Markers**: Different icons for start, end, and waypoint locations
- **Route Lines**: Visual path connections between locations
- **Popup Information**: Detailed location data with social context
- **Zoom Controls**: Navigate and explore different areas of the city

### Art Map Generation
- **Custom Styling**: Artistic color schemes and visual enhancements
- **Enhanced Markers**: Stylized location indicators
- **Route Aesthetics**: Beautiful path visualizations
- **Export Ready**: High-quality maps suitable for sharing

## 📁 Project Structure

```
Assignments/final/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── src/                           # Source code modules
│   ├── google_places_client.py    # Google Places API integration
│   ├── social_analyzer.py         # Social sentiment analysis
│   └── wellness_scorer.py         # Wellness scoring algorithms
├── data/                          # Data files
│   └── nyc_qgis/                 # NYC geospatial data
├── generated_maps/               # Generated art maps
└── art_map_template.html         # HTML template for art maps
```

## 🔧 Configuration

### Optional: Google Places API
To enable enhanced venue data:
1. Get a Google Places API key
2. Create a `.env` file in the project root
3. Add: `GOOGLE_PLACES_API_KEY=your_api_key_here`

The app works fully without the API using NYC Open Data.

## 🎯 Use Cases

- **Urban Planning**: Understand wellness-focused route preferences
- **Tourism**: Create personalized NYC exploration experiences  
- **Mental Health**: Design routes that promote psychological well-being
- **Cultural Engagement**: Connect people with NYC's rich cultural landscape
- **Community Building**: Highlight local venues and social spaces

## 🚀 Future Enhancements

- **Real-time Data**: Integration with live venue information
- **User Profiles**: Save and share personalized routes
- **Mobile App**: Native mobile application development
- **Machine Learning**: Enhanced personality-based recommendations
- **Social Features**: Community route sharing and rating

## 📝 Technical Notes

- The application uses simulated social media data for demonstration purposes
- All geospatial calculations are performed client-side for privacy
- Maps are generated dynamically based on user selections
- The system is designed to work offline with included NYC datasets

## 🎓 Academic Context

This project demonstrates advanced data mapping techniques including:
- **Geospatial Analysis**: Complex spatial operations and route optimization
- **Data Integration**: Combining multiple heterogeneous data sources
- **Interactive Visualization**: Dynamic web-based mapping interfaces
- **User Experience Design**: Intuitive interface for complex data exploration
- **Social Data Analysis**: Incorporating community sentiment into spatial analysis

---

**Author**: [Your Name]  
**Course**: Data Mapping Systems  
**Institution**: [Your Institution]  
**Date**: August 2025
