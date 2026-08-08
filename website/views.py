from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
# from .forms import ContactForm
from django.contrib import messages
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .forms import ContactForm
from .models import Contact

from shop.models import Category, Product, ProductStatusType




class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()[:4]
        context["discount_products"] = (
            Product.objects
            .filter(
                status=ProductStatusType.PUBLISH.value,
                discount_percent__gt=0
            )
            .order_by("-created_date")[:8]
        )
        return context


class ContactView(TemplateView):
    template_name = "website/contact.html"

class AboutView(TemplateView):
    template_name = "website/about.html"




class SendContactView(CreateView):
    """
    ارسال پیام تماس با ما
    """
    http_method_names = ['post']
    model = Contact
    form_class = ContactForm

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 
            'پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 
            'مشکلی در ارسال پیام وجود دارد. لطفاً فیلدها را بررسی کنید.'
        )
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def get_success_url(self):
        return reverse('website:contact')