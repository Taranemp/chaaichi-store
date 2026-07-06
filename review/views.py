from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from shop.models import Product
from .forms import SubmitReviewForm
from .models import Review


class SubmitReviewView(LoginRequiredMixin, CreateView):
    """ارسال نظر برای محصول"""
    template_name = "review/submit_review.html"
    form_class = SubmitReviewForm
    model = Review

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['product'] = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shop:product-detail', kwargs={'slug': self.kwargs['product_slug']})