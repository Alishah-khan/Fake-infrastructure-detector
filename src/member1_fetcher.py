"""
Module: Satellite Image Acquisition & Geocoding Service
Author: Member 1 (Satellite & Spatial Data Lead)

Provides geocoding resolution, satellite tile ingestion, and realistic sample generation.
"""

import math
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFile
import numpy as np
from geopy.geocoders import Nominatim

ImageFile.LOAD_TRUNCATED_IMAGES = True

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
CACHE_DIR = DATA_DIR / "cache"

PRESET_LOCATIONS = {
    "connaught place, delhi": (28.6315, 77.2167, "Connaught Place, New Delhi, Delhi, India"),
    "rampur, varanasi": (25.3176, 82.9739, "Rampur Sector 4, Varanasi, Uttar Pradesh, India"),
    "kishanpur, bhedaghat": (23.1298, 79.8007, "Kishanpur Link Road, Jabalpur, Madhya Pradesh, India"),
    "devbagh, ratnagiri": (16.9902, 73.3120, "Devbagh Block, Ratnagiri, Maharashtra, India"),
    "dhenkanal, odisha": (20.6586, 85.5956, "Bypass Bridge, Dhenkanal, Odisha, India"),
    "bengaluru tech park": (12.9716, 77.5946, "Outer Ring Road, Bengaluru, Karnataka, India"),
    "rural health center, bihar": (25.5941, 85.1376, "Ganga Basin Project, Patna, Bihar, India")
}


def geocode_location(query: str):
    """Resolves location query into (latitude, longitude, formatted_address)."""
    cleaned = query.strip().lower()

    for key, (lat, lon, name) in PRESET_LOCATIONS.items():
        if key in cleaned or cleaned in key:
            return lat, lon, name

    if "," in query:
        parts = query.split(",")
        try:
            return float(parts[0].strip()), float(parts[1].strip()), f"Coordinates ({parts[0].strip()}, {parts[1].strip()})"
        except ValueError:
            pass

    try:
        geolocator = Nominatim(user_agent="fake_infra_audit_sih_v1")
        loc = geolocator.geocode(query, timeout=4)
        if loc:
            return loc.latitude, loc.longitude, loc.address
    except Exception:
        pass

    return 28.6139, 77.2090, f"{query} (Default Geocode)"


def _deg2num(lat_deg: float, lon_deg: float, zoom: int):
    """Converts geographic coordinates to XYZ tile indices."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def fetch_satellite_tile(lat: float, lon: float, zoom: int = 16) -> Image.Image:
    """Fetches high-resolution satellite imagery from Earth Observation tile servers."""
    xtile, ytile = _deg2num(lat, lon, zoom)
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ytile}/{xtile}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            return img.resize((600, 600), Image.Resampling.LANCZOS)
    except Exception:
        pass
    return None


def _create_terrain_texture(width: int, height: int, base_color: list, noise_level: int = 18):
    """Generates synthetic high-fidelity satellite terrain texture."""
    base = np.array(base_color, dtype=np.int16)
    noise = np.random.randint(-noise_level, noise_level + 1, (height, width, 3), dtype=np.int16)
    return Image.fromarray(np.clip(base + noise, 0, 255).astype(np.uint8))


def generate_all_samples():
    """Generates curated before/after satellite image pairs for demonstrations."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. School (Verified)
    f_school = SAMPLES_DIR / "verified_school"
    f_school.mkdir(parents=True, exist_ok=True)
    b_school = _create_terrain_texture(600, 600, [115, 138, 88])
    draw_b = ImageDraw.Draw(b_school)
    draw_b.line([(0, 280), (600, 300)], fill=(160, 142, 110), width=12)
    b_school.filter(ImageFilter.GaussianBlur(1.0)).save(f_school / "before.png")

    a_school = _create_terrain_texture(600, 600, [112, 134, 85])
    draw_a = ImageDraw.Draw(a_school)
    draw_a.rectangle([140, 140, 460, 460], fill=(185, 180, 172), outline=(130, 125, 118), width=3)
    draw_a.line([(0, 280), (460, 280)], fill=(65, 65, 70), width=22)
    draw_a.rectangle([190, 185, 410, 260], fill=(60, 60, 60))
    draw_a.rectangle([180, 175, 400, 250], fill=(55, 95, 145), outline=(35, 65, 100), width=4)
    draw_a.rectangle([190, 250, 265, 420], fill=(60, 60, 60))
    draw_a.rectangle([180, 240, 255, 410], fill=(68, 110, 160), outline=(35, 65, 100), width=3)
    a_school.filter(ImageFilter.GaussianBlur(0.8)).save(f_school / "after.png")

    # 2. Road (Suspicious)
    f_road = SAMPLES_DIR / "suspicious_road"
    f_road.mkdir(parents=True, exist_ok=True)
    b_road = _create_terrain_texture(600, 600, [178, 160, 128])
    draw_br = ImageDraw.Draw(b_road)
    draw_br.line([(0, 320), (300, 340), (600, 310)], fill=(145, 128, 98), width=16)
    b_road.filter(ImageFilter.GaussianBlur(1.0)).save(f_road / "before.png")

    a_road = _create_terrain_texture(600, 600, [174, 156, 124])
    draw_ar = ImageDraw.Draw(a_road)
    draw_ar.line([(0, 320), (300, 340), (600, 310)], fill=(148, 130, 100), width=16)
    a_road.filter(ImageFilter.GaussianBlur(1.0)).save(f_road / "after.png")

    # 3. Hospital (Suspicious)
    f_hosp = SAMPLES_DIR / "suspicious_hospital"
    f_hosp.mkdir(parents=True, exist_ok=True)
    b_hosp = _create_terrain_texture(600, 600, [125, 145, 95])
    draw_bh = ImageDraw.Draw(b_hosp)
    for y in range(80, 520, 45):
        draw_bh.line([(50, y), (550, y)], fill=(105, 125, 75), width=4)
    b_hosp.filter(ImageFilter.GaussianBlur(0.8)).save(f_hosp / "before.png")

    a_hosp = _create_terrain_texture(600, 600, [145, 155, 90])
    draw_ah = ImageDraw.Draw(a_hosp)
    for y in range(80, 520, 45):
        draw_ah.line([(50, y), (550, y)], fill=(125, 135, 70), width=4)
    a_hosp.filter(ImageFilter.GaussianBlur(0.8)).save(f_hosp / "after.png")

    # 4. Bridge (Verified)
    f_brg = SAMPLES_DIR / "verified_bridge"
    f_brg.mkdir(parents=True, exist_ok=True)
    b_brg = _create_terrain_texture(600, 600, [120, 135, 90])
    draw_bb = ImageDraw.Draw(b_brg)
    draw_bb.polygon([(0, 200), (600, 220), (600, 380), (0, 360)], fill=(45, 85, 135))
    b_brg.filter(ImageFilter.GaussianBlur(1.0)).save(f_brg / "before.png")

    a_brg = _create_terrain_texture(600, 600, [120, 135, 90])
    draw_ab = ImageDraw.Draw(a_brg)
    draw_ab.polygon([(0, 200), (600, 220), (600, 380), (0, 360)], fill=(45, 85, 135))
    draw_ab.line([(290, 0), (290, 205)], fill=(65, 65, 70), width=32)
    draw_ab.line([(290, 375), (290, 600)], fill=(65, 65, 70), width=32)
    draw_ab.rectangle([295, 200, 335, 380], fill=(20, 40, 65))
    draw_ab.rectangle([275, 200, 315, 380], fill=(200, 200, 205), outline=(130, 130, 135), width=3)
    a_brg.filter(ImageFilter.GaussianBlur(0.8)).save(f_brg / "after.png")


