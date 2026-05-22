from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class CustomManager(BaseUserManager):

    def create_user(self, fullname, phone, email=None, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required.")

        if not fullname:
            raise ValueError("Fullname is required.")

        email = self.normalize_email(email) if email else None

        user = self.model(
            fullname=fullname,
            phone=phone,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, fullname, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            fullname=fullname,
            phone=phone,
            email=email,
            password=password,
            is_active=True,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, null=True, blank=True) # email is optional and NOT unique.
    phone = models.CharField(max_length=11, unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["fullname", "email"]  # phone is not submitted, because it is the USERNAME_FIELD.

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.fullname
