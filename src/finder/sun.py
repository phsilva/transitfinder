#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import ephem
import datetime as dt
from coords.position import dms


class Sun (object):

    def __init__ (self, site):
        self.site = site
        self.sun = ephem.Sun()

    def _makeEphemSite(self, date):
        site = ephem.Observer()
        site.lat = '%s%d:%d:%.2f' % dms(self.site['lat'])
        site.lon = '%s%d:%d:%.2f' % dms(self.site['lon'])
        site.alt = self.site['alt']
        site.date= date
        return site

    def getSunrise(self, date):
        self.sun.compute(self._makeEphemSite(date))
        return self.sun.rise_time.datetime()

    def getSunset(self, date):
        self.sun.compute(self._makeEphemSite(date))
        return self.sun.set_time.datetime()

    def getTimes(self, date):
        return (self.getSunrise(date), self.getSunset(date))

if __name__ == "__main__":

    s = Sun({"lat": -22.534, "lon": -45.5825, "alt": 1864})
    print s.getTimes(dt.date.today())
    
