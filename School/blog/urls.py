from django.urls import path
from .views import *

urlpatterns = [
    path('', blog),
    path('<slug>/', blog_view),
    path('<slug>/edit', blog_edit_view),
    path('<slug>/delete', blog_delete_view),
]
