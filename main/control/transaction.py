# coding: utf-8

from google.appengine.ext import ndb
import flask
import flask_wtf
import wtforms

import auth
import model
import util

from main import app


###############################################################################
# Update
###############################################################################
class TransactionUpdateForm(flask_wtf.FlaskForm):
  date = wtforms.DateField(
    model.Transaction.date._verbose_name,
    [wtforms.validators.required()],
  )
  spent_amount = wtforms.FloatField(
    model.Transaction.spent_amount._verbose_name,
    [wtforms.validators.optional()],
  )
  spent_currency_key = wtforms.SelectField(
    model.Transaction.spent_currency_key._verbose_name,
    [wtforms.validators.required()],
    choices=[],
  )
  fee = wtforms.FloatField(
    model.Transaction.fee._verbose_name,
    [wtforms.validators.optional()],
  )
  acquired_amount = wtforms.FloatField(
    model.Transaction.acquired_amount._verbose_name,
    [wtforms.validators.optional()],
  )
  acquired_currency_key = wtforms.SelectField(
    model.Transaction.acquired_currency_key._verbose_name,
    [wtforms.validators.required()],
    choices=[],
  )
  notes = wtforms.TextAreaField(
    model.Transaction.notes._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  platform = wtforms.StringField(
    model.Transaction.platform._verbose_name,
    [wtforms.validators.optional(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )


@app.route('/investment/create/', methods=['GET', 'POST'])
@app.route('/investment/<int:transaction_id>/update/', methods=['GET', 'POST'])
@auth.login_required
def transaction_update(transaction_id=0):
  if transaction_id:
    transaction_db = model.Transaction.get_by_id(transaction_id)
  else:
    transaction_db = model.Transaction(user_key=auth.current_user_key())

  if not transaction_db or transaction_db.user_key != auth.current_user_key():
    flask.abort(404)

  form = TransactionUpdateForm(obj=transaction_db)

  currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1)
  form.spent_currency_key.choices = [(c.key.urlsafe(), '%s (%s)' % (c.name, c.code)) for c in currency_dbs]
  form.acquired_currency_key.choices = [(c.key.urlsafe(), '%s (%s)' % (c.name, c.code)) for c in currency_dbs]
  if flask.request.method == 'GET' and not form.errors:
    form.spent_currency_key.data = transaction_db.spent_currency_key.urlsafe() if transaction_db.spent_currency_key else None
    form.acquired_currency_key.data = transaction_db.acquired_currency_key.urlsafe() if transaction_db.acquired_currency_key else None

  if form.validate_on_submit():
    form.spent_currency_key.data = ndb.Key(urlsafe=form.spent_currency_key.data) if form.spent_currency_key.data else None
    form.acquired_currency_key.data = ndb.Key(urlsafe=form.acquired_currency_key.data) if form.acquired_currency_key.data else None
    form.spent_amount.data = form.spent_amount.data or 0
    form.acquired_amount.data = form.acquired_amount.data or 0
    form.fee.data = form.fee.data or 0
    form.populate_obj(transaction_db)
    transaction_db.put()
    return flask.redirect(flask.url_for('welcome'))

  return flask.render_template(
    'transaction/transaction_update.html',
    title='%s' % 'Investment' if transaction_id else 'New investment',
    html_class='transaction-update',
    form=form,
    transaction_db=transaction_db,
  )


###############################################################################
# List
###############################################################################
@app.route('/transaction/')
@auth.login_required
def transaction_list():
  transaction_dbs, transaction_cursor = model.Transaction.get_dbs(user_key=auth.current_user_key())
  return flask.render_template(
    'transaction/transaction_list.html',
    html_class='transaction-list',
    title='Transaction List',
    transaction_dbs=transaction_dbs,
    next_url=util.generate_next_url(transaction_cursor),
    api_url=flask.url_for('api.transaction.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/investment/<int:transaction_id>/')
@auth.login_required
def transaction_view(transaction_id):
  transaction_db = model.Transaction.get_by_id(transaction_id)
  if not transaction_db or transaction_db.user_key != auth.current_user_key():
    flask.abort(404)

  return flask.render_template(
    'transaction/transaction_view.html',
    html_class='transaction-view',
    title='Investment',
    transaction_db=transaction_db,
    api_url=flask.url_for('api.transaction', transaction_key=transaction_db.key.urlsafe() if transaction_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/transaction/')
@auth.admin_required
def admin_transaction_list():
  transaction_dbs, transaction_cursor = model.Transaction.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'transaction/admin_transaction_list.html',
    html_class='admin-transaction-list',
    title='Transaction List',
    transaction_dbs=transaction_dbs,
    next_url=util.generate_next_url(transaction_cursor),
    api_url=flask.url_for('api.admin.transaction.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class TransactionUpdateAdminForm(TransactionUpdateForm):
  pass


@app.route('/admin/transaction/create/', methods=['GET', 'POST'])
@app.route('/admin/transaction/<int:transaction_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_transaction_update(transaction_id=0):
  if transaction_id:
    transaction_db = model.Transaction.get_by_id(transaction_id)
  else:
    transaction_db = model.Transaction(user_key=auth.current_user_key())

  if not transaction_db:
    flask.abort(404)

  form = TransactionUpdateAdminForm(obj=transaction_db)

  user_dbs, user_cursor = model.User.get_dbs(limit=-1)
  currency_dbs, currency_cursor = model.Currency.get_dbs(limit=-1)
  form.spent_currency_key.choices = [(c.key.urlsafe(), c.name) for c in currency_dbs]
  form.acquired_currency_key.choices = [(c.key.urlsafe(), c.name) for c in currency_dbs]
  if flask.request.method == 'GET' and not form.errors:
    form.spent_currency_key.data = transaction_db.spent_currency_key.urlsafe() if transaction_db.spent_currency_key else None
    form.acquired_currency_key.data = transaction_db.acquired_currency_key.urlsafe() if transaction_db.acquired_currency_key else None

  if form.validate_on_submit():
    form.spent_currency_key.data = ndb.Key(urlsafe=form.spent_currency_key.data) if form.spent_currency_key.data else None
    form.acquired_currency_key.data = ndb.Key(urlsafe=form.acquired_currency_key.data) if form.acquired_currency_key.data else None
    form.populate_obj(transaction_db)
    transaction_db.put()
    return flask.redirect(flask.url_for('admin_transaction_list', order='-modified'))

  return flask.render_template(
    'transaction/admin_transaction_update.html',
    title='%s' % 'Transaction',
    html_class='admin-transaction-update',
    form=form,
    transaction_db=transaction_db,
    back_url_for='admin_transaction_list',
    api_url=flask.url_for('api.admin.transaction', transaction_key=transaction_db.key.urlsafe() if transaction_db.key else ''),
  )


###############################################################################
# Delete
###############################################################################
@app.route('/investment/<int:transaction_id>/delete/', methods=['POST'])
@auth.login_required
def transaction_delete(transaction_id):
  transaction_db = model.Transaction.get_by_id(transaction_id)
  if transaction_db and auth.current_user_key() == transaction_db.user_key:
    transaction_db.key.delete()
    flask.flash('Investement deleted.', category='success')
  return flask.redirect(flask.url_for('welcome'))


###############################################################################
# Admin Delete
###############################################################################
@app.route('/admin/transaction/<int:transaction_id>/delete/', methods=['POST'])
@auth.admin_required
def admin_transaction_delete(transaction_id):
  transaction_db = model.Transaction.get_by_id(transaction_id)
  transaction_db.key.delete()
  flask.flash('Transaction deleted.', category='success')
  return flask.redirect(flask.url_for('admin_transaction_list'))
