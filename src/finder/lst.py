import time
import novas
from coord import Coord

now = time.gmtime()

#mjd = novas.julian_date (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour + now.tm_min/60.0 + now.tm_sec/3600.0)
mjd = novas.julian_date (2008, 06, 04, 21 + 30/60.0)

mobl, tobl, eqeq, psi, eps = novas.earthtilt (mjd)

gst = novas.sidereal_time (mjd, 0, eqeq)
lst = (gst + (-45.5 / 15.0)) % 24

print "MJD:", mjd
print "GST:", Coord.fromHMS(gst)
print "LST:", Coord.fromHMS(lst)
