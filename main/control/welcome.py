# coding: utf-8

import flask
from google.appengine.ext import ndb

import auth
import config
import model
import util

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  if auth.is_logged_in():
    currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1)
    transaction_dbs, transaction_cursor = model.Transaction.get_dbs(user_key=auth.current_user_key(), limit=-1)
    return flask.render_template(
      'welcome.html',
      html_class='welcome',
      transaction_dbs=transaction_dbs,
      currency_dbs=currency_dbs,
      api_url=flask.url_for('api.transaction.list'),
    )
  return flask.render_template(
    'welcome.html',
    html_class='welcome',
  )


@app.route('/exchange/<code>/')
@app.route('/exchange/')
def exchange(code=None):
  price_qry = None
  if code:
    code = code.upper()
    price_qry = model.Price.query(ndb.OR(model.Price.currency_from_code == code, model.Price.currency_to_code == code))
  price_dbs, price_cursor = model.Price.get_dbs(query=price_qry, limit=-1)
  currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1, order='name')
  return flask.render_template(
    'exchange.html',
    html_class='exchange',
    title='Exchange',
    price_dbs=price_dbs,
    currency_dbs=currency_dbs,
    code=code,
    api_url=flask.url_for('api.price.list'),
  )


###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
    'sitemap.xml',
    lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
  ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
