from django.urls import path
from dashboard.admin.views import categories as views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
]
