from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

app_name = 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('blog/', include('blog.urls')),
    path('', include('website.urls')),
    path('shop/', include('shop.urls')),
    path('payment/', include('payment.urls')),
    path('order/', include('order.urls')),
    path('cart/', include('cart.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('review/', include('review.urls', namespace='review')),
    path('wallet/deposit/', include('wallet.urls', namespace='wallet')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )