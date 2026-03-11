"""
py5 Ship and Aircraft Tracker

This script visualizes real-time ship and aircraft positions on a world map.
It uses py5 (Python wrapper for Processing) for visualization and fetches data from:
- AISStream (WebSocket) for ship positions
- OpenSky Network (REST API) for aircraft positions

Features:
- Real-time tracking of ships and aircraft
- Movement history trails (cyan for ships, yellow for aircraft)
- Simplified world map background
- Performance optimization (limits display to 50 objects each)

Note: This script requires an internet connection and uses public APIs.
"""

import py5
import threading
import time
import requests
import json
import websocket
import math

# Global lists to store ship and aircraft data with history
ships = []  # List of dicts: {'lat': float, 'lon': float, 'name': str, 'history': list}
aircraft = []  # List of dicts: {'lat': float, 'lon': float, 'callsign': str, 'history': list}
ships_lock = threading.Lock()
aircraft_lock = threading.Lock()

# Configuration
OPENSKY_API_URL = "https://opensky-network.org/api/states/all"
AISSTREAM_WS_URL = "wss://stream.aisstream.io/v0/stream"


def websocket_thread():
    """Connect to AISStream websocket and update ship positions."""

    def on_message(ws, message):
        data = json.loads(message)
        if "Message" in data:
            msg = data["Message"]
            if "PositionReport" in msg:
                pos = msg["PositionReport"]
                lat = pos["Latitude"]
                lon = pos["Longitude"]
                name = msg.get("VesselName", "Unknown")

                with ships_lock:
                    # Find if ship already exists
                    found = False
                    for ship in ships:
                        if ship["name"] == name:
                            # Update position and add to history
                            ship["lat"] = lat
                            ship["lon"] = lon
                            ship["history"].append((lat, lon))
                            # Keep only last 50 history points
                            if len(ship["history"]) > 50:
                                ship["history"].pop(0)
                            found = True
                            break

                    if not found:
                        # Add new ship
                        ships.append(
                            {
                                "lat": lat,
                                "lon": lon,
                                "name": name,
                                "history": [(lat, lon)],
                            }
                        )

                    # Limit total ships
                    if len(ships) > 100:
                        ships.pop(0)

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(ws):
        print("WebSocket connected")
        subscription = {
            "Apikey": "public",
            "BoundingBoxes": [[-90, -180], [90, 180]],
            "FilterMessageTypes": ["PositionReport"],
        }
        ws.send(json.dumps(subscription))

    try:
        ws = websocket.WebSocketApp(
            AISSTREAM_WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()
    except Exception as e:
        print(f"WebSocket connection failed: {e}")


def aircraft_thread():
    """Fetch aircraft data from OpenSky Network API periodically."""
    while True:
        try:
            response = requests.get(OPENSKY_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                with aircraft_lock:
                    # Create a set of current aircraft for updating
                    current_aircraft = {}
                    for state in data.get("states", []):
                        if state[5] is not None and state[6] is not None:
                            icao = state[0]
                            current_aircraft[icao] = {
                                "lat": state[6],
                                "lon": state[5],
                                "callsign": state[1] if state[1] else "N/A",
                            }

                    # Update existing aircraft and add new ones
                    new_aircraft = []
                    for icao, data in current_aircraft.items():
                        found = False
                        for plane in aircraft:
                            if plane.get("icao") == icao:
                                # Update position and history
                                plane["lat"] = data["lat"]
                                plane["lon"] = data["lon"]
                                plane["history"].append((data["lat"], data["lon"]))
                                if len(plane["history"]) > 50:
                                    plane["history"].pop(0)
                                new_aircraft.append(plane)
                                found = True
                                break

                        if not found:
                            # Add new aircraft
                            new_aircraft.append(
                                {
                                    "icao": icao,
                                    "lat": data["lat"],
                                    "lon": data["lon"],
                                    "callsign": data["callsign"],
                                    "history": [(data["lat"], data["lon"])],
                                }
                            )

                    aircraft.clear()
                    aircraft.extend(new_aircraft)

                    print(f"Aircraft update: {len(aircraft)} planes tracked")
        except Exception as e:
            print(f"Aircraft fetch error: {e}")
        time.sleep(10)


def setup():
    py5.size(1200, 700)

    # Start threads
    t1 = threading.Thread(target=websocket_thread, daemon=True)
    t2 = threading.Thread(target=aircraft_thread, daemon=True)
    t1.start()
    t2.start()


def draw():
    py5.background(20, 30, 50)  # Sea color

    # Draw world map (continents)
    py5.stroke(60, 80, 100)
    py5.stroke_weight(2)

    # Simplified continent outlines
    # North America
    py5.line(150, 150, 300, 150)
    py5.line(300, 150, 350, 250)
    py5.line(350, 250, 250, 350)
    py5.line(250, 350, 150, 250)
    py5.line(150, 250, 150, 150)
    # South America
    py5.line(250, 350, 300, 400)
    py5.line(300, 400, 280, 550)
    py5.line(280, 550, 250, 600)
    py5.line(250, 600, 220, 500)
    py5.line(220, 500, 250, 350)
    # Eurasia
    py5.line(500, 100, 900, 100)
    py5.line(900, 100, 950, 200)
    py5.line(950, 200, 900, 350)
    py5.line(900, 350, 600, 350)
    py5.line(600, 350, 500, 250)
    py5.line(500, 250, 500, 100)
    # Africa
    py5.line(550, 350, 650, 350)
    py5.line(650, 350, 680, 450)
    py5.line(680, 450, 620, 550)
    py5.line(620, 550, 550, 450)
    py5.line(550, 450, 550, 350)
    # Australia
    py5.line(900, 450, 1050, 450)
    py5.line(1050, 450, 1050, 550)
    py5.line(1050, 550, 900, 550)
    py5.line(900, 550, 900, 450)

    # Helper function to convert lat/lon to screen coordinates
    def latlon_to_screen(lat, lon):
        x = (lon + 180) * (py5.width / 360)
        y = (90 - lat) * (py5.height / 180)
        return x, y

    # Draw Ships (AIS) with history trails
    with ships_lock:
        # Limit to 50 ships for performance
        for ship in ships[:50]:
            # Draw history trail
            if len(ship["history"]) > 1:
                py5.stroke(0, 255, 255, 100)  # Cyan with transparency
                py5.stroke_weight(2)
                py5.no_fill()
                py5.begin_shape()
                for lat, lon in ship["history"]:
                    x, y = latlon_to_screen(lat, lon)
                    py5.vertex(x, y)
                py5.end_shape()

            # Draw current position
            x, y = latlon_to_screen(ship["lat"], ship["lon"])
            py5.fill(0, 255, 255)
            py5.no_stroke()
            py5.circle(x, y, 6)

    # Draw Aircraft with history trails
    with aircraft_lock:
        # Limit to 50 aircraft for performance
        for plane in aircraft[:50]:
            # Draw history trail
            if len(plane["history"]) > 1:
                py5.stroke(255, 255, 0, 100)  # Yellow with transparency
                py5.stroke_weight(2)
                py5.no_fill()
                py5.begin_shape()
                for lat, lon in plane["history"]:
                    x, y = latlon_to_screen(lat, lon)
                    py5.vertex(x, y)
                py5.end_shape()

            # Draw current position
            x, y = latlon_to_screen(plane["lat"], plane["lon"])
            py5.fill(255, 255, 0)
            py5.no_stroke()
            py5.circle(x, y, 6)

    # Legend
    py5.fill(255)
    py5.text_size(12)
    py5.text_align(py5.LEFT)
    py5.text("Ships (AIS) - Cyan with trails", 10, 20)
    py5.text("Aircraft (ADS-B) - Yellow with trails", 10, 40)
    py5.text("Trails show recent movement history", 10, 60)


if __name__ == "__main__":
    print("Starting tracking app with history trails...")
    py5.run_sketch()
