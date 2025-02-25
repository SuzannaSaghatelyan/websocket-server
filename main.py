import asyncio
import websockets
from datetime import datetime, timedelta
import math

def calculate_moon_ra_dec() -> tuple[float, float]:
    now = datetime.utcnow()

    julian_date = 2451545.0 + (now - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0

    days_since_j2000 = julian_date - 2451545.0

    mean_longitude = (218.316 + 13.176396 * days_since_j2000) % 360
    mean_anomaly = (134.963 + 13.064993 * days_since_j2000) % 360

    ecliptic_longitude = (mean_longitude + 6.289 * math.sin(math.radians(mean_anomaly))) % 360

    obliquity = 23.4367

    sin_dec = math.sin(math.radians(ecliptic_longitude)) * math.sin(math.radians(obliquity))
    dec = math.degrees(math.asin(sin_dec))

    y = math.cos(math.radians(ecliptic_longitude))
    x = math.cos(math.radians(obliquity)) * math.sin(math.radians(ecliptic_longitude))
    ra = math.degrees(math.atan2(x, y)) % 360

    ra_hours = ra / 15.0

    return ra_hours, dec

def format_ra_dec(ra: float, dec: float) -> tuple[str, str]:
    ra_str = f"{int(ra):02}:{int((ra % 1) * 60):02}:{int(((ra * 60) % 1) * 60):02}"
    dec_str = f"{'+' if dec >= 0 else '-'}{int(abs(dec)):02}\u00b0 {int((abs(dec) % 1) * 60):02}' {int(((abs(dec) * 60) % 1) * 60):02}\""
    return ra_str, dec_str

async def send_moon_coordinates(websocket):
    try:
        while True:
            ra, dec = calculate_moon_ra_dec()
            ra_str, dec_str = format_ra_dec(ra, dec)

            message = f"RA: {ra_str}, DEC: {dec_str}"
            print(message)
            await websocket.send(message)

            await asyncio.sleep(10)
    except websockets.ConnectionClosed:
        print("Client disconnected")

async def run():
    async with websockets.serve(send_moon_coordinates, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run())

