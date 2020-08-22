from django import forms

from zanhu.articles.models import Article
from markdownx.fields import MarkdownxFormField


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    edited = forms.BooleanField(widget=forms.HiddenInput(),initial=False,required=False)
    content = MarkdownxFormField()
    class Meta:
        model = Article
        fields = ['title','content','image','tags']
