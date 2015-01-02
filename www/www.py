#! /usr/bin/env python
# -*- coding: utf-8 -*-

from finder.transitobserver import TransitObserver
from finder.observatory     import Observatory
from finder.position        import Position
from finder.planetdb        import PlanetDb

from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY

import os
import sys
import time
import datetime as dt

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
@app.route("/<begin>")
@app.route("/<begin>/<end>")
def finder(begin="tonight", end=None):

    db = PlanetDb()

    obs = Observatory(Position.fromLongLat("-43:00:00", "-22:30:00"), 1864, -3)

    dates = {
        "tonight"   : lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=1)),
        "this-week" : lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=7)),
        "this-month": lambda : (dt.datetime.now(), dt.datetime.now()+dt.timedelta(days=30))
    }

    selection = begin

    # use date shortcuts
    if begin.lower() in dates.keys():
        begin, end = dates[begin.lower()]()
    # or plain dates, assumes now for time part
    else:
        try:
            begin = parse(begin, default=dt.datetime.now())
            end  =  parse(end,   default=dt.datetime.now())
        except ValueError:
            return render_template("index.html", error="invalid date range")


    # compute!
    transits= []

    for planet in db:
        transits += TransitObserver.observable(planet, obs, begin, end)

    # order by date

    transits_by_day = {}

    for transit in transits:
        day= transit.begin.date()

        if day not in transits_by_day:
            transits_by_day[day] = []

        transits_by_day[day].append(transit)

    days_in_order = sorted(transits_by_day.keys())

    return render_template(
        "index.html",
        transits=transits_by_day, days=days_in_order, error=None,
        begin=begin, end=end, selection=selection)

if __name__ == '__main__':
    app.debug = True
    app.run()
