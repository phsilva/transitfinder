#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

from position import Position
from planet   import Planet

from observatory     import Observatory
from transitobserver import TransitObserver

import datetime as dt
import os

planets = [
    ("transitsearch.org/HD17156__b.transits.txt",  "02 49 44.4875",  "+71 45 11.636"),  
    ("transitsearch.org/HAT-P-2__b.transits.txt",  "16 20 36.3572",  "+41 02 53.101"),
    ("transitsearch.org/HD149026_b.transits.txt",  "16 30 29.6192",  "+38 20 50.315"),
    ("transitsearch.org/TrES-1___b.transits.txt",  "19 04 09.844 ",  "+36 37 57.54 "),
    ("transitsearch.org/TrES-2___b.transits.txt",  "19 07 14.035 ",  "+49 18 59.07 "),
    ("transitsearch.org/TrES-3___b.transits.txt",  "17 52.0      ",  "+37 32       "),
    ("transitsearch.org/TrES-4___b.transits.txt",  "17 53 13.058 ",  "+37 12 42.36 "),
    ("transitsearch.org/OGLE-TR10b.transits.txt",  "17 51 28.25  ",  "-29 52 34.9  "),
    ("transitsearch.org/OGLETR111b.transits.txt",  "10 53 17.91  ",  "-61 24 20.3  "),
    ("transitsearch.org/OGLETR113b.transits.txt",  "10 52 24.40  ",  "-61 26 48.5  "),
    ("transitsearch.org/OGLETR132b.transits.txt",  "10 50 34.72  ",  "-61 57 25.9  "),
    ("transitsearch.org/HAT-P-1__b.transits.txt",  "22 57 46.83  ",  "+38 40 29.8  "),
    ("transitsearch.org/HAT-P-2__b.transits.txt",  "16 20 36.36  ",  "+41 02 53.1  "),
    ("transitsearch.org/HAT-P-3__b.transits.txt",  "13 44 23.0   ",  "+48 01 43    "),
    ("transitsearch.org/HAT-P-5__b.transits.txt",  "18 17 37.299 ",  "+36 37 16.88 "),
    ("transitsearch.org/HAT-P-6__b.transits.txt",  "23 39 05.806 ",  "+42 27 57.51 "),
    ("transitsearch.org/XO-1_____b.transits.txt",  "16 02 11.84  ",  "+28 10 10.4  "),
    ("transitsearch.org/XO-2_____b.transits.txt",  "07 48 06.46  ",  "+50 13 32.9  "),
    ("transitsearch.org/WASP-1___b.transits.txt",  "00 20 40.08  ",  "+31 59 23.8  "),
    ("transitsearch.org/WASP-2___b.transits.txt",  "20 30 54.13  ",  "+06 25 46.4  "),
    ("transitsearch.org/WASP-3___b.transits.txt",  "18 34 31.625 ",  "+35 39 41.55 ")]


class PlanetDb (object):

    def __init__ (self):

        self.planets = []

        for planet in planets:

            p = Planet.fromFile(os.path.join(os.path.dirname(__file__), "../../data", planet[0]))
            p.star.position = Position.fromRaDec(planet[1], planet[2])
            self.planets.append(p)

    def __iter__ (self):
        return self.planets.__iter__()

