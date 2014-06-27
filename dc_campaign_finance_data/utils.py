import logging
import functools
import retrying
import requests_cache


def enable_logging():
    logging.basicConfig(level=logging.DEBUG)


def listify(f):
    @functools.wraps(f)
    def listify_helper(*args, **kwargs):
        return list(f(*args, **kwargs))
    return listify_helper


# Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds, then 10 seconds afterwards
retry_exp_backoff = retrying.retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000
)


def enable_cache():
    requests_cache.install_cache(allowable_methods=('GET', 'POST'), expire_after=60 * 60 * 24)

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
        except Exception:
            pass
        else:
            return return_output
        finally:
            indent_level -= 1
            _log_with_level('{}->'.format(f.__name__))

    return wrapper
