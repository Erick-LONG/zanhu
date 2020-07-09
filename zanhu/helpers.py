from functools import wraps
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied


def ajax_requred(f):
    '''验证是否为ajax请求'''
    @wraps(f)
    def wrap(request,*args,**kwargs):
        # request.is_ajax()
        if not request.is_ajax():
            return HttpResponseBadRequest('不是ajax请求')
        return f(request,*args,**kwargs)
    return wrap


class AuthorRequireMixin(View):
    '''验证是否为原作者，用户状态删除和文章编辑'''
    def dispatch(self, request, *args, **kwargs):
        #状态和文章实例有user属性
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

