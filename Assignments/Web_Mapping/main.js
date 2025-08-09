// Supabase client setup
const { createClient } = supabase;
const supabaseUrl = 'https://dykzwplgzaheuwnmugpr.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR5a3p3cGxnemFoZXV3bm11Z3ByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMzOTUwNzMsImV4cCI6MjA2ODk3MTA3M30.RhQ3UY-En-6md4FZ49fIuBYdtaDi5_t451lbq-mM6Q8';
const supabaseClient = createClient(supabaseUrl, supabaseKey);

// Function to query Supabase data
async function querySupabase() {
    const { data, error } = await supabaseClient
        .from("open-restaurant-inspections")
        .select("*")
        .limit(100);

    if (error) {
        console.error("Error fetching data:", error);
    } else {
        console.log("Data fetched successfully:", data);
    }
}

// Function to query restaurants within distance of a clicked point
async function queryWithinDistance(point, n = 1000) {
    console.log("Querying point:", point, "radius:", n);
    
    const { data, error } = await supabaseClient.rpc(
        "find_nearest_n_restaurants",
        {
            lat: point[1],
            lon: point[0],
            n: n,
        }
    );

    if (error) {
        console.error("Error fetching nearest points:", error);
        return;
    }
    
    console.log("Nearest points fetched successfully:", data);
    console.log("Number of restaurants found:", data.length);
    
    if (!data || data.length === 0) {
        console.log("No restaurants found in this area");
        return;
    }
    
    console.log("First restaurant:", data[0]);
    
    // Convert data to GeoJSON format
    const validRestaurants = data.filter(restaurant => {
        const hasValidCoords = restaurant.long != null && restaurant.lat != null && 
                              !isNaN(restaurant.long) && !isNaN(restaurant.lat);
        if (!hasValidCoords) {
            console.log("Invalid coordinates for:", restaurant.name);
        }
        return hasValidCoords;
    });
    
    console.log("Valid restaurants:", validRestaurants.length);
    
    if (validRestaurants.length === 0) {
        console.log("No restaurants with valid coordinates");
        return;
    }
    
    const geojsonData = {
        type: "FeatureCollection",
        features: validRestaurants.map((restaurant) => {
            console.log("Creating feature for:", restaurant.name, "at", restaurant.long, restaurant.lat);
            return {
                type: "Feature",
                geometry: {
                    type: "Point",
                    coordinates: [Number(restaurant.long), Number(restaurant.lat)]
                },
                properties: restaurant
            };
        })
    };

    console.log("GeoJSON features created:", geojsonData.features.length);

    // Add to map with styling
    const layer = L.geoJSON(geojsonData, {
        pointToLayer: function (feature, latlng) {
            console.log("Creating marker at:", latlng);
            return L.circleMarker(latlng, {
                radius: 8,
                fillColor: "#ff0000",
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });
        },
        onEachFeature: function (feature, layer) {
            const popup = `
                <strong>${feature.properties.name || 'Unknown'}</strong><br>
                Distance: ${Math.round(feature.properties.dist_meters || 0)}m<br>
                Seating: ${feature.properties.seating_choice || 'N/A'}
            `;
            layer.bindPopup(popup);
        }
    });
    
    layer.addTo(map);
    console.log("Layer added to map successfully");
}

// Create a map and set its view to a specific location and zoom level
var map = L.map("map").setView([40.70491, -73.97144], 13);

// Add a tile layer to the map (this is the base layer that provides the map imagery)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

// When map is loaded, add click event
map.on('load', function() {
    // Add click event to the map (as instructed in tutorial)
    map.on("click", (e) => {
        const point = [e.latlng.lng, e.latlng.lat];
        queryWithinDistance(point, 1000); 
    });
});

// Also add click event immediately for Leaflet (since 'load' event behavior differs)
map.on("click", (e) => {
    const point = [e.latlng.lng, e.latlng.lat];
    queryWithinDistance(point, 1000); 
});

// Fetch pizza restaurant data from the NYC Open Data API (commented out)
/*
fetch(
  "https://data.cityofnewyork.us/resource/43nn-pn8j.geojson?cuisine_description=Pizza&$limit=10000"
)
  .then((response) => response.json())
  .then((data) => {
    // Process each feature to create proper geometry
    data.features.forEach((feature) => {
      feature.geometry = {
        type: "Point",
        coordinates: [
          Number(feature.properties.longitude),
          Number(feature.properties.latitude),
        ],
      };
    });

    // Add the data to the map as a GeoJSON layer with custom styling
    L.geoJSON(data, {
      pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: "#ff7800",
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        });
      },
      onEachFeature: function (feature, layer) {
        layer.bindPopup(feature.properties.dba);
      }
    }).addTo(map);
  })
  .catch((error) => console.error("Error fetching data:", error));
*/

// Call querySupabase when page loads
document.addEventListener("DOMContentLoaded", () => {
    querySupabase();
});