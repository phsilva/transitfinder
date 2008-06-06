#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

from sun import Sun

import pylab as P
from matplotlib.dates import HourLocator, DateFormatter, date2num

import numpy as N
import novas

from dateutil.rrule import *
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil import tz

from coords import Position

import time

def datetime2mjd (t):
    return novas.julian_date (t.year, t.month, t.day,
                              t.hour + t.minute/60. + t.microsecond/1e6)

def datetime2seconds (t):
    return time.mktime(t.timetuple())

def equ2alt (mjd, ra, dec):
    zd, az, rar, decr = novas.equ2hor (mjd, 0, 0, 0, site,
                                       ra, dec, 0)
    return 90 - zd


local_tz = tz.tzoffset(None, -3*3600)
tzinfos = {"LOCAL": local_tz}

start_local = parse("2008/06/06 12:00:00 LOCAL", tzinfos=tzinfos)
end_local   = start_local + relativedelta(days=1)

pos = Position("17:57:00 -29:32:00")
ra, dec = pos.dd()

site = novas.site_info()
site.latitude = -22.534
site.longitude = -45.5825
site.height = 1864

#
# end of input
#

print "="*80
print "Start time (local):", start_local
print "End time   (local):", end_local

start_ut = start_local.astimezone(tz.tzutc())
end_ut   = end_local.astimezone(tz.tzutc())

print "="*80
print "Start time (UT)   :", start_ut
print "End time   (UT)   :", end_ut

sun = Sun({"lat": site.latitude, "lon": site.longitude, "alt": site.height})

day = list(rrule(DAILY, dtstart=start_ut, until=end_ut))

sunrise = {}
sunset  = {}

for d in day:
    sunrise[d] = sun.getSunrise(d).replace(tzinfo=local_tz)
    sunset[d] = sun.getSunset(d).replace(tzinfo=local_tz)

sunrise_mjd = map(datetime2mjd, sunrise)
sunset_mjd = map(datetime2mjd, sunset)

print "="*80
print "days between start and end"
print "="*80    

for d in day:
    print d.date(), "Sunrise:", sunrise[d].time(), "(local) Sunset:", \
          sunset[d].time(), "(local)"
    

t_ut = N.array(list(rrule(MINUTELY, interval=10,
                          dtstart=start_ut, until=end_ut)))

mjd = N.array(map(datetime2mjd, t_ut))
alt = N.array(map(lambda m: equ2alt(m, ra/15., dec), mjd))

print "="*80
print "observable hours"
print "="*80

# for each night (days - 1)
for i in range(len(day)-1):

    begin_local = sunset[day[i]]
    end_local = sunrise[day[i+1]]

    begin_ut = begin_local.astimezone(tz.tzutc())
    end_ut = end_local.astimezone(tz.tzutc())

    begin_mjd = datetime2mjd(begin_ut)
    end_mjd = datetime2mjd(end_ut)

    dark = (mjd >= begin_mjd) & (mjd <= end_mjd)
    observable = (alt >= 30.0) & dark
    observable_hrs = sum(observable)
    
    print day[i].astimezone(local_tz).date(), begin_local.time(), \
          end_local.time(), (observable_hrs*10)/60.

    P.plot_date(t_ut, alt, xdate=True, fmt='-')

    hourLoc = HourLocator(tz=local_tz)
    hourFmt = DateFormatter('%H', tz=local_tz)

    P.gca().xaxis.set_major_locator(hourLoc)
    P.gca().xaxis.set_major_formatter(hourFmt)

    P.yticks(N.arange(-90, 100, 10))
    P.grid()

    P.xlabel("Local Hours")
    P.ylabel("Altitude")
    P.title("Altitude curve for %s at %s" % (pos, begin_local.date()))

    P.ylim(ymin=0, ymax=90)
    P.xlim(xmin=date2num(begin_local), xmax=date2num(end_local))

    P.show()



print "="*80



