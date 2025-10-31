
# Global variables

# ----------------
# Application info
# ----------------
APPVERSION = '2.1.1'
APPNAME = 'OSM to PNG'
APPINFO = 'By M. Mula, 2025'

APP_INFOSTRING = f'{APPNAME} v.{APPVERSION} {APPINFO}'
APP_ICON_ICO = 'osm2png.ico'
APP_ICON_PNG = 'osm2png.png'

# --------------------
# Available map styles
# --------------------


map_styles = {
    "Mapnik (OSM)": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "Cycle Map": "https://tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Transport": "https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Landscape": "https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Outdoors": "https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Neighbourhood": "https://tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Pioneer": "https://tile.thunderforest.com/pioneer/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Mobile Atlas": "https://tile.thunderforest.com/mobile-atlas/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Atlas": "https://tile.thunderforest.com/atlas/{z}/{x}/{y}.png?apikey={APIKEY}",
    "Spinal Map": "https://tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey={APIKEY}"
    # "OpenTopMap": "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
}

# Styles are described in the dict below. The key is the name that will be dispalyed in the Coordinate Picker.
# The realted value is orgaised as a list where the elements represent:
#   [0]     Tile provider (i.e. "OpenStreetMap"
#   [1]     Provider's website
#   [2]     Tile width (pixels)
#   [3]     Tile height (pixels).
styles_info = {
"Mapnik (OSM)": ["OpenStreetMap", "https://www.openstreetmap.org", 256, 256],
    "Cycle Map": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Transport": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Landscape": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Outdoors": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Neighbourhood": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Pioneer": ["Thunderforest", "https://www.thunderforest.com",  256, 256],
    "Mobile Atlas": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Atlas": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    "Spinal Map": ["Thunderforest", "https://www.thunderforest.com", 256, 256],
    # "OpenTopMap": ["OpenTopoMap", "https://opentopomap.org", 256, 256]
}

web_sites = {
    "OpenStreetMap": "https://www.openstreetmap.org",
    "Thunderforest": "https://www.thunderforest.com",
    "OpenTopoMap": "https://opentopomap.org",
}

tilesize_kb = 75