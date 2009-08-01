#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-


from observatory import Observatory
from attrdict import AttrDict

from dateutil import tz

import time
import datetime as dt
from types import IntType


class TransitObserver (object):

    @staticmethod
    def observable (planet, observatory, begin, end=1, min_alt=30):

        if isinstance(end, IntType):
            end = begin + dt.timedelta(days=end)

        transits = planet.getTransits(begin, end)

        # for each transit occurring in the given period, check if
        # it's observable at given observatory, above given altitude

        observables = []
        
        for transit_begin, transit_center, transit_end in transits:

            begin_ut = dt.datetime.fromtimestamp(transit_begin).replace(tzinfo=tz.tzutc())
            center_ut = dt.datetime.fromtimestamp(transit_center).replace(tzinfo=tz.tzutc())            
            end_ut   = dt.datetime.fromtimestamp(transit_end).replace(tzinfo=tz.tzutc())

            begin_local = begin_ut.astimezone(observatory.local_tz)
            center_local = center_ut.astimezone(observatory.local_tz)            
            end_local   = end_ut.astimezone(observatory.local_tz)

            observable = observatory.observable([planet.star.position],
                                                begin=begin_local, end=end_local,
                                                min_alt=min_alt,
                                                log="/dev/null")[0]

            percent =  ((observable*3600.0) / planet.transits.duration) * 100
            if percent > 100:
                percent = 100.0
            
            if percent > 0:
                observables.append(AttrDict(planet=planet.name,
                                            begin=begin_local, center=center_local, end=end_local,
                                            observable=observable, percent=percent))

        return observables
                

if __name__ == '__main__':

    from observatory import Observatory
    from planet      import Planet
    from position    import Position    

    lna = Observatory(Position.fromLongLat("-43:00:00", "-22:30:00"),
                      1864, -3)

    planet = Planet.fromFile("../../data/transitsearch.org/HD212301_b.transits.txt")
    planet.star.position = Position.fromRaDec("22:27", "-77:43")

    #t0 = time.clock()
    #t00 = time.time()
    
    observables = TransitObserver.observable(planet, lna, dt.datetime.now(), 10)

    for observable in observables:
        print "%s transit between: %s %s observable for %2.1fh (%3d%%)" % (planet.name, observable.begin, observable.end,
                                                                           observable.observable, observable.percent)
              
    
    #print time.clock()-t0
    #print time.time()-t00
    

    
