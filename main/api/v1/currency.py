# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask
import flask_restful

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/currency/', endpoint='api.currency.list')
class CurrencyListAPI(flask_restful.Resource):
  def get(self):
    currency_dbs, currency_cursor = model.Currency.get_dbs()
    return helpers.make_response(currency_dbs, model.Currency.FIELDS, currency_cursor)


@api_v1.resource('/currency/<string:currency_key>/', endpoint='api.currency')
class CurrencyAPI(flask_restful.Resource):
  def get(self, currency_key):
    currency_db = ndb.Key(urlsafe=currency_key).get()
    if not currency_db:
      helpers.make_not_found_exception('Currency %s not found' % currency_key)
    return helpers.make_response(currency_db, model.Currency.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/currency/', endpoint='api.admin.currency.list')
class AdminCurrencyListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    currency_keys = util.param('currency_keys', list)
    if currency_keys:
      currency_db_keys = [ndb.Key(urlsafe=k) for k in currency_keys]
      currency_dbs = ndb.get_multi(currency_db_keys)
      return helpers.make_response(currency_dbs, model.currency.FIELDS)

    currency_dbs, currency_cursor = model.Currency.get_dbs()
    return helpers.make_response(currency_dbs, model.Currency.FIELDS, currency_cursor)

  @auth.admin_required
  def delete(self):
    currency_keys = util.param('currency_keys', list)
    if not currency_keys:
      helpers.make_not_found_exception('Currency(s) %s not found' % currency_keys)
    currency_db_keys = [ndb.Key(urlsafe=k) for k in currency_keys]
    ndb.delete_multi(currency_db_keys)
    return flask.jsonify({
      'result': currency_keys,
      'status': 'success',
    })


@api_v1.resource('/admin/currency/<string:currency_key>/', endpoint='api.admin.currency')
class AdminCurrencyAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, currency_key):
    currency_db = ndb.Key(urlsafe=currency_key).get()
    if not currency_db:
      helpers.make_not_found_exception('Currency %s not found' % currency_key)
    return helpers.make_response(currency_db, model.Currency.FIELDS)

  @auth.admin_required
  def delete(self, currency_key):
    currency_db = ndb.Key(urlsafe=currency_key).get()
    if not currency_db:
      helpers.make_not_found_exception('Currency %s not found' % currency_key)
    currency_db.key.delete()
    return helpers.make_response(currency_db, model.Currency.FIELDS)
