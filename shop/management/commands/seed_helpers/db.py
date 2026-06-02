import os
import shutil
from django.conf import settings
from django.core.management import call_command
from django.apps import apps
import importlib.util


def remove_and_migrate_db(stdout):
    # ---------- Delete db.sqlite3 ----------
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        stdout.write('✅ DB removed successfully.')
    else:
        stdout.write('⚠️ DB does not exist.')

    # ---------- Delete all migration files (except __init__.py) ----------
    for app_config in apps.get_app_configs():
        app_name = app_config.name
        if app_name.startswith('django.'):
            continue

        try:
            app_path = app_config.path
            migrations_path = os.path.join(app_path, 'migrations')
            
            if os.path.exists(migrations_path):
                for filename in os.listdir(migrations_path):
                    if filename != '__init__.py' and filename.endswith('.py'):
                        file_path = os.path.join(migrations_path, filename)
                        os.remove(file_path)
                        stdout.write(f'  Removed: {app_name}/migrations/{filename}')
                
                # Delete __pycache__ if exists
                pycache_path = os.path.join(migrations_path, '__pycache__')
                if os.path.exists(pycache_path):
                    shutil.rmtree(pycache_path)
                        
        except Exception as e:
            stdout.write(f'⚠️ Error checking migrations for {app_name}: {e}')

    # ---------- Run migrations ----------
    try:
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)
        stdout.write('✅ Migrations applied successfully.')
    except Exception as e:
        stdout.write(f'❌ Migration Failed: {e}')