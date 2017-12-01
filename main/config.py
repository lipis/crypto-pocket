# coding: utf-8

import os
import operator
import flask

PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
DEBUG = DEVELOPMENT = not PRODUCTION

try:
  # This part is surrounded in try/except because the config.py file is
  # also used in the run.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  from google.appengine.api import app_identity

  APPLICATION_ID = app_identity.get_application_id()
  APPLICATION_NAME = 'cryptopocket.io'
except (ImportError, AttributeError):
  pass
else:
  from datetime import datetime

  CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID')
  CURRENT_VERSION_NAME = CURRENT_VERSION_ID.split('.')[0]
  CURRENT_VERSION_TIMESTAMP = long(CURRENT_VERSION_ID.split('.')[1]) >> 28
  if DEVELOPMENT:
    import calendar

    CURRENT_VERSION_TIMESTAMP = calendar.timegm(datetime.utcnow().timetuple())
  CURRENT_VERSION_DATE = datetime.utcfromtimestamp(CURRENT_VERSION_TIMESTAMP)
  USER_AGENT = '%s/%s' % (APPLICATION_ID, CURRENT_VERSION_ID)

  import model

  CONFIG_DB = model.Config.get_master_db()
  SECRET_KEY = CONFIG_DB.flask_secret_key.encode('ascii')
  RECAPTCHA_PUBLIC_KEY = CONFIG_DB.recaptcha_public_key
  RECAPTCHA_PRIVATE_KEY = CONFIG_DB.recaptcha_private_key
  RECAPTCHA_LIMIT = 8
  TRUSTED_HOSTS = CONFIG_DB.trusted_hosts
  LOCALE_DEFAULT = CONFIG_DB.locale

DEFAULT_DB_LIMIT = 64
SIGNIN_RETRY_LIMIT = 4
TAG_SEPARATOR = ' '

OG_DESCRIPTION = 'Track your crypto portfolios and your investments.'
OG_IMAGE = '/p/img/og-main.png'
OG_PRICES = '/p/img/og-prices.png'

###############################################################################
# i18n Stuff
###############################################################################

# Languages: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# Countries: http://en.wikipedia.org/wiki/ISO_3166-1
# To Add/Modify languages use one of the filenames in: libx/babel/localedata/
# Examples with country included: en_GB, ru_RU, de_CH
LOCALE = {
  'en': u'English',
  'el': u'Ελληνικά',
  'pl': u'Polski',
  'ru': u'Русский',
}

LOCALE_SORTED = sorted(LOCALE.iteritems(), key=operator.itemgetter(1))
LANGUAGES = [l.lower().replace('_', '-') for l in LOCALE.keys()]
