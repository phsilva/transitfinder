#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# teste de branch do git
# de novo

from position import Position

from observatory     import Observatory
from transitobserver import TransitObserver
from planetdb        import PlanetDb

import time
import datetime as dt

db   = PlanetDb()
site = Observatory(Position.fromLongLat("-43:00:00", "-22:30:00"), 1864, -3)

t0 = time.clock()

map(lambda planet: TransitObserver.observable(planet, site, dt.datetime.now(), 10), db.planets)

print time.clock()-t0

