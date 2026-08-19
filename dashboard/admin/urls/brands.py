from django.urls import path
from dashboard.admin.views import brands as views

app_name = 'brands'

urlpatterns = [
    path('', views.BrandListView.as_view(), name='brand-list'),
    path('create/', views.BrandCreateView.as_view(), name='brand-create'),
    path('<int:pk>/update/', views.BrandUpdateView.as_view(), name='brand-update'),
    path('<int:pk>/delete/', views.BrandDeleteView.as_view(), name='brand-delete'),
]