"""
URL configuration for LITRevu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from applicationLITRevu.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('tickets/add/', add_ticket, name='add_ticket'),
    path('tickets/edit/<int:ticket_id>/', edit_ticket, name='edit_ticket'),
    path('tickets/delete/<int:ticket_id>/', delete_ticket, name='delete_ticket'),
    path('reviews/create/', create_review, name='create_review'),
    path('tickets/<int:ticket_id>/reviews/add/', add_review, name='add_review'),
    path('reviews/<int:review_id>/edit/', edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('users/follows/', user_follows, name='user_follows'),
    path('users/unfollow/<int:user_id>/', unfollow_user, name='unfollow_user'),
    path('feed/', feed, name='feed'),
    path('posts/', posts, name='posts'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)