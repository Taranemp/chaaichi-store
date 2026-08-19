from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from shop.models import Grade, PackageType
from dashboard.admin.forms.attributes import GradeForm, PackageTypeForm

# --- درجه‌های کیفی (Grades) ---

class GradeListView(ListView):
    model = Grade
    template_name = 'dashboard/admin/attributes/grade_list.html'
    context_object_name = 'grades'


class GradeCreateView(SuccessMessageMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'dashboard/admin/attributes/grade_form.html'
    success_url = reverse_lazy('dashboard:admin:attributes:grade-list')
    success_message = "درجه کیفی جدید با موفقیت ثبت شد."


class GradeUpdateView(SuccessMessageMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'dashboard/admin/attributes/grade_form.html'
    success_url = reverse_lazy('dashboard:admin:attributes:grade-list')
    success_message = "درجه کیفی بروزرسانی شد."


class GradeDeleteView(DeleteView):
    model = Grade
    template_name = 'dashboard/admin/attributes/attribute_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin:attributes:grade-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "درجه کیفی حذف شد.")
        return super().delete(request, *args, **kwargs)


# --- انواع بسته‌بندی (PackageTypes) ---

class PackageTypeListView(ListView):
    model = PackageType
    template_name = 'dashboard/admin/attributes/package_list.html'
    context_object_name = 'packages'


class PackageTypeCreateView(SuccessMessageMixin, CreateView):
    model = PackageType
    form_class = PackageTypeForm
    template_name = 'dashboard/admin/attributes/package_form.html'
    success_url = reverse_lazy('dashboard:admin:attributes:package-list')
    success_message = "نوع بسته‌بندی جدید ثبت شد."


class PackageTypeUpdateView(SuccessMessageMixin, UpdateView):
    model = PackageType
    form_class = PackageTypeForm
    template_name = 'dashboard/admin/attributes/package_form.html'
    success_url = reverse_lazy('dashboard:admin:attributes:package-list')
    success_message = "نوع بسته‌بندی بروزرسانی شد."


class PackageTypeDeleteView(DeleteView):
    model = PackageType
    template_name = 'dashboard/admin/attributes/attribute_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin:attributes:package-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "نوع بسته‌بندی حذف شد.")
        return super().delete(request, *args, **kwargs)