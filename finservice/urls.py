from django.conf.urls import include, url
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView

urlpatterns = [
    #url('index.html', views.index, name='index'),
    #url(r'^$', views.index),
    url('index.html', PostListView.as_view(), name='index'),
    url(r'^$', PostListView.as_view()),

    url('^equity/(?P<country_code>\w+)/', views.equity, name='equity'),
    url('^equity/$', views.equity),
    url('^indices/(?P<ric>\w+)/', views.indices, name='indices'),
    url('^indices/$', views.indices),
    url('^forex/(?P<ric>\w+)/', views.forex, name='forex'),
    url('^forex/$', views.forex),
    url("^chart/(?P<market>\w+)/(?P<ric>\w+)/", views.chart, name="chart"),

    url('user/(?P<username>\w+)/', UserPostListView.as_view(), name='user-posts'),
    url('post/(?P<pk>[0-9]+)/$', PostDetailView.as_view(), name='post-detail'),
    url('post/new/', PostCreateView.as_view(), name='post-create'),
    url('post/(?P<pk>[0-9]+)/update/', PostUpdateView.as_view(), name='post-update'),
    url('post/(?P<pk>[0-9]+)/delete/', PostDeleteView.as_view(), name='post-delete'),

]
