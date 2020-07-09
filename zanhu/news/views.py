from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from zanhu.news.models import News
from zanhu.helpers import ajax_requred, AuthorRequireMixin


class NewsListView(LoginRequiredMixin, ListView):
    '''首页动态'''
    model = News
    # queryset = News.objects.all()#可做简单过滤
    paginate_by = 20  # url中的?page=
    # page_kwarg = 'p'
    # context_object_name = 'news_list' # 要循环的对象默认是「模型类名_list」或者「object_list」
    # ordering = 'created_at' # ('x','y',)在模型类中已经定义
    template_name = 'news/news_list.html'  # 可以不用写，默认模型类名_list.html

    # def get_ordering(self):
    #     pass
    # def get_paginate_by(self, queryset):
    #     pass

    def get_queryset(self):  # 可做更复杂的过滤
        return News.objects.filter(reply=False)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     '''添加额外的上下文'''
    #     context = super().get_context_data()
    #     context['views'] = 100
    #     return context


class NewDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    # slug_url_kwarg = 'slug' #通过url传入要删除的对象主键ID，默认值是slug
    # pk_url_kwarg = 'pk' #通过url传入要删除的对象主键ID，默认值是pk
    success_url = reverse_lazy('news:list')  # 在项目URLconf未加载前使用


@login_required
@ajax_requred
@require_http_methods(['POST'])
def post_new(request):
    '''发送动态,AJAX POST请求'''

    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest('内容不能为空')


@login_required
@ajax_requred
@require_http_methods(['POST'])
def like(request):
    '''点赞,AJAX POST请求'''
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    # 取消或者添加赞
    news.switch_like(request.user)
    return JsonResponse({'likes': news.count_likers()})
