from functools import wraps
from django.http import HttpResponseBadRequest


def ajax_requred(f):
    '''验证是否为ajax请求'''
    @wraps(f)
    def wrap(request,*args,**kwargs):
        # request.is_ajax()
        if not request.is_ajax():
            return HttpResponseBadRequest('不是ajax请求')
        return f(request,*args,**kwargs)
    return wrap
