import functools
from flask import session, redirect


def login_require(is_admin=None):
    def outer(func):
        outer.__name__ =  func.__name__
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if not is_admin:
                if 'user_id' not in session:
                    return redirect('/')
            else:
                if 'admin_id' not in session:
                    return redirect('/admin/login')
            return func(*args, **kwargs)
        outer.__name__ = func.__name__
        return inner
    return outer


def login_required(func):
    # outer.__name__ =  func.__name__
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return func(*args, **kwargs)
    return inner


class LoginRequire(object):
    def __init__(self, is_admin=None):
        self.level = is_admin

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.level:
                if 'user_id' not in session:
                    return redirect('/')
            else:
                if 'admin_id' not in session:
                    return redirect('/admin/login')
            # print("[{level}]: the function {func}() is running...".format(level=self.level, func=func.__name__))
            return func(*args, **kwargs)
        return wrapper
