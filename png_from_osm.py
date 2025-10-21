#
# #  png_from_osm.py
#
# # import io, urllib2, datetime, time, re, random
# import io, datetime, time, re, random
# import urllib.request, urllib.error,  urllib.parse
# import sys
# import os
#
# from PIL import Image, ImageDraw
#
# def usage():
#     helpstring = ("\n"
#                   "Usage: png_from_osm.py xmin xmax ymin ymax osm_zoom_level output_file\n"
#                   "  This routine will create a png file from osm data.  \n"
#                   "  The opencyclemap tiles are hard-coded.  xmin, xmax, ymin, ymax are\n"
#                   "  osm tile indices for the given osm_zoom_level.\n"
#                   "\n"
#                   "  You can refer to webpage http://openstreetmap.gryph.de/bigmap.html\n"
#                   "  to obtain the x/y indices from geographic coordinates\n")
#     print(helpstring)
#
# def get_tiles():
#     if len(sys.argv) != 7:
#         usage()
#         sys.exit()
#
#     #parse command line arguments
#     xmin = None
#     xmax = None
#     ymin = None
#     ymax = None
#     zoom = None
#     output_file_name = None
#
#     i = 1
#     while i < len(sys.argv):
#         arg = sys.argv[i]
#         if xmin is None:
#             try:
#                 xmin = float(arg)
#             except Exception:
#                 print("xmin must be a number.")
#                 sys.exit()
#
#             xmin = int(arg)
#             if xmin != float(arg):
#                 print("xmin must be an integer.")
#                 sys.exit()
#         elif xmax is None:
#             try:
#                 xmax = float(arg)
#             except Exception:
#                 print("xmax must be a number.")
#                 sys.exit()
#
#             xmax = int(arg)
#             if xmax != float(arg):
#                 print("xmax must be an integer.")
#                 sys.exit()
#
#         elif ymin is None:
#             try:
#                 ymin = float(arg)
#             except Exception:
#                 print("ymin must be a number.")
#                 sys.exit()
#
#             ymin = int(arg)
#             if ymin != float(arg):
#                 print("ymin must be an integer.")
#                 sys.exit()
#
#         elif ymax is None:
#             try:
#                 ymax = float(arg)
#             except Exception:
#                 print("ymax must be a number.")
#                 sys.exit()
#
#             ymax = int(arg)
#             if ymax != float(arg):
#                 print("ymax must be an integer.")
#                 sys.exit()
#
#         elif zoom is None:
#             try:
#                 zoom = float(arg)
#             except Exception:
#                 print("osm_zoom_level must be a number.")
#                 sys.exit()
#
#             zoom = int(arg)
#             if zoom != float(arg):
#                 print("osm_zoon_level must be an integer.")
#                 sys.exit()
#
#         elif output_file_name is None:
#             output_file_name = arg
#             if os.path.isfile(output_file_name):
#                 print("%s exists." % output_file_name)
#                 sys.exit()
#         i += 1
#
#     if output_file_name is None:
#         usage()
#         sys.exit()
#
#     #I now (June 2017) need an API key to get opencycltmap tiles without a
#     #watermark
#     #I got this key from thunderforest.com
#     # APIkey = 'you need to get your own API key'
#     APIkey = 'bf4ece5830bd46eabfc8ca6af800d7fe'     # Got from thunderforest.com
#     sURLAPI = '?apikey=%s' % APIkey
#     #for testing
#     #sURLAPI = ''
#
#     #layers = ["http://{abc}.tile.opencyclemap.org/cycle/!z/!x/!y.png%s" % sURLAPI]
#     #There's a new server to pull these tiles from to use the api key
#     # layers = ["https://{abc}.tile.thunderforest.com/cycle/!z/!x/!y.png%s" % sURLAPI]
#     layers = ["https://{abc}.tile.thunderforest.com/cycle/!z/!x/!y.png%s" % sURLAPI]
#     attribution = 'Map data (c) OpenStreetMap, Tiles (c) Andy Allan, compilation Bryan Keith'
#     xsize = xmax - xmin + 1
#     ysize = ymax - ymin + 1
#
#     resultImage = Image.new("RGBA", (xsize * 256, ysize * 256), (0,0,0,0))
#     counter = 0
#     for x in range(xmin, xmax+1):
#         for y in range(ymin, ymax+1):
#             for layer in layers:
#                 url = layer.replace("!x", str(x)).replace("!y", str(y)).replace("!z", str(zoom))
#                 match = re.search("{([a-z0-9]+)}", url)
#                 if match:
#                     url = url.replace(match.group(0), random.choice(match.group(1)))
#                 print(url, "... ")
#
#                 try:
#                     #I tried different combinations to get the api key to work
#                     #req = urllib2.Request(url, headers={'User-Agent': 'BigMap/2.0'})
#                     #req = urllib2.Request(url, headers={'apikey': APIkey})
#                     # req = urllib2.Request(url)    # TODO Remove, not used in Python 3
#                     req = urllib.request.Request(url)
#
#                     #req.add_header("Authorization", "Basic %s" % APIkey)
#                     #req.add_header("auth_appkey", APIkey)
#                     #req.add_header("apikey", APIkey)
#                     # # tile = urllib2.urlopen(req).read()            # TODO Remove, not used in Python 3
#                     tile = urllib.request.urlopen(req).read()
#
#                 except Exception as e:
#                     print("Error", e)
#                     continue
#                 image = Image.open(io.BytesIO(tile))
#                 resultImage.paste(image, ((x-xmin)*256, (y-ymin)*256), image.convert("RGBA"))
#                 counter += 1
#                 if counter == 10:
#                     time.sleep(2)
#                     counter = 0
#
#     draw = ImageDraw.Draw(resultImage)
#     draw.text((5, ysize*256-15), attribution, (0,0,0))
#     del draw
#
#     now = datetime.datetime.now()
#     resultImage.save(output_file_name)
#
# if __name__ == 'main':
#     get_tiles()