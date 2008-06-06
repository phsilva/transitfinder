#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

import cherrypy
from   genshi.template import TemplateLoader
import simplejson as json

from dateutil.parser import parse

loader = TemplateLoader('.', auto_reload=True)

from finder.observer import Observer
from finder.coord    import Coord
from finder.position import Position
from finder.planet   import Planet

import datetime as dt

location = Position.fromLongLat("-43:00:00", "-22:30:00")
altitude = 1864
timezone = -3

planets = [
    ("../data/transitsearch.org/HD17156__b.transits.txt",  "02 49 44.4875",  "+71 45 11.636"),  
    ("../data/transitsearch.org/HAT-P-2__b.transits.txt",  "16 20 36.3572",  "+41 02 53.101"),
    ("../data/transitsearch.org/HD149026_b.transits.txt",  "16 30 29.6192",  "+38 20 50.315"),
    ("../data/transitsearch.org/TrES-1___b.transits.txt",  "19 04 09.844 ",  "+36 37 57.54 "),
    ("../data/transitsearch.org/TrES-2___b.transits.txt",  "19 07 14.035 ",  "+49 18 59.07 "),
    ("../data/transitsearch.org/TrES-3___b.transits.txt",  "17 52.0      ",  "+37 32       "),
    ("../data/transitsearch.org/TrES-4___b.transits.txt",  "17 53 13.058 ",  "+37 12 42.36 "),
    ("../data/transitsearch.org/OGLE-TR10b.transits.txt",  "17 51 28.25  ",  "-29 52 34.9  "),
    ("../data/transitsearch.org/OGLETR111b.transits.txt",  "10 53 17.91  ",  "-61 24 20.3  "),
    ("../data/transitsearch.org/OGLETR113b.transits.txt",  "10 52 24.40  ",  "-61 26 48.5  "),
    ("../data/transitsearch.org/OGLETR132b.transits.txt",  "10 50 34.72  ",  "-61 57 25.9  "),
    ("../data/transitsearch.org/HAT-P-1__b.transits.txt",  "22 57 46.83  ",  "+38 40 29.8  "),
    ("../data/transitsearch.org/HAT-P-2__b.transits.txt",  "16 20 36.36  ",  "+41 02 53.1  "),
    ("../data/transitsearch.org/HAT-P-3__b.transits.txt",  "13 44 23.0   ",  "+48 01 43    "),
    ("../data/transitsearch.org/HAT-P-5__b.transits.txt",  "18 17 37.299 ",  "+36 37 16.88 "),
    ("../data/transitsearch.org/HAT-P-6__b.transits.txt",  "23 39 05.806 ",  "+42 27 57.51 "),
    ("../data/transitsearch.org/XO-1_____b.transits.txt",  "16 02 11.84  ",  "+28 10 10.4  "),
    ("../data/transitsearch.org/XO-2_____b.transits.txt",  "07 48 06.46  ",  "+50 13 32.9  "),
    ("../data/transitsearch.org/WASP-1___b.transits.txt",  "00 20 40.08  ",  "+31 59 23.8  "),
    ("../data/transitsearch.org/WASP-2___b.transits.txt",  "20 30 54.13  ",  "+06 25 46.4  "),
    ("../data/transitsearch.org/WASP-3___b.transits.txt",  "18 34 31.625 ",  "+35 39 41.55 ")]


db = []

for planet in planets:

    p = Planet.fromFile(planet[0])
    p.star.position = Position.fromRaDec(planet[1], planet[2])
    db.append(p)


class _ctrlchain(object):
 
    def __init__(self, name, head=None):
        if head is None:
            self.chain = list()
        else:
            self.chain = head[:]
        self.chain.append(name)
 
    def __getattr__(self, attr):
        return _ctrlchain(attr, self.chain)
 
    def __call__(self, *args, **kwargs):
        if len(self.chain) > 3:
            raise Exception("Don't know what to do with over 3 chain elements")
        if len(self.chain) > 2:
            kwargs["action"] = self.chain[2]
        if len(self.chain) > 1:
            kwargs["controller"] = self.chain[1]
 
        if len(args) == 1 and len(kwargs) == 0 and type(args[0]) in (str, unicode):
            return cherrypy.url(args[0])
        else:
            return cherrypy.url(routes.url_for(*args, **kwargs))
 
url = _ctrlchain('urlgen')


class Finder (object):

    def index (self, **args):
        tmpl = loader.load('index.html')

        transits = ""

        for planet in db:
            found = Observer.observableTransits(planet, location, altitude, timezone,
                                                parse(args["begin"], default=dt.datetime.now().replace(hour=12,minute=0)),
                                                parse(args["end"], default=dt.datetime.now().replace(hour=12,minute=0)))
            for f in found:
                transits += f

        return tmpl.generate(title='Transit Finder', transits=transits, **args).render('html', doctype='html')


def setup_routes():
    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect('finder', 'finder/:target/:begin/:end/:action', controller=Finder(),
              target='all', begin='today', end='1')
    
    return d


conf = {
    '/': {
        'request.dispatch': setup_routes()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.dir': 'static'
    }
}


def start(config=None):
    if config:
        cherrypy.config.update(config)
    app = cherrypy.tree.mount(None, config=conf)
    cherrypy.quickstart(app)

if __name__ == '__main__':

    start(os.path.join(os.path.dirname(__file__), 'finder.conf'))
