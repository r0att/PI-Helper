from django.urls import path

from .views import home, challenge, finish_challenge, finish_hard_mode


urlpatterns = [
    path("", home, name="home"),
    path("challenge/", challenge, name="challenge"),
    path("challenge/finish/", finish_challenge, name="finish_challenge"),
    path("challenge/hard-mode/finish/", finish_hard_mode, name="finish_hard_mode"),
]