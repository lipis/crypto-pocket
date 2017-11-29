# coding: utf-8

from __future__ import absolute_import

import json

import flask
from google.appengine.api import urlfetch
from webargs import fields as wf
from webargs.flaskparser import parser
import flask_restful

import config
import util

from main import api_v1


@api_v1.resource('/crypto/price/historical/', endpoint='api.crypto.price.historical')
class CryptoPriceHistoricalAPI(flask_restful.Resource):
  def get(self):
    args = parser.parse({
      'fsym': wf.Str(),
      'tsym': wf.Str(),
      'ts': wf.Str(),
    })
    result = urlfetch.fetch('https://min-api.cryptocompare.com/data/pricehistorical?fsym=%s&tsyms=%s&ts=%s&extraParams=%s' % (args['fsym'], args['tsym'], args['ts'], config.APPLICATION_NAME))
    if result.status_code == 200:
      content = json.loads(result.content)
      try:
        rate = content[args['fsym']][args['tsym']]
        return util.jsonpify({'%s%s' % (args['fsym'], args['tsym']): rate})
      except:
        flask.abort(404)
    else:
      flask.abort(result.status_code)
