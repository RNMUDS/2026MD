# py5 Ship and Aircraft Tracker

This is a real-time visualization application using py5 (a Python wrapper for Processing) that displays ships and aircraft on a world map.

## Overview

The application fetches real-time ship positions from AISStream (via WebSocket) and aircraft positions from OpenSky Network (via REST API). It then visualizes these positions on a simplified world map, showing movement history trails.

![Visualization Screenshot](screenshot.png) <!-- If you have a screenshot, add it here -->

## Features

- **Real-time tracking**: Ships and aircraft are updated continuously
- **Movement history**: Trails show recent positions (last 50 points)
- **Performance optimized**: Limits display to 50 ships and 50 aircraft
- **Simple visualization**: Dark blue sea, gray continents, cyan ships, yellow aircraft

## Requirements

- Python 3.7+
- Internet connection (for API access)
- Dependencies: `py5`, `websocket-client`, `requests`

## Setup

### 1. Create a virtual environment (recommended)

```bash
python -m venv py5_env
source py5_env/bin/activate  # On macOS/Linux
# or py5_env\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install py5 websocket-client requests
```

### 3. Run the application

```bash
python moving_circles.py
```

## Data Sources

- **Ships**: [AISStream](https://aisstream.io/) (WebSocket API)
  - Provides real-time Automatic Identification System (AIS) data for ships
  - Uses public API key for demonstration
  
- **Aircraft**: [OpenSky Network](https://opensky-network.org/) (REST API)
  - Provides real-time ADS-B data for aircraft
  - Free tier allows up to 10000 requests per hour

## Visualization Details

- **Background**: Dark blue (#141E30) representing the ocean
- **Continents**: Simplified gray outlines
- **Ships**: Cyan dots with cyan trails (RGBA: 0, 255, 255, 100)
- **Aircraft**: Yellow dots with yellow trails (RGBA: 255, 255, 0, 100)
- **Coordinate system**: Equirectangular projection (simple mapping from lat/lon to screen coordinates)

## Performance Notes

- The application limits visible objects to 50 ships and 50 aircraft to prevent performance issues
- Data is continuously fetched, but only a subset is rendered
- The Java VM may crash if too many objects are drawn (hence the limit)

## Troubleshooting

### "JVMNotRunning" error
- This may occur if the Java Virtual Machine encounters memory issues
- The application includes limits to prevent this, but you can adjust the limits in the code

### WebSocket connection errors
- Check your internet connection
- The AISStream API may have rate limits
- Error messages will appear in the console

### API errors
- OpenSky Network API may be temporarily unavailable
- Check the API status pages for both services

## Code Structure

- `moving_circles.py`: Main application script
  - `websocket_thread()`: Handles AISStream WebSocket connection
  - `aircraft_thread()`: Polls OpenSky Network API
  - `setup()`: Initializes py5 sketch
  - `draw()`: Renders visualization each frame

## License

This project is for educational purposes. Data sources have their own terms of use.

## Future Improvements

- Add interactive controls (zoom, pan, filter by region)
- Store historical data for analysis
- Improve map accuracy with actual geographic data
- Add error handling and retry logic for API failures