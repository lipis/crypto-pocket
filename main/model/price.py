# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util


class Price(model.Base):
  currency_from_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Currency From'))
  currency_to_key = ndb.KeyProperty(kind=model.Currency, required=True, verbose_name=_(u'Currency To'))
  amount = ndb.FloatProperty(default=0, verbose_name=_(u'Amount'))

  @ndb.ComputedProperty
  def amount_currency(self):
    return '%.4f %s' % (self.amount, self.currency_to_key.get().code)

  @ndb.ComputedProperty
  def currency_from_code(self):
    return self.currency_from_key.get().code

  @ndb.ComputedProperty
  def currency_to_code(self):
    return self.currency_to_key.get().code

  @ndb.ComputedProperty
  def currency_from_name(self):
    return self.currency_from_key.get().name

  @ndb.ComputedProperty
  def currency_to_name(self):
    return self.currency_to_key.get().name

  @ndb.ComputedProperty
  def amount_invert(self):
    if self.amount != 0:
      return 1.0 / self.amount
    return 1

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Price, cls).get_dbs(
      order=order or util.param('order') or 'currency_from_name,currency_to_name',
      **kwargs
    )

  FIELDS = {
    'currency_from_key': fields.Key,
    'currency_to_key': fields.Key,
    'amount': fields.Float,
  }

  FIELDS.update(model.Base.FIELDS)
