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


@api_v1.resource('/transaction/', endpoint='api.transaction.list')
class TransactionListAPI(flask_restful.Resource):
  @auth.login_required
  def get(self):
    transaction_dbs, transaction_cursor = model.Transaction.get_dbs(user_key=auth.current_user_key())
    return helpers.make_response(transaction_dbs, model.Transaction.FIELDS, transaction_cursor)


@api_v1.resource('/transaction/<string:transaction_key>/', endpoint='api.transaction')
class TransactionAPI(flask_restful.Resource):
  @auth.login_required
  def get(self, transaction_key):
    transaction_db = ndb.Key(urlsafe=transaction_key).get()
    if not transaction_db or transaction_db.user_key != auth.current_user_key():
      helpers.make_not_found_exception('Transaction %s not found' % transaction_key)
    return helpers.make_response(transaction_db, model.Transaction.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/transaction/', endpoint='api.admin.transaction.list')
class AdminTransactionListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    transaction_keys = util.param('transaction_keys', list)
    if transaction_keys:
      transaction_db_keys = [ndb.Key(urlsafe=k) for k in transaction_keys]
      transaction_dbs = ndb.get_multi(transaction_db_keys)
      return helpers.make_response(transaction_dbs, model.transaction.FIELDS)

    transaction_dbs, transaction_cursor = model.Transaction.get_dbs()
    return helpers.make_response(transaction_dbs, model.Transaction.FIELDS, transaction_cursor)

  @auth.admin_required
  def delete(self):
    transaction_keys = util.param('transaction_keys', list)
    if not transaction_keys:
      helpers.make_not_found_exception('Transaction(s) %s not found' % transaction_keys)
    transaction_db_keys = [ndb.Key(urlsafe=k) for k in transaction_keys]
    ndb.delete_multi(transaction_db_keys)
    return flask.jsonify({
      'result': transaction_keys,
      'status': 'success',
    })


@api_v1.resource('/admin/transaction/<string:transaction_key>/', endpoint='api.admin.transaction')
class AdminTransactionAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, transaction_key):
    transaction_db = ndb.Key(urlsafe=transaction_key).get()
    if not transaction_db:
      helpers.make_not_found_exception('Transaction %s not found' % transaction_key)
    return helpers.make_response(transaction_db, model.Transaction.FIELDS)

  @auth.admin_required
  def delete(self, transaction_key):
    transaction_db = ndb.Key(urlsafe=transaction_key).get()
    if not transaction_db:
      helpers.make_not_found_exception('Transaction %s not found' % transaction_key)
    transaction_db.key.delete()
    return helpers.make_response(transaction_db, model.Transaction.FIELDS)
