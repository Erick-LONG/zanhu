from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from zanhu.news.models import News

class NewsListView(LoginRequiredMixin,ListView):
    '''首页动态'''
    model = News
    # queryset = News.objects.all()#可做简单过滤
    paginate_by = 20 #url中的?page=
    # page_kwarg = 'p'
    # context_object_name = 'news_list' # 要循环的对象默认是「模型类名_list」或者「object_list」
    # ordering = 'created_at' # ('x','y',)在模型类中已经定义
    template_name = 'news/news_list.html' #可以不用写，默认模型类名_list.html

    # def get_ordering(self):
    #     pass
    # def get_paginate_by(self, queryset):
    #     pass

    def get_queryset(self): #可做更复杂的过滤
        return News.objects.filter(reply=False)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     '''添加额外的上下文'''
    #     context = super().get_context_data()
    #     context['views'] = 100
    #     return context


