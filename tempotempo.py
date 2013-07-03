import os
import datetime
import time
import functools

import tempodb


TEMPODB_API_HOST = os.getenv('TEMPODB_API_HOST', "api.tempo-db.com")
TEMPODB_API_KEY = os.getenv('TEMPODB_API_KEY')
TEMPODB_API_PORT = int(os.getenv('TEMPODB_API_PORT', 443))
TEMPODB_API_SECRET = os.getenv('TEMPODB_API_SECRET')
TEMPODB_API_SECURE = os.getenv('TEMPODB_API_SECURE', 'True')

if TEMPODB_API_SECURE.lower() == 'true':
    TEMPODB_API_SECURE = True
else:
    TEMPODB_API_SECURE = False


def _create_client(**kwargs):
    return tempodb.Client(key=kwargs.pop('key', TEMPODB_API_KEY),
                          secret=kwargs.pop('secret', TEMPODB_API_SECRET),
                          host=kwargs.pop('host', TEMPODB_API_HOST),
                          port=kwargs.pop('port', TEMPODB_API_PORT),
                          secure=kwargs.pop('secure', TEMPODB_API_SECURE),
                          **kwargs)

class Client(object):

    _client = None

    def __init__(self, default_key=None, **kwargs):
        self._series_key = default_key
        if self._client is None:
            self._client = _create_client(**kwargs)

    def _write(self, key=None, value=None, date=None):
        if value is None:
            value = 1
        if key is None:
            if self._series_key is None:
                raise ValueError('Key not provided')
            key = self._series_key
        if date is None:
            date = datetime.datetime.now()

        data = (tempodb.DataPoint(date, value),)
        return self._client.write_key(key, data)

    def __call__(self, key=None, value=None, date=None):
        return self._write(key, value, date)

    def before(self, key=None, value=None, date=None):
        def wrap(f):
            @functools.wraps(f)
            def wrapped(*args, **kwargs):
                self._write(key, value, date)
                return f(*args, **kwargs)
            return wrapped
        return wrap

    def after(self, key=None, value=None, date=None):
        def wrap(f):
            @functools.wraps(f)
            def wrapped(*args, **kwargs):
                res = f(*args, **kwargs)
                self._write(key, value, date)
                return res
            return wrapped
        return wrap

    def measure(self, key=None, value=None, date=None):
        def wrap(f):
            @functools.wraps(f)
            def wrapped(*args, **kwargs):
                start = time.clock()
                res = f(*args, **kwargs)
                end = time.clock()
                value = end - start
                self._write(key, value, date)
                return res
            return wrapped
        return wrap


class Measure(Client):

    def __init__(self, default_key=None, **kwargs):
        super(Measure, self).__init__(default_key, **kwargs)

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, exception_type, exception_val, trace):
        end = time.clock()
        value = end - self.start
        return self._write(key, value, date)
