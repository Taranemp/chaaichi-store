from django.urls import path
from dashboard.admin.views import attributes as views

app_name = 'attributes'

urlpatterns = [
    # Grades
    path('grades/', views.GradeListView.as_view(), name='grade-list'),
    path('grades/create/', views.GradeCreateView.as_view(), name='grade-create'),
    path('grades/<int:pk>/update/', views.GradeUpdateView.as_view(), name='grade-update'),
    path('grades/<int:pk>/delete/', views.GradeDeleteView.as_view(), name='grade-delete'),

    # Packages
    path('packages/', views.PackageTypeListView.as_view(), name='package-list'),
    path('packages/create/', views.PackageTypeCreateView.as_view(), name='package-create'),
    path('packages/<int:pk>/update/', views.PackageTypeUpdateView.as_view(), name='package-update'),
    path('packages/<int:pk>/delete/', views.PackageTypeDeleteView.as_view(), name='package-delete'),
]