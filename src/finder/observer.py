#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-


from observability import Observability

from dateutil import tz

import time
import datetime as dt
from types import IntType


class Observer (object):

    @staticmethod
    def observableTransits (planet, location, alt, timezone,
                            obs_begin, obs_end=1, min_alt=30):

        # candy, to allow obs_end to be a integer number of days
        if isinstance(obs_end, IntType):
            obs_end = obs_begin + dt.timedelta(days=obs_end)

        transits = planet.getTransits(obs_begin, obs_end)

        site = Observability(location, alt, timezone)

        # for each transit occurring in the given period, check if it's observable at
        # given location, above given altitude

        #print "[%s]" % planet.name

        observables = []
        
        for transit_begin, transit_end in zip(transits.begin, transits.end):

            begin_ut = dt.datetime.fromtimestamp(transit_begin).replace(tzinfo=tz.tzutc())
            end_ut   = dt.datetime.fromtimestamp(transit_end).replace(tzinfo=tz.tzutc())

            begin_local = begin_ut.astimezone(site.local_tz)
            end_local = end_ut.astimezone(site.local_tz)

            observable = site.observable([planet.star.position],
                                         begin=begin_local, end=end_local, min_alt=min_alt,
                                         log="/dev/null")[0]

            percent =  (observable*3600.0) / planet.transits.duration
            if percent > 1:
                percent = 1.0

            percent *= 100

            if percent > 0:
                print "%s transit between:" % planet.name, begin_local, end_local, "observable for", "%2.1fh" % observable, "(%3d%%)" % percent

            #if percent > 0:
            #    site.plot()

            if percent > 0:
                observables.append("%s transit between: %s %s observable for %2.1fh (%3d%%)\n" % (planet.name, begin_local, end_local,
                                                                                                  observable, percent))

        #print
        return observables
                

if __name__ == '__main__':

    from coord    import Coord
    from position import Position
    from planet   import Planet

    p = Planet.fromFile("../../data/transitsearch.org/HD212301_b.transits.txt")
    p.star.position = Position.fromRaDec("22:27", "-77:43")

    location = Position.fromLongLat("-43:00:00", "-22:30:00")

    #t0 = time.clock()
    #t00 = time.time()
    Observer.observableTransits(p, location, 1864, -3, dt.datetime.now(), 10)
    #print time.clock()-t0
    #print time.time()-t00
    

    
