#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import ephem
from coord import Coord

import datetime as dt


class Sun (object):

    def __init__ (self, site):
        self.site = site
        self.sun = ephem.Sun()

    def _makeEphemSite(self, date):
        site = ephem.Observer()
        
        site.lat = Coord.fromD(self.site["lat"]).strfcoord('%(d)02d:%(m)02d:%(s).2f', signed=True)
        site.long = Coord.fromD(self.site["lon"]).strfcoord('%(d)02d:%(m)02d:%(s).2f', signed=True)
        site.elevation = self.site["alt"]
        site.date = date
        return site

    def getSunrise(self, date):
        observer = self._makeEphemSite(date)
        self.sun.compute(observer)
        return observer.next_rising(self.sun).datetime()

    def getSunset(self, date):
        observer = self._makeEphemSite(date)
        self.sun.compute(observer)
        return observer.next_setting(self.sun).datetime()

    def getTimes(self, date):
        return (self.getSunrise(date), self.getSunset(date))

if __name__ == "__main__":

    s = Sun({"lat": -22.534, "lon": -45.5825, "alt": 1864})
    print s.getTimes(dt.date.today())
    
