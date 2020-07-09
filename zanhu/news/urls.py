from django.urls import path
from zanhu.news import views

app_name = "news"
urlpatterns = [
    path("", views.NewsListView.as_view(), name="list"),
    path('post-news/',views.post_new,name='post_news'),
    path('delete/<str:pk>/',views.NewDeleteView.as_view(),name='delete_news'),
    path('like/',views.like,name='like_post')
]