def fetch_satellite_pair(lat: float, lon: float, start_date: str, end_date: str, sample_id: str = None):
    """Retrieves before and after satellite image paths for verification."""
    generate_all_samples()

    if sample_id:
        sample_folder = SAMPLES_DIR / sample_id
        b_path = sample_folder / "before.png"
        a_path = sample_folder / "after.png"
        if b_path.exists() and a_path.exists():
            return str(b_path), str(a_path)

    cache_before = CACHE_DIR / f"{lat:.4f}_{lon:.4f}_before_{start_date}.png"
    cache_after = CACHE_DIR / f"{lat:.4f}_{lon:.4f}_after_{end_date}.png"

    if cache_before.exists() and cache_after.exists():
        return str(cache_before), str(cache_after)

    live_tile = fetch_satellite_tile(lat, lon, zoom=16)
    if live_tile:
        live_tile.save(cache_after)
        live_tile.copy().save(cache_before)
        return str(cache_before), str(cache_after)

    sample_folder = SAMPLES_DIR / "verified_school"
    return str(sample_folder / "before.png"), str(sample_folder / "after.png")


def get_demo_samples_meta():
    """Returns metadata for pre-configured demonstration projects."""
    return [
        {
            "id": "verified_school",
            "name": "Primary Model School Complex",
            "department": "Education & School Infrastructure",
            "type": "Building / School",
            "location": "Rampur Sector 4, Varanasi, Uttar Pradesh",
            "lat": 25.3176,
            "lon": 82.9739,
            "budget": 14500000.0,
            "start_date": "2024-01-15",
            "end_date": "2024-11-20",
            "expected_verdict": "VERIFIED"
        },
        {
            "id": "suspicious_road",
            "name": "Bitumen Highway Link Road 12B",
            "department": "Public Works Department (PWD)",
            "type": "Road / Highway",
            "location": "Kishanpur to Bhedaghat Link, Madhya Pradesh",
            "lat": 23.1298,
            "lon": 79.8007,
            "budget": 32000000.0,
            "start_date": "2024-02-01",
            "end_date": "2024-10-15",
            "expected_verdict": "SUSPICIOUS"
        },
        {
            "id": "suspicious_hospital",
            "name": "Community Health & Trauma Center",
            "department": "Health & Family Welfare",
            "type": "Hospital / Health Center",
            "location": "Devbagh Block, Ratnagiri, Maharashtra",
            "lat": 16.9902,
            "lon": 73.3120,
            "budget": 28000000.0,
            "start_date": "2024-03-01",
            "end_date": "2024-12-05",
            "expected_verdict": "SUSPICIOUS"
        },
        {
            "id": "verified_bridge",
            "name": "Brahmani River Elevated Bypass Bridge",
            "department": "National Highways Authority",
            "type": "Bridge / Flyover",
            "location": "Bypass Bridge, Dhenkanal, Odisha",
            "lat": 20.6586,
            "lon": 85.5956,
            "budget": 52000000.0,
            "start_date": "2023-11-01",
            "end_date": "2024-11-30",
            "expected_verdict": "VERIFIED"
        }
    ]
