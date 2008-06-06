#! /usr/bin/env python
#! -*- coding: utf-8 -*-

from transits import Transits
from star import Star

import time
import datetime as dt
import os.path


class Planet (object):

    @staticmethod
    def fromFile (filename):

        p = Planet()

        basename = os.path.basename(filename)
        
        p.name = basename.split(".")[0].replace("_", "")
        p.transits = Transits.fromFile(filename)
        return p

    def __init__ (self):

        self.name = ""

        self.radius = 0
        self.mass   = 0

        self.period = 0
        self.e      = 0

        self.star = Star()

        self.transits = None

    def getTransits (self, begin, end):
        """
        Returns an array of observable transits between begin and end
        (inclusive).
        """

        mask = (self.transits.begin >= time.mktime(begin.timetuple())) & \
               (self.transits.end   <= time.mktime(end.timetuple()))

        return Transits.copy(self.transits, mask)
        

if __name__ == "__main__":

    p = Planet.fromFile("../../data/transitsearch.org/OGLE-TR56b.transits.txt")
    print p.name
    print len(p.transits.begin)
    print time.strftime("%c", time.localtime(p.transits.begin[0]))
