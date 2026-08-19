from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from shop.models import Brand
from dashboard.admin.forms.brands import BrandForm


class BrandListView(ListView):
    model = Brand
    template_name = 'dashboard/admin/brands/brand_list.html'
    context_object_name = 'brands'
    paginate_by = 10


class BrandCreateView(SuccessMessageMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'dashboard/admin/brands/brand_form.html'
    success_url = reverse_lazy('dashboard:admin:brands:brand-list')
    success_message = "برند جدید با موفقیت ثبت شد."


class BrandUpdateView(SuccessMessageMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'dashboard/admin/brands/brand_form.html'
    success_url = reverse_lazy('dashboard:admin:brands:brand-list')
    success_message = "اطلاعات برند با موفقیت بروزرسانی شد."


class BrandDeleteView(DeleteView):
    model = Brand
    template_name = 'dashboard/admin/brands/brand_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin:brands:brand-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "برند مورد نظر حذف شد.")
        return super().delete(request, *args, **kwargs)