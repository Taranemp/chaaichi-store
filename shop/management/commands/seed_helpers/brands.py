# shop/management/commands/seed_helpers/brands.py
from shop.models import Brand


def create_or_link_brand(name, slug, description, stdout):
    brand, created = Brand.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "description": description}
    )
    if created:
        stdout.write(f'  Brand "{name}" created')
    return brand


def create_brands(stdout):
    brands_data = [
        {"name": "NoorJafari", "slug": "noorjafari", "description": "Premium tea from Lahijan, Iran"},
        {"name": "Ghazal", "slug": "ghazal", "description": "Iranian tea brand"},
        {"name": "Refaah", "slug": "refaah", "description": "Iranian tea brand"},
    ]
    
    brands = {}
    for data in brands_data:
        obj = create_or_link_brand(data["name"], data["slug"], data["description"], stdout)
        brands[data["slug"]] = obj
    
    stdout.write(f'✅ Created {len(brands_data)} brands')
    return brands