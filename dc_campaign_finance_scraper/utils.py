import logging
import functools
import retrying
import requests_cache
import requests.exceptions


def enable_logging():
    logging.basicConfig(level=logging.DEBUG)


def listify(f):
    @functools.wraps(f)
    def listify_helper(*args, **kwargs):
        return list(f(*args, **kwargs))
    return listify_helper


def retry_exp_backoff(f):
    @functools.wraps(f)
    def retry_exp_backoff_helper(*args, **kwargs):
        # Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds, then 10 seconds afterwards
        return retrying.Retrying(
            wait_exponential_multiplier=1000,
            wait_exponential_max=10000,
            retry_on_exception=lambda exception: isinstance(exception, requests.exceptions.ConnectionError)
        ).call(f, *args, **kwargs)
    return retry_exp_backoff_helper


def enable_cache(backend='sqlite', **kwargs):
    requests_cache.install_cache(allowable_methods=('GET', 'POST'), expire_after=60 * 60 * 24, backend=backend, **kwargs)

indent_level = 0


def _log_with_level(str):
    global indent_level
    logger = logging.getLogger(__name__)
    logger.debug(' ' * indent_level + str)


def log_function(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        global indent_level
        argument_string = ', '.join(map(repr, args)) + ', '.join(key + '=' + repr(value) for (key, value) in kwds.items())
        _log_with_level('{}({})'.format(f.__name__, argument_string))
        indent_level += 1
        try:
            return_output = f(*args, **kwds)
        except Exception as e:
            _log_with_level('->Raised {}'.format(repr(e)))
            raise
        else:
            _log_with_level('->{}'.format(repr(return_output)[0:50]))
            return return_output
        finally:
            indent_level -= 1

    return wrapper
