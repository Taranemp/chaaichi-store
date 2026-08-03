from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse


class ProductStatusType(models.IntegerChoices):
    PUBLISH = 1, "Publish"
    DRAFT = 2, "Draft"


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("shop:category_detail", args=[self.slug])


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(allow_unicode=True, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    description = models.TextField(blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["name"]
        
    def __str__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(allow_unicode=True, unique=True)
    level = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
        ordering = ["level"]
        
    def __str__(self):
        return self.name


class PackageType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(allow_unicode=True, unique=True)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        if self.weight_grams:
            return f"{self.name} - {self.weight_grams}g"
        return self.name




class Product(models.Model):

    category = models.ManyToManyField(Category)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    package = models.ForeignKey(
        PackageType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        allow_unicode=True,
        unique=True
    )

    image = models.ImageField(
        upload_to="products/img/",
        default="/default/product-image.png"
    )

    description = models.TextField()

    brief_description = models.TextField(
        blank=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    status = models.IntegerField(
        choices=ProductStatusType.choices,
        default=ProductStatusType.DRAFT.value
    )

    # قیمت اصلی محصول
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="قیمت اصلی"
    )

    # درصد تخفیف محصول
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name="درصد تخفیف"
    )

    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0
    )

    reviews_count = models.PositiveIntegerField(
        default=0
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return self.title


    @property
    def discount_amount(self):
        """
        مبلغ تخفیف محصول
        مثال:
        قیمت 850000
        تخفیف 5%
        خروجی: 42500
        """
        if self.discount_percent:
            return round(
                self.price * Decimal(
                    self.discount_percent / 100
                )
            )

        return Decimal(0)


    @property
    def final_price(self):
        """
        قیمت نهایی بعد از تخفیف
        """
        return self.price - self.discount_amount


    @property
    def has_discount(self):
        return self.discount_percent > 0


    def get_price(self):
        """
        برای سازگاری با کدهای قبلی
        """
        return self.final_price


    def get_price_with_comma(self):
        return f"{self.final_price:,}"


    def is_published(self):
        return self.status == ProductStatusType.PUBLISH.value


    def get_absolute_url(self):
        return reverse(
            "shop:product_detail",
            args=[self.slug]
        )

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    file = models.ImageField(upload_to="products/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return f"Image for {self.product.title}"
    
    

class WishlistProductModel(models.Model):

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_date"]
        unique_together = [["user", "product"]]  
    def __str__(self):
        return f"{self.user.phone} - {self.product.title}"