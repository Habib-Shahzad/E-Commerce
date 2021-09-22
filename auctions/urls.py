from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed", views.closed, name='closed'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('createlisting', views.createlisting, name="createlisting"),
    path("create", views.create, name='create'),
    path("listings/<int:name>", views.item, name='item'),
    path("bid/<int:name>", views.bid,name='bid'),
    path('watch', views.watch, name='watch'),
    path("watchlist/<int:name>", views.listwatch, name='listwatch'),
    path("removewatch/<int:name>", views.removewatch, name='removewatch'),
    path("comment/<int:name>", views.comment, name='comment'),
    path('categories', views.categories, name='categories'),
    path("viewbycategory/<str:name>", views.viewbycategory, name='viewbycategory'),
    path('endauction/<int:name>', views.endauction, name='endauction')
]
