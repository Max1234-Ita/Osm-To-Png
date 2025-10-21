# import urllib.request
#
# def download_tile(x, y, z, path):
#     url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
#     headers = {"User-Agent": "TileDownloader/1.0 (your_email@example.com)"}
#     r = urllib.request.get(url, headers=headers)
#     if r.status_code == 200:
#         with open(path, "wb") as f:
#             f.write(r.content)
#         print(f"Saved {path}")
#     else:
#         print(f"Failed: {r.status_code}")
#
# download_tile(17640, 12267, 15, "tile_15_17640_12267.png")
