#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pylab as P
from matplotlib.dates import HourLocator, DateFormatter, date2num

import numpy as N

import novas
from sun import Sun

from dateutil.rrule import *
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil import tz

from coord import Coord
from position import Position

import time
import datetime as dt
import sys
from types import IntType


def datetime2mjd (t=None):
    t = t or dt.datetime.now()
    return novas.julian_date (t.year, t.month, t.day,
                              t.hour + t.minute/60. + t.microsecond/1e6)

def datetime2seconds (t):
    return time.mktime(t.timetuple())

def equ2alt (site, mjd, ra, dec):
    zd, az, rar, decr = novas.equ2hor (mjd, 0, 0, 0, site,
                                       ra, dec, 0)
    return 90 - zd


class Observability (object):

    def __init__ (self, location, altitude, timezone=-3):
        self.location = location
        self.altitude = altitude

        # timezone stuff
        self.local_tz = tz.tzoffset(None, timezone*3600)
        self._tzinfos = {"LOCAL": self.local_tz}

    def observable (self, objects, begin, end,
                    min_alt=30.0, log=None, by_night=False):
        """
        Returns the number of observable hours for each object in
        'objects' list between 'begin' and 'end'.

        'objects' should be a list of Position's.

        'begin' and 'end' should be a datetime instance. 'end' could
        also be an integer number of days after 'begin'.

        Both 'begin' and 'end' must be local time.

        'min_alt' is the minimun altitude to consider an object
        observable.

        'log' could a filename, which will be overwritten if exists, if
        None would log to stdout.

        'by_night'. If True, returns observable hours separated (as a
        list for each object) for every night, otherwise, returns a
        single number of observable hours for the entire period.
        """

        if log:
            log = open(log, "w")
        else:
            log = sys.stdout

        start_local = begin.replace(tzinfo=self.local_tz)

        if isinstance(end, IntType):
            end = start_local + relativedelta(days=1)

        end_local = end.replace(tzinfo=self.local_tz)

        start_ut = start_local.astimezone(tz.tzutc())
        end_ut   = end_local.astimezone(tz.tzutc())

        start_ut = start_local.astimezone(tz.tzutc())
        end_ut   = end_local.astimezone(tz.tzutc())

        start_mjd = datetime2mjd(start_ut)
        end_mjd   = datetime2mjd(end_ut)
        
        print >> log, "="*80
        print >> log, "Start time (local):", start_local
        print >> log, "End time   (local):", end_local

        print >> log, "="*80
        print >> log, "Start time (UT)   :", start_ut
        print >> log, "End time   (UT)   :", end_ut

        print >> log, "="*80
        print >> log, "Start time (MJD)  :", start_mjd
        print >> log, "End time   (MJD)  :", end_mjd

        novas = self._getNovas()

        sun = Sun({"lat": novas.latitude, "lon": novas.longitude, "alt": novas.height})

        # spanning days
        day = list(rrule(DAILY, dtstart=start_ut, until=end_ut))

        if len(day) == 1:
            # begin/end on the same day, add next/previous day to calc dark time correctly
            if day[0].time() < dt.time(12,00): # before noon, prepend previous day
                day.insert(0, day[0]-relativedelta(days=1))
            else:
                day.append(day[0]+relativedelta(days=1))

        sunrise = {}
        sunset  = {}

        for d in day:
            sunrise[d] = sun.getSunrise(d).replace(tzinfo=self.local_tz)
            sunset[d] = sun.getSunset(d).replace(tzinfo=self.local_tz)

        sunrise_mjd = map(datetime2mjd, sunrise)
        sunset_mjd = map(datetime2mjd, sunset)

        t_ut = N.array(list(rrule(MINUTELY, interval=10,
                                  dtstart=start_ut, until=end_ut)))

        mjd = N.array(map(datetime2mjd, t_ut))

        alt = []
        for obj in objects:
            alt.append(N.array(map(lambda mjd: equ2alt(novas, mjd, obj.ra.H, obj.dec.D), mjd)))
            
        if by_night:
            observables = N.zeros((len(objects), len(day)-1))
        else:
            observables = N.zeros(len(objects))

        print >> log, "="*80
        print >> log, "Observable hours"
        print >> log, "="*80

        # for each night (days - 1)
        for i in range(len(day)-1):

            dark_begin_local = sunset[day[i]]
            dark_end_local = sunrise[day[i+1]]
            
            dark_begin_ut = dark_begin_local.astimezone(tz.tzutc())
            dark_end_ut = dark_end_local.astimezone(tz.tzutc())
            
            dark_begin_mjd = datetime2mjd(dark_begin_ut)
            dark_end_mjd = datetime2mjd(dark_end_ut)
            
            dark = (mjd >= dark_begin_mjd) & (mjd <= dark_end_mjd)

            print >> log, "[%s]" % day[i].astimezone(self.local_tz).date(), \
                  "Sunrise:", dark_begin_local.time(), \
                  "(local) Sunset:", dark_end_local.time(), "(local) (next day)"

            print >> log
            
            for j, obj in enumerate(objects):
                
                observable = (alt[j] >= min_alt) & dark
                observable_hrs = (sum(observable)*10)/60.

                if observable_hrs:
                    observable_hrs += 5/60. # to account border problems

                print >> log, "\t", obj, observable_hrs

                if by_night:
                    observables[j][i] = observable_hrs
                else:
                    observables[j] += observable_hrs

            print >> log

        print >> log, "="*80

        # save log state
        self._last_objects = objects
        self._last_alt = alt
        self._last_ut = t_ut
        self._last_begin_local = start_local
        self._last_end_local = end_local

        return observables


    def plot (self, filename=None):

        for i, obj in enumerate(self._last_objects):
            
            P.figure(i)

            P.plot_date(self._last_ut, self._last_alt[i], xdate=True, fmt='-')

            hourLoc = HourLocator(tz=self.local_tz)
            hourFmt = DateFormatter('%H', tz=self.local_tz)

            P.gca().xaxis.set_major_locator(hourLoc)
            P.gca().xaxis.set_major_formatter(hourFmt)

            P.yticks(N.arange(-90, 100, 10))
            P.grid()

            P.xlabel("Local Hours")
            P.ylabel("Altitude")
            P.title("%s - %s" % (self._last_begin_local.date(), obj))
            
            P.ylim(ymin=0, ymax=90)
            P.xlim(xmin=date2num(self._last_begin_local), xmax=date2num(self._last_end_local))

            P.show()

    def _getNovas (self):
        site = novas.site_info()
        site.latitude = self.location.lat.D
        site.longitude = self.location.long.D
        site.height = self.altitude
        return site



if __name__ == "__main__":

    lna = Observability(Position.fromLongLat("-45 34 03.00", "-22 32 03.00"), 1864, -3)

    print lna.observable([Position.fromRaDec("05:30:00", "-40:00:00"),
                          Position.fromRaDec("10:10:10", "-40:00:00"),
                          Position.fromRaDec("17 56 35.51", "-29 32 21.2")],
                          parse("2008/06/04 20:59"),  parse("2008/06/04 22:51"), 30)

    lna.plot()

    
    
    
