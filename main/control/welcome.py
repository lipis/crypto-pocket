# coding: utf-8

import flask

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
    transaction_dbs, transaction_cursor = model.Transaction.get_dbs(user_key=auth.current_user_key())
    return flask.render_template(
      'welcome.html',
      html_class='welcome',
      transaction_dbs=transaction_dbs,
      next_url=util.generate_next_url(transaction_cursor),
      api_url=flask.url_for('api.transaction.list'),
    )
  return flask.render_template(
    'welcome.html',
    html_class='welcome',
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
