
#  png_from_osm.py

# import io, urllib2, datetime, time, re, random
import io, datetime, time, re, random
import urllib.request, urllib.error,  urllib.parse
import sys
import os
from dataclasses import replace

from random import randrange, choice
from time import sleep

from PIL import Image, ImageDraw

import globals
import inifile_access

MAP_STYLES = globals.map_styles
config = inifile_access.IniManager('config.ini')

def usage():
    helpstring = ("\n"
                  "Usage: png_from_osm.py xmin xmax ymin ymax osm_zoom_level output_file\n"
                  "  This routine will create a png file from osm data.  \n"
                  "  The opencyclemap tiles are hard-coded.  xmin, xmax, ymin, ymax are\n"
                  "  osm tile indices for the given osm_zoom_level.\n"
                  "\n"
                  "  You can refer to webpage http://openstreetmap.gryph.de/bigmap.html\n"
                  "  to obtain the x/y indices from geographic coordinates\n")
    print(helpstring)

def get_tiles(xmin=None, xmax=None, ymin=None, ymax=None, zoom=None, style=None, output_file_name=None):
    def _get_mapnik_tile(x, y, z):
        # osm_url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        osm_url = MAP_STYLES[style]
        osm_url = osm_url.replace('{z}', str(z))
        osm_url = osm_url.replace('{x}', str(x))
        osm_url = osm_url.replace('{y}', str(y))
        headers = {"User-Agent": f"TileDownloader/1.0 ({osmemail})"}
        try:
            sleep(0.3)
            r = urllib.request.Request(osm_url, headers=headers)
            t = urllib.request.urlopen(r).read()
        except Exception as e:
            print("Error", e)
            t = None
        return t

    # def _get_opentopomap_tile(x, y, z):       # TODO - not used so far
    #     t= None
    #     otm_url = MAP_STYLES["OpenTopMap"]
    #     # server = choice(['a', 'b', 'c'])
    #     # otm_url = otm_url.replace('{a|b|c}', server)
    #     otm_url = otm_url.replace('{x}', str(x))
    #     otm_url = otm_url.replace('{y}', str(y))
    #     otm_url = otm_url.replace('{z}', str(z))
    #     try:
    #         sleep(0.5)
    #         r = urllib.request.Request(otm_url)
    #         t = urllib.request.urlopen(r).read()
    #     except Exception as e:
    #         print("Error", e)
    #         t = None
    #     return t

    def _get_thundeforest_tile(x, y, z, api_key):
        url = layer.replace("{x}", str(x)).replace("{y}", str(y)).replace("{z}", str(zoom))
        url = url.replace('{APIKEY}', api_key)
        match = re.search("{([a-z0-9]+)}", url)
        if match:
            url = url.replace(match.group(0), random.choice(match.group(1)))
        try:
            req = urllib.request.Request(url)
            t = urllib.request.urlopen(req).read()
        except Exception as e:
            print("Error", e)
            t = None

        return t

    # -------------------------------------------------------------------------------------------------------
    if None in [xmin, xmax, ymin,ymax, zoom, style]:
        print('xmin, xmax, ymin,ymax, zoom, must be integers; style must be a string. ')
        sys.exit(-1)

    if output_file_name is None:
        print('Please provide a valid output file name.')
        sys.exit(-1)
    elif os.path.isfile(output_file_name):
            print("%s exists and will be overwritten" % output_file_name)

    if output_file_name is None:
        usage()
        sys.exit()

    # Since 2017, an API key is required to get ThunderForest tiles without a watermark.
    apikey = config.getvalue('tile_download', 'apikey')     # Get API Key from thunderforest.com
    osmemail = config.getvalue('tile_download', 'osm_email')   # Provide a valid email, to get Mapnik tiles
    s_urlapi = '?apikey=%s' % apikey

    layer = MAP_STYLES[style]
    attribution = 'Map data (c) OpenStreetMap, Tiles (c) Andy Allan, compilation Bryan Keith'
    xsize = xmax - xmin + 1
    ysize = ymax - ymin + 1

    result_image = Image.new("RGBA", (xsize * 256, ysize * 256), (0,0,0,0))
    counter = 0
    n_tiles = (xmax - xmin + 1) * (ymax-ymin + 1)
    print(f'\nDownloading {n_tiles} tiles')
    dl_count = 1
    for x in range(xmin, xmax+1):
        for y in range(ymin, ymax+1):
            try:
                print(f' -> Getting {style} tile {dl_count}/{n_tiles} ')
                if style == "Mapnik (OSM)":
                    tile = _get_mapnik_tile(x,y,zoom)
                    # Put some additional wait time to avoid overloading the OSM server
                    if dl_count %10 == 0:
                        print('    ___')
                        time.sleep(randrange(8))
                        counter = 0
                    if counter >= 6:
                        sl = randrange(2)
                        if sl > 0:
                            print('    ...')
                            sleep(randrange(3))
                            counter = 0
                # elif style == 'OpenTopMap':
                #     # Get OpenTopoap tiles
                #     if int(zoom) <= 17:
                #         tile = _get_opentopomap_tile(x, y, zoom)
                #     else:
                #         print(f'Images at zoom {zoom} are not available in OpenTopoMap. Please select a different style')
                #         sys.exit(-2)
                else:
                    # Get ThunderForest tiles
                    tile = _get_thundeforest_tile(x, y, zoom, apikey)
            except Exception:
                continue
            image = Image.open(io.BytesIO(tile))
            result_image.paste(image, ((x-xmin)*256, (y-ymin)*256), image.convert("RGBA"))

            #  ------ Put some anti-overload delay -----
            counter += 1
            if dl_count % 10  == 0:
                time.sleep(2)
                counter = 0

            elif style == 'Mapnik (OSM)':
                if dl_count % 99 == 0:
                    print('Waiting some time to avoid overloading OSM server...')
                    time.sleep(30)
                time.sleep(0.5)
            dl_count +=1

    draw = ImageDraw.Draw(result_image)
    draw.text((5, ysize*256-15), attribution, (0,0,0))
    del draw

    now = datetime.datetime.now()
    result_image.save(output_file_name)
    return dl_count -1

if __name__ == 'main':
    get_tiles()