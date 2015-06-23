#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle

import scraper

app = Flask(__name__)
assets = Environment(app)

app.config.update(dict(
    # default settings here
))
# load env-specific settings (i.e. dev)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

# any asset bundles requiring pre-processing are declared here
assets.register('site_css', Bundle('c/site.scss', filters='scss',
                                   output='gen/site.css'))


@app.route('/')
def index():
    summary = scraper.get_summary()
    pretty = json.dumps(summary, sort_keys=True, indent=4)
    return render_template('index.html', summary=summary, pretty=pretty)


@app.route('/<int:match_id>')
def match(match_id):
    summary = scraper.get_summary()
    match = scraper.get_match(match_id)
    pretty = json.dumps(match, sort_keys=True, indent=4)
    return render_template('match.html', match=match, summary=summary, 
        pretty=pretty)


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
