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

    path('', include('HOME.urls')),
    path('auth/', include('AUTHENTICATE.urls')),
    path('poll/', include('PARLEYPRO.urls')),
    path('philanthropy/', include('PHILANTHROPY.urls')),
    path('newmember/', include('NEWMEMBER.urls')),
    path('sobersheet/', include('SOBERSHEET.urls')),
]

# In production nginx serves /static/ and /media/; these only apply while developing
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
