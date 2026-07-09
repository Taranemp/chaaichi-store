from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Avg
from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()


class ReviewStatusType(models.IntegerChoices):
    PENDING = 1, "Pending"
    APPROVED = 2, "Approved"
    REJECTED = 3, "Rejected"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    rate = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.IntegerField(
        choices=ReviewStatusType.choices,
        default=ReviewStatusType.PENDING.value
    )
    is_purchased = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        # unique_together حذف شد: حالا هر کاربر می‌تونه برای یک محصول چندین دیدگاه ثبت کنه

    def __str__(self):
        return f"{self.user.phone} - {self.product.title} - {self.rate}★"

    def get_status(self):
        return {
            "id": self.status,
            "name": ReviewStatusType(self.status).name,
            "label": ReviewStatusType(self.status).label,
        }

    def is_approved(self):
        return self.status == ReviewStatusType.APPROVED.value


@receiver(post_save, sender=Review)
def update_product_avg_rating_on_save(sender, instance, **kwargs):
    if instance.status == ReviewStatusType.APPROVED.value:
        _update_product_avg_rating(instance.product)


@receiver(post_delete, sender=Review)
def update_product_avg_rating_on_delete(sender, instance, **kwargs):
    _update_product_avg_rating(instance.product)


def _update_product_avg_rating(product):
    avg_rating = Review.objects.filter(
        product=product,
        status=ReviewStatusType.APPROVED.value
    ).aggregate(Avg('rate'))['rate__avg']

    product.avg_rating = round(avg_rating, 1) if avg_rating else 0
    product.reviews_count = Review.objects.filter(
        product=product,
        status=ReviewStatusType.APPROVED.value
    ).count()
    product.save(update_fields=['avg_rating', 'reviews_count'])