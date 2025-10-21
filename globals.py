
# Global variables

# ============================
# Application info
# ============================
APPVERSION = '2.1.1'
APPNAME = 'OSM to PNG'
APPINFO = 'By Massimo Mula, 2025'

APP_INFOSTRING = f'{APPNAME} v.{APPVERSION} {APPINFO}'

# ============================
# Available map styles
# ============================
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
    "Spinal Map": "https://tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey={APIKEY}",
    # "OpenTopMap": "https://a.tile.opentopomap.org/{z}/{x}/{y}.png"
}

tilesize_kb = 75