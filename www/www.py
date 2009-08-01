#! /usr/bin/env python
# -*- coding: utf-8 -*-

from finder.transitobserver import TransitObserver
from finder.observatory     import Observatory
from finder.position        import Position
from finder.planetdb        import PlanetDb

import cherrypy
from   genshi.template import TemplateLoader
import simplejson as json

from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY

import os
import sys
import time
import datetime as dt

loader = TemplateLoader('.', auto_reload=True)


class Finder (object):

    def __init__ (self):

        self.db = PlanetDb()

        self.obs = Observatory(Position.fromLongLat("-43:00:00", "-22:30:00"), 1864, -3)

        self.dates = {"tonight"   : lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=1)),
                      "this-week" : lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=7)),
                      "this-month": lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=30))}

    def index (self, begin, end, *args, **kwargs):
        
        tmpl = loader.load('index.html')

        selection = begin

        # use date shortcuts
        if begin.lower() in self.dates.keys():
            begin, end = self.dates[begin.lower()]()
        # or plain dates, assumes now for time part
        else:
            try:
                begin = parse(begin, default=dt.datetime.now())
                end  =  parse(end,   default=dt.datetime.now())
            except ValueError:
                return tmpl.generate(error="invalid date range").render('html', doctype='html')
                

        # compute!
        transits= []
        
        for planet in self.db:
            transits += TransitObserver.observable(planet, self.obs, begin, end)

        # order by date

        transits_by_day = {}

        for transit in transits:
            day= transit.begin.date()

            if day not in transits_by_day:
                transits_by_day[day] = []
                
            transits_by_day[day].append(transit)

        days_in_order = sorted(transits_by_day.keys())

        return tmpl.generate(transits=transits_by_day, days=days_in_order, error=None,
                             begin=begin, end=end, selection=selection).render('html', doctype='html')


def setup_routes():
    d = cherrypy.dispatch.RoutesDispatcher()

    d.connect('finder', 'finder/:begin/:end/:action', controller=Finder(),
              begin='tonight', end=None)

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
