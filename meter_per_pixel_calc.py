# #!/usr/bin/python
# #calculate the distance/pixel of osm tiles at your desired tile zoom and
# #latitude
# #see http://wiki.openstreetmap.org/wiki/Zoom_levels
# import math
# import sys
#
# def usage():
#     print("Usage: meter_per_pixel_calc.py latitude_in_degrees osm_zoom_level")
#     print("    This routine will write out the approximate numbers of meters per")
#     print("    pixel for the given latitude and openstreetmap tiled zoom level.")
#     print("    meters are hard-coded")
#     return
#
# if len(sys.argv) != 3:
#     usage()
#     sys.exit()
# #parse command line arguments
# lat = None
# z = None
# i = 1
# while i < len(sys.argv):
#     arg = sys.argv[i]
#     if lat is None:
#         try:
#             lat = float(arg)
#         except Exception:
#             print("latitude_in_degrees must be a number.")
#             sys.exit()
#     elif z is None:
#         try:
#             z = float(arg)
#         except Exception:
#             print("osm_zoom_level must be an integer.")
#             sys.exit()
#
#         z = int(arg)
#         if z != float(arg):
#             print("osm_zoom_level must be an integer.")
#             sys.exit()
#     i += 1
#
# if z is None:
#     usage()
#     sys.exit()
#
# #set the openstreetmap tile zoom level you're interested in
# #z = 14
# #set the circumference of the earth at the equator in meters (or whatever
# #unit you want per pixel)
# C = 40075.16 * 1000
# #set the latitude that we're interested in (in degrees)
# #lat = 0
# #convert latitude degrees to radians
# pi = math.pi
# y = lat * pi / 180
# #calculate distance/pixel
# S = C * math.cos(y) / 2 ** (z + 8)
# print(S)