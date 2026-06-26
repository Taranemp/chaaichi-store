from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from account.validators import validate_iranian_cellphone_number


class UserType(models.IntegerChoices):
    customer = 1, _("customer")
    admin = 2, _("admin")
    superuser = 3, _("superuser")


class UserManager(BaseUserManager):
    """
    Custom user model manager where phone is the unique identifier
    for authentication instead of username or email.
    """

    def create_user(self, phone, password=None, **extra_fields):
        """
        Create and save a User with the given phone and password.
        """
        if not phone:
            raise ValueError(_("The Phone number must be set"))
        
        # اعتبارسنجی شماره تلفن
        try:
            validate_iranian_cellphone_number(phone)
        except:
            raise ValueError(_("Enter a valid Iranian cellphone number"))

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given phone and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.superuser.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with phone as unique identifier.
    """
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_iranian_cellphone_number],
        verbose_name=_("Phone Number")
    )
    email = models.EmailField(
        _("Email Address"),
        blank=True,
        null=True,
        help_text="Optional email address"
    )
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    type = models.IntegerField(
        choices=UserType.choices,
        default=UserType.customer.value
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]  # هنگام createsuperuser ایمیل هم خواسته می‌شود

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.phone

    def get_fullname(self):
        if hasattr(self, 'profile'):
            return self.profile.get_fullname()
        return self.phone


class Profile(models.Model):
    """
    User profile model for additional information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to="profiles/",
        default="profiles/default.png",
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.phone} - {self.get_fullname()}"

    def get_fullname(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return "New User"


# Signal to auto-create profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()