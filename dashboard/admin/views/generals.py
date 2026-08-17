from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from django.contrib.auth import get_user_model

from shop.models import Product 
from order.models import Order, OrderStatusType
from account.models import UserType

User = get_user_model()


class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = "dashboard/admin/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ۱. کل محصولات
        context['total_products'] = Product.objects.count()

        # ۲. سفارشات موفق
        context['success_orders'] = Order.objects.filter(
            status=OrderStatusType.SUCCESS.value
        ).count()

        # ۳. سفارشات در انتظار
        context['pending_orders'] = Order.objects.filter(
            status=OrderStatusType.PENDING.value
        ).count()

        # شمارش فقط کاربران مشتری (غیر ادمین)
        context['total_users'] = User.objects.filter(type=UserType.customer.value).count()  

        # ۵. آخرین ۵ سفارش برای جدول همراه با بهینه‌سازی کوئری
        context['recent_orders'] = Order.objects.select_related(
            'user', 'user__profile'
        ).order_by('-created_date')[:5]

        return context