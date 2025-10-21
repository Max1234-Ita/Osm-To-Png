import math

zoom = 16
coordinates=[(45.57327, 9.07516),
             (45.37989, 9.32301)
             ]


def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2 ** int(zoom)
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    print(f"x: {x_tile}, y = {y_tile}")
    return x_tile, y_tile


# for c in coordinates:
#     latlon_to_tile(c[0], c[1], zoom)

# import math
# import os
# import requests


# def latlon_to_tile(lat, lon, zoom):
#     """Converte coordinate lat/lon in coordinate tile x, y per un dato zoom."""
#     lat_rad = math.radians(lat)
#     n = 2.0 ** zoom
#     x = int((lon + 180.0) / 360.0 * n)
#     y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
#     return x, y


# import math
# import os
# import requests
#
#
# def latlon_to_tile(lat, lon, zoom):
#     """Converte coordinate lat/lon in coordinate tile x, y per un dato zoom."""
#     lat_rad = math.radians(lat)
#     n = 2.0 ** zoom
#     x = int((lon + 180.0) / 360.0 * n)
#     y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
#     return x, y


# def download_opentopomap_tile(lat, lon, zoom):
#     """
#     Scarica la tile OpenTopoMap corrispondente a una coordinata (lat, lon) e zoom.
#
#     lat, lon: coordinate geografiche
#     zoom: livello di zoom (es. 10–17)
#     out_dir: directory di destinazione
#     """
#
#     x, y = latlon_to_tile(lat, lon, zoom)
#     url = f"https://b.tile.opentopomap.org/{zoom}/{x}/{y}.png"
#
#     print(f"Scarico tile per lat={lat}, lon={lon}, zoom={zoom}")
#     print(f"→ URL: {url}")
#
#     r = requests.get(url, timeout=10)
#     return r
#
#
# # ESEMPIO: Piazza Duomo, Milano
# download_opentopomap_tile(lat=45.4642, lon=9.1916, zoom=16)
