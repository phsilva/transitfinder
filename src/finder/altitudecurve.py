#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import numpy as N
import pylab as P
import novas
import datetime as dt
import time
import math

from coords import AstroDate
from coords import Position

from matplotlib.dates import HourLocator, DateFormatter, date2num

from types import IntType, FloatType, LongType

from sun import Sun


class AltitudeCurve (object):

    def __init__ (self, site, objects, start, end=1):
        self.site = site
      
        # convert object to decimal degrees to speed-up things
        self.coords = [] # decimal degrees
        self.objects = []
        
        for obj in objects:
            #if isinstance(obj, Position):
            self.coords.append(obj.dd())
            self.objects.append(obj)
            #else:
            #    self.coords.append(obj)
            #    self.objects.append(Position(obj))

        self.n_objs = len(self.objects)            

        # start at 12:00:00 AM of the given date
        self.start = start
        self.startJD = AstroDate(self.start)
        self.startSec = time.mktime(self.start.timetuple())
                
        if type(end) in (IntType, FloatType, LongType):
            end = self.start + dt.timedelta(days=end)

        # end at 12:00:00 AM of the given date
        self.end = end

        self.endJD = AstroDate(self.end)
        self.endSec = time.mktime(self.end.timetuple())

        # private
        self.updated = False
        
        self.n  = 24*6
        self.range = self._calcRange(self.start, self.end)

        self.t, self.dt  = N.linspace(self.startJD.mjd, self.endJD.mjd, self.n, retstep=True)
        # convert dt to seconds
        self.dt *= 86400

        # altitudes for each object
        self.h  = N.zeros((self.n_objs, self.n), dtype=N.float32)

        self.sunrises = {}
        self.sunsets = {}
        self.midnights = {}

    def _makeNovasSite(self):
        site = novas.site_info()
        site.latitude = self.site['lat']
        site.longitude = self.site['lon']
        site.height = self.site['alt']
        return site

    def _calcRange(self, start, end):
        r = (self.end - self.start)
        r = float(86400*r.days + r.seconds + r.microseconds/1e6)
        return r

    def _index(self, t):
        t = time.mktime(t.timetuple())
        return int(round(((t - self.startSec) / self.dt)))

    def _update (self):

        site = self._makeNovasSite()

        for i, p in enumerate(self.coords):
            for j, t in enumerate(self.t):
                zd, az, rar, decr = novas.equ2hor (t, 0, 0, 0, site,
                                                   p[0]/15., p[1], 0)
                self.h[i][j] = 90 - zd

        # calculate sunrises/sunsets
        sun = Sun(self.site)
        
        for i in range((self.end - self.start).days+1):
            next_day = self.start.date()+dt.timedelta(days=i)
            self.sunrises[next_day] = sun.getSunrise(next_day)
            self.sunsets[next_day]  = sun.getSunset(next_day)

    def observable (self, start=None, end=None, zenital_distance_limit=30.0, galactic_latitude_limit=None, verbose=True):

        if not self.updated:
            self._update()

        start = start or self.start
        end   = end   or self.end

        if start < self.start:
            start = self.start

        if end > self.end:
            end = self.end

        if end < self.start:
            return 0

        observable = N.zeros(self.n_objs, dtype=N.float32)

        if verbose:
            print "Computing observability: from %s to %s" % (start.strftime("%d/%m/%Y %H:%M:%S"), end.strftime("%d/%m/%Y %H:%M:%S"))
        
        for i in range((end - start).days):
            today    = start+dt.timedelta(days=i)
            tomorrow = today+dt.timedelta(days=1)

            sunset  = self.sunsets[today.date()]
            sunrise = self.sunrises[tomorrow.date()]

            if verbose:
                print "\t[%s] sun set  at: %s" % (sunset.strftime("%d/%m/%Y"), sunset.strftime("%H:%M"))
                print "\t[%s] sun rise at: %s" % (sunrise.strftime("%d/%m/%Y"), sunrise.strftime("%H:%M"))

            startIdx = self._index(sunset)
            endIdx   = self._index(sunrise)

            for i, p in enumerate(self.objects):

                # check if galactic latitude limit was given
                if galactic_latitude_limit and abs(p.galactic()[1]) > galactic_latitude_limit:
                    if verbose:
                        print "\t[%s] outside galactic latitude limit %s" % (p, p.galactic())
                    continue
                
                area = self.h[i][startIdx:endIdx]
                area = area[area >= zenital_distance_limit]
                area = (area.size*self.dt)/3600.
                observable[i] += area

                if verbose:
                    print "\tObservable hours for [%s]: %.2f" % (p, area)

        if verbose:
            print
            for i, p in enumerate(self.objects):
                print "Total observable hours for [%s]: %.2f" % (p, observable[i])
        
        return observable.tolist()

    def plot (self):

        if not self.updated:
            self._update()
        
        f = P.figure()

        for i in range(self.n_objs):
            P.plot_date(self.t, self.h[i], xdate=True, ydate=False, fmt='-')

        hourLoc = HourLocator()
        hourFmt = DateFormatter('%H')

        P.gca().xaxis.set_major_locator(hourLoc)
        P.gca().xaxis.set_major_formatter(hourFmt)

        P.gca().xaxis.grid(linestyle=':')
        P.gca().yaxis.grid(linestyle=':')

        P.axhline(30, ls='-.', color='r', lw=2)

        P.yticks(N.arange(-90, 100, 10))
        P.ylim(ymin=-90, ymax=90)
        
        P.show()

    def __getitem__(self, t):
        if not self.updated:
            self._update()

        i = self._index(t)

        if i > 0 and i < self.h.size:
            return self.h[i]
        else:
            return 0

    def __iter__(self):
        return self.h.__iter__()

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 4:
            print "Usage: %s 'hh:mm:ss.s -dd:mm:ss.s' dd/mm/yy days" % sys.argv[0]
            sys.exit(1)

    c = AltitudeCurve({"lat": -22.534, "lon": -45.5825, "alt": 1864},
                      [Position(sys.argv[1])],
                      start=dt.datetime.strptime(sys.argv[2], "%d/%m/%Y %H:%M"), end=int(sys.argv[3]))

    c.observable(zenital_distance_limit=30.0, galactic_latitude_limit=None)    
    c.plot()
                      
