# shop/management/commands/seed_helpers/users.py
from django.contrib.auth import get_user_model

User = get_user_model()


def create_super_user(stdout):
    phone = "09338484618"
    password = "Admin@123"
    fullname = "Salar Khosravi"
    email = "salar.khosravi@gmail.com"

    if not User.objects.filter(phone=phone).exists():
        user = User.objects.create_superuser(
            phone=phone,
            password=password,
            email=email,
            # fullname حذف شد
        )
        # ذخیره fullname در پروفایل
        if hasattr(user, 'profile'):
            user.profile.first_name = fullname
            user.profile.save()
        stdout.write(f'✅ Superuser "{phone}" created')
    else:
        user = User.objects.get(phone=phone)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        stdout.write(f'✅ Superuser "{phone}" password updated')
    
    return phone, password