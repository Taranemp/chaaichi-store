
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


app_name = 'core'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('', include('blog.urls')),
    path('', include('website.urls')),
    path('shop/', include('shop.urls')),
    path('payment/', include('payment.urls')),
    path('order/', include('order.urls')),
    path('cart/', include('cart.urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)





