# #!/usr/bin/python
# #approximately calculate the meters/degree of longitude at the specified
# #latitude
# #see https://knowledge.safe.com/articles/725/calculating-accurate-length-in-meters-for-lat-long.html
# import math
# import sys
#
# def usage():
#     print("Usage: meter_per_degree_latiude.py latitude_in_degrees")
#     print("    This routine will write out the approximate number of meters per")
#     print("    degree of longitude for the given latitude.")
#     print("    meters are hard-coded")
#     return
#
#
# #parse command line arguments
# if len(sys.argv) != 2:
#     usage()
#     sys.exit()
#
# lat = None
# i = 1
# while i < len(sys.argv):
#     arg = sys.argv[i]
#     if lat is None:
#         try:
#             lat = float(arg)
#         except Exception:
#             print("latitude_in_degrees must be a number.")
#             sys.exit()
#     i += 1
#
# #convert latitude degrees to radians
# pi = math.pi
# rlat = lat * pi / 180
#
# #calculate meters/degree of longitude
# mlon = 111412.84 * math.cos(rlat) - 93.5 * math.cos(3 * rlat)
# mlat = 111132.92 - 559.82 * math.cos(2 * rlat) + 1.175 * math.cos(4 * rlat)
#
# print("%f meters/degree of longitude at %f degrees latitude" % (mlon, lat))
# print("%f meters/degree of latitude at %f degrees latitude" % (mlat, lat))
