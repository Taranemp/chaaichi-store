# shop/management/commands/seed_data.py
import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.apps import apps

from .seed_helpers.db import remove_and_migrate_db
from .seed_helpers.users import create_super_user
from .seed_helpers.categories import create_categories
from .seed_helpers.brands import create_brands
from .seed_helpers.grades import create_grades
from .seed_helpers.package_types import create_package_types
from .seed_helpers.products import create_products


class Command(BaseCommand):
    help = "Seed database with tea store data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🌱 Starting seed data process..."))

        # 1. Remove DB and migrations, then migrate
        remove_and_migrate_db(self.stdout)

        # 2. Create superuser
        self.stdout.write(self.style.WARNING("Creating superuser..."))
        phone, password = create_super_user(self.stdout)

        # 3. Seed all data
        self.stdout.write(self.style.WARNING("Seeding data..."))
        
        categories = create_categories(self.stdout)
        brands = create_brands(self.stdout)
        grades = create_grades(self.stdout)
        package_types = create_package_types(self.stdout)
        create_products(self.stdout, categories, brands, grades, package_types)

        self.stdout.write(self.style.SUCCESS("✅ Seed data completed successfully!"))
        self.stdout.write(self.style.SUCCESS(f"🔐 Login with: Phone={phone}, Password={password}"))