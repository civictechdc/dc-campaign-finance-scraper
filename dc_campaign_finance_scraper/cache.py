import shelve
import functools
import tempfile
import os
import weakref


PERSISTANT_CACHE = False


def _named_temp_file(name):
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, name)


CACHE_FILE_NAME = _named_temp_file('dc_campaign_finance_scraper')


def use_persistant_cache():
    global PERSISTANT_CACHE
    PERSISTANT_CACHE = True


def clear_persistant_cache():
    with shelve.open(CACHE_FILE_NAME, writeback=True) as cache:
        cache.clear()


def cache(function):
    @functools.wraps(function)
    def wrapper(*args, **kwds):
        if PERSISTANT_CACHE:
            cache_wrapper = _persistant_cache(CACHE_FILE_NAME)
        else:
            cache_wrapper = functools.lru_cache(maxsize=None)
        return cache_wrapper(function)(*args, **kwds)
    return wrapper


def _check_cache(cache, key, func, args, kwargs):
    try:
        return cache[key]
    except KeyError:
        cache[key] = func(*args, **kwargs)
        return cache[key]

_handle_dict = weakref.WeakValueDictionary()


def _persistant_cache(filename):
    def decorating_function(user_function):
        @functools.wraps(user_function)
        def wrapper(*args, **kwds):
            args_key = str(hash(functools._make_key(args, kwds, typed=False)))
            func_key = '.'.join([user_function.__module__, user_function.__name__])
            unique_kye = func_key + args_key
            try:
                return _check_cache(_handle_dict[filename], unique_kye,
                                    user_function, args, kwds)
            except KeyError:

                with shelve.open(filename, writeback=True) as cache:
                    _handle_dict[filename] = cache
                    return _check_cache(cache, unique_kye, user_function, args, kwds)

        return wrapper

    return decorating_function
