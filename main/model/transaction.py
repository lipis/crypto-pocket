# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util
import crypto


class Transaction(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True, verbose_name=_(u'User Key'))
  spent_amount = ndb.FloatProperty(default=0, verbose_name=_(u'Spent Amount'))
  spent_currency_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Spent Currency'))
  aquired_amount = ndb.FloatProperty(default=0, verbose_name=_(u'Aquired Amount'))
  aquired_currency_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Aquired Currency Key'))
  date = ndb.DateProperty(required=True, verbose_name=_(u'Date'))
  notes = ndb.StringProperty(default='', verbose_name=_(u'Notes'))
  platform = ndb.StringProperty(default='', verbose_name=_(u'Platform'))

  @ndb.ComputedProperty
  def spent(self):
    return self.spent_amount

  @ndb.ComputedProperty
  def aquired(self):
    return self.aquired_amount

  @ndb.ComputedProperty
  def aquired_rate(self):
    if self.spent_amount != 0:
      return self.spent_amount / self.aquired_amount
    return 0

  @ndb.ComputedProperty
  def current_rate(self):
    return crypto.get_exchange_rate_by_keys(self.aquired_currency_key, self.spent_currency_key)

  @ndb.ComputedProperty
  def profit(self):
    return (self.current_rate - self.aquired_rate) * self.aquired_amount

  @ndb.ComputedProperty
  def total(self):
    return self.profit + self.spent_amount

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Transaction, cls).get_dbs(
      order=order or util.param('order') or '-date',
      **kwargs
    )

  FIELDS = {
    'user_key': fields.Key,
    'spent_amount': fields.Float,
    'spent_currency_key': fields.Key,
    'aquired_amount': fields.Float,
    'aquired_currency_key': fields.Key,
    'date': fields.Fixed,
    'notes': fields.String,
    'platform': fields.String,
  }

  FIELDS.update(model.Base.FIELDS)
