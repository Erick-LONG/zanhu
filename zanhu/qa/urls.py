from django.urls import path
from zanhu.articles import views

app_name = "articles"
urlpatterns = [
    path("", views.ArticlesListView.as_view(), name="list"),
    path("write-new-article/", views.ArticlesCreateView.as_view(), name="write_new"),
    path("drafts/", views.DraftListView.as_view(), name="drafts"),
    path("<str:slug>/", views.ArticlesDetailView.as_view(), name="article"),
    path("edit/<int:pk>/", views.ArticlesEditView.as_view(), name="edit_article"),
]
