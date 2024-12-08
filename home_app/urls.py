from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('course/<slug>/', views.course_detail, name='course'),
    path('become-pro/', views.become_pro, name='become_pro'),
    path('charge/', views.charge, name='charge'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
]
