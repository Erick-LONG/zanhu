from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import CreateView,ListView,UpdateView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from zanhu.articles.models import Article
from zanhu.articles.forms import ArticleForm


class ArticlesListView(LoginRequiredMixin,ListView):
    '''已发布的文章列表'''
    model = Article
    paginate_by = 10
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()


class DraftListView(ArticlesListView):
    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()


class ArticlesCreateView(LoginRequiredMixin,CreateView):
    '''发表文章'''
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_create.html'
    message = '您的文章已创建成功'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        '''创建成功后跳转'''
        messages.success(self.request,self.message) #消息传递给下一次请求
        return reverse_lazy('articles:list')
