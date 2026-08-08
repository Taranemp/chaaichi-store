from django.views.generic import UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission

from dashboard.admin.forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError

from review.models import Review, ReviewStatusType


class AdminReviewListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView
):

    template_name = "dashboard/admin/reviews/review-list.html"
    model = Review
    paginate_by = 10


    def get_paginate_by(self, queryset):
        return self.request.GET.get(
            'page_size',
            self.paginate_by
        )


    def get_queryset(self):

        queryset = Review.objects.select_related(
            "user",
            "product"
        ).all()


        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(
                product__title__icontains=search_q
            )


        status = self.request.GET.get("status")

        if status:
            queryset = queryset.filter(
                status=status
            )


        order_by = self.request.GET.get("order_by")

        if order_by:
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass


        return queryset



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        reviews = self.get_queryset()


        # ===============================
        # Stats Cards
        # ===============================

        context["total_items"] = reviews.count()


        context["pending_count"] = reviews.filter(
            status=ReviewStatusType.PENDING.value
        ).count()


        context["approved_count"] = reviews.filter(
            status=ReviewStatusType.APPROVED.value
        ).count()


        context["rejected_count"] = reviews.filter(
            status=ReviewStatusType.REJECTED.value
        ).count()



        context["status_types"] = ReviewStatusType.choices


        return context




class AdminReviewEditView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView
):

    template_name = "dashboard/admin/reviews/review-edit.html"

    model = Review

    form_class = ReviewForm

    success_message = "تغییرات با موفقیت اعمال شد"



    def get_success_url(self):

        return reverse_lazy(
            "dashboard:admin:reviews:review-list"
        )



    def form_valid(self, form):

        if "status" in self.request.POST:

            form.instance.status = self.request.POST.get(
                "status"
            )


        return super().form_valid(form)