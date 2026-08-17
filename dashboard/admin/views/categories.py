from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from shop.models import Category
from dashboard.admin.forms.categories import CategoryForm


class CategoryListView(ListView):
    model = Category
    template_name = 'dashboard/admin/categories/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10


class CategoryCreateView(SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/admin/categories/category_form.html'
    success_url = reverse_lazy('dashboard:admin:category-list')
    success_message = "دسته‌بندی جدید با موفقیت ایجاد شد."


class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/admin/categories/category_form.html'
    success_url = reverse_lazy('dashboard:admin:category-list')
    success_message = "دسته‌بندی با موفقیت بروزرسانی شد."


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'dashboard/admin/categories/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin:category-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "دسته‌بندی با موفقیت حذف شد.")
        return super().delete(request, *args, **kwargs)