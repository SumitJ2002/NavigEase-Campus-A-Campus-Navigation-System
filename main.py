import folium

# Create a Folium map.
m = folium.Map(location=[-29.449813889018642, 27.722397467525237], zoom_start=12)

# Store the initial location coordinates.
initial_location = [-29.449813889018642, 27.722397467525237]

# Add a marker to the map for the initial location.
folium.Marker(initial_location, popup="Your Location").add_to(m)

# Store the clicked location coordinates.
clicked_location = None

# Define a click event handler function.
def click_handler(event):
    global clicked_location
    clicked_location = [event.latitude, event.longitude]
    marker = folium.Marker(clicked_location, popup="Your Destination")
    marker.add_to(m)

    # Remove any existing routes and draw the new one.
    m.get_root().script.add_child(folium.Element("clearRoute();"))
    draw_route()

# Add the ClickForMarker plugin to the map.
folium.ClickForMarker(popup=None).add_to(m)

# Draw a route between the initial location and clicked location.
def draw_route():
    if clicked_location is not None:
        # Create a PolyLine object using the initial and clicked locations.
        route = folium.PolyLine(locations=[initial_location, clicked_location], color='blue', weight=2.5)
        route.add_to(m)

        # Pan the map to fit both locations.
        bounds = [initial_location, clicked_location]
        m.fit_bounds(bounds)

# Add a button to the map for getting directions.
get_directions_button = """
<button onclick="getDirections();" style="position: absolute; top: 10px; left: 10px; z-index: 1000;">Get Directions</button>
"""
m.get_root().html.add_child(folium.Element(get_directions_button))

# Add the necessary JavaScript code to load routes on the map using Mapbox.
javascript_code = """
<script src='https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.js'></script>
<link href='https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.css' rel='stylesheet' />

<script>
    mapboxgl.accessToken = 'pk.eyJ1Ijoia2V2aW4wMTEiLCJhIjoiY2xmaWwyeWdwMG9yMzN2cnM0YzY0amxzbyJ9.LJ07zcJETilspFo9RJxteA';

    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-29.449813889018642, 27.722397467525237],
        zoom: 12
    });

    // Store the initial location coordinates.
    var initialLocation = [-29.449813889018642, 27.722397467525237];
    var clickedLocation = null;

    // Add a marker to the map for the initial location.
    new mapboxgl.Marker()
        .setLngLat(initialLocation)
        .setPopup(new mapboxgl.Popup().setHTML('Your Location'))
        .addTo(map);

    // Define a click event handler function.
    function clickHandler(event) {
        clickedLocation = [event.lngLat.lng, event.lngLat.lat];
        new mapboxgl.Marker()
            .setLngLat(clickedLocation)
            .setPopup(new mapboxgl.Popup().setHTML('Your Destination'))
            .addTo(map);

        // Remove any existing routes and draw the new one.
        clearRoute();
        drawRoute();
    }

    // Draw a route between the initial location and clicked location.
    function drawRoute() {
        if (clickedLocation !== null) {
            var coordinates = [initialLocation, clickedLocation];
            var route = {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': coordinates
                        }
                    }
                ]
            };
            map.addSource('route', {
                'type': 'geojson',
                'data': route
            });
            map.addLayer({
                'id': 'route',
                'type': 'line',
                'source': 'route',
                'layout': {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                'paint': {
                    'line-color': '#0074D9',
                    'line-width': 4
                }
            });

            // Fit the map to the bounds of the route.
            var bounds = coordinates.reduce(function(bounds, coord) {
                return bounds.extend(coord);
            }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));
            map.fitBounds(bounds, { padding: 50 });
        }
    }

    // Add a click event listener to the map.
    map.on('click', function(e) {
        clickHandler(e);
    });

    // Function to remove the route from the map.
    function clearRoute() {
        if (map.getLayer('route')) {
            map.removeLayer('route');
        }
        if (map.getSource('route')) {
            map.removeSource('route');
        }
    }

    // Function to get directions using Mapbox Directions API.
    function getDirections() {
        if (clickedLocation !== null) {
            var coordinates = [initialLocation, clickedLocation];
            var directionsAPI = 'https://api.mapbox.com/directions/v5/mapbox/driving-traffic/';
            var requestURL = directionsAPI + coordinates.join(';') + '?access_token=' + mapboxgl.accessToken;

            fetch(requestURL)
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    var route = data.routes[0].geometry;
                    map.addSource('route', {
                        'type': 'geojson',
                        'data': {
                            'type': 'Feature',
                            'geometry': route
                        }
                    });
                    map.addLayer({
                        'id': 'route',
                        'type': 'line',
                        'source': 'route',
                        'layout': {
                            'line-join': 'round',
                            'line-cap': 'round'
                        },
                        'paint': {
                            'line-color': '#0074D9',
                            'line-width': 4
                        }
                    });

                    // Fit the map to the bounds of the route.
                    var bounds = route.coordinates.reduce(function(bounds, coord) {
                        return bounds.extend(coord);
                    }, new mapboxgl.LngLatBounds(route.coordinates[0], route.coordinates[0]));
                    map.fitBounds(bounds, { padding: 50 });
                });
        }
    }
</script>
"""
m.get_root().html.add_child(folium.Element(javascript_code))

# Save the map.
m.save("map.html")
