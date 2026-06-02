# shop/management/commands/seed_helpers/users.py
from django.contrib.auth import get_user_model

User = get_user_model()


def create_super_user(stdout):
    phone = "09338484618"
    password = "Admin@123"
    fullname = "Salar Khosravi"
    email = "salar.khosravi@gmail.com"

    if not User.objects.filter(phone=phone).exists():
        User.objects.create_superuser(
            phone=phone,
            fullname=fullname,
            email=email,
            password=password
        )
        stdout.write(f'✅ Superuser "{phone}" created')
    else:
        # اگر وجود داشت، رمز رو آپدیت کن
        user = User.objects.get(phone=phone)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        stdout.write(f'✅ Superuser "{phone}" password updated')
    
    return phone, password