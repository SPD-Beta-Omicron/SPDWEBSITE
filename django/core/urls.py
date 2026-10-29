"""
Top-level URL routes. Each app's own urls.py holds its pages.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # The admin path comes from .env so it isn't guessable
    path(f'{settings.ADMIN_URL}/', admin.site.urls),

    path('', include('home.urls')),
    path('auth/', include('authenticate.urls')),
    path('poll/', include('polls.urls')),
    path('philanthropy/', include('philanthropy.urls')),
    path('newmember/', include('newmember.urls')),
    path('sobersheet/', include('sobersheet.urls')),
]

# In production nginx serves /static/ and /media/; these only apply while developing
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
