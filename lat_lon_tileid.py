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
    # print(f"x: {x_tile}, y = {y_tile}")
    return x_tile, y_tile

