#! /usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import time
import sys

import numpy as N

class Transits (object):
    """
    Transits contains arrays with begin, center and end times (in MJD) of
    transits of a known exoplanet in a given period. 
    """

    #
    # static factories
    #

    @staticmethod
    def fromFile (filename):
        """
        Load transits from filename. Transitsearch.org fomat accepted.
        """

        f = None

        try:
            f = open(filename)
        except IOError, e:
            print >> sys.stderr, e
            sys.exit(1)

        lines = f.readlines()

        transits_begin  = N.zeros(len(lines[8:]), dtype=N.int32)
        transits_center = N.zeros(len(lines[8:]), dtype=N.int32)
        transits_end    = N.zeros(len(lines[8:]), dtype=N.int32)
        transits_obs    = N.ones(len(lines[8:]), dtype=N.float32)        

        splitre = re.compile("\d+\.\d+")

        # skip first 8 lines
        for i, line in enumerate(lines[8:]):
            parts = re.split(splitre, line[:-1])

            begin  = time.mktime(time.strptime(parts[1].strip(), "%Y %m %d %H %M"))
            center = time.mktime(time.strptime(parts[2].strip(), "%Y %m %d %H %M"))
            end    = time.mktime(time.strptime(parts[3].strip(), "%Y %m %d %H %M"))
                        
            transits_begin[i]  = begin
            transits_center[i] = center
            transits_end[i]    = end

        t = Transits()
        t.begin  = transits_begin 
        t.center = transits_center
        t.end    = transits_end
        t.observable = transits_obs
        t.duration   = t.end[0] - t.begin[0]

        return t

    @staticmethod
    def copy (transits, mask):
        t = Transits()
        t.duration = transits.duration
        t.begin    = transits.begin[mask]
        t.center   = transits.center[mask]
        t.end      = transits.end[mask]
        t.observable = transits.observable[mask]

        return t


    #
    # default constructor
    #
    
    def __init__ (self):

        self.duration = 0
        
        self.begin   = None
        self.center  = None
        self.end     = None

        self.observable = None


        
