#! /usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
  name = 'transitfinder',
  version = "0.1",
  description = "Transit Finder",
  long_description = "App to find exoplanet transit observation opportunities at your place",
  url = "https://github.com/phsilva/transitfinder",

  author = "Paulo Henrique Silva",
  author_email = "ph.silva@gmail.com",

  license = "GPLv3",

  package_dir = {"": "src"},
  packages = find_packages("src"),

  include_package_data = True,

  install_requires = [
    "numpy",
    "matplotlib",
    "novas",
    "pyephem",
    "Flask",
  ]
)
