from django.conf.urls import url

from server import views

urlpatterns = [
    url(r'^$', views.index, name='index'),    
    url(r'^index/$', views.index, name='index'),
    url(r'^register_user/$', views.register_user, name='register_user'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^create_game/$', views.create_game, name='create_game'),
    url(r'^counter/$', views.counter, name='counter'),
    url(r'^clean_orphan_games/$', views.clean_orphan_games, name='clean_orphan_games'),
    url(r'^status_turn/$', views.status_turn, name='status_turn'),
    url(r'^status_turn2/$', views.status_turn2, name='status_turn2'),
    url(r'^status_board/$', views.status_board, name='status_board'),
    url(r'^join_game/$', views.join_game, name='join_game'),
    url(r'^move/$', views.move, name='move'),
    url(r'^show/$', views.show, name='show'),
    url(r'^show_board/$', views.show_board, name='show_board'),
    url(r'^winner/$', views.winner, name='winner'),
]
