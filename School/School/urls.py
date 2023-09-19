from django.contrib import admin
from django.urls import path, include
from accounts.views import (
    login_view,
    logout_view,
    account,
)
from .views import (
    home,
    new_view,
    about_us,
    contact_us,
    news
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path("login/", login_view),
    path('logout/', logout_view),
    path('new/', news),
    path('new/<str:slug>', new_view),
    path('account/', account),
    path('about-us', about_us),
    path('contact-us', contact_us),
    path('account/', include('LMS.urls')),
    path('blog/', include('blog.urls'))
]
