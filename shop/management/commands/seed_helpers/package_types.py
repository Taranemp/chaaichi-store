from shop.models import PackageType


def create_or_link_package_type(name, slug, weight_grams, stdout):
    package, created = PackageType.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "weight_grams": weight_grams}
    )
    if created:
        weight_str = f"{weight_grams}g" if weight_grams else "variable"
        stdout.write(f'  Package type "{name}" ({weight_str}) created')
    return package


def create_package_types(stdout):
    packages_data = [
        {"name": "Box", "slug": "box", "weight_grams": 500},
        {"name": "Loose", "slug": "loose", "weight_grams": None},
        {"name": "Bag", "slug": "bag", "weight_grams": 25},
        {"name": "Tin", "slug": "tin", "weight_grams": 200},
        {"name": "Gift Box", "slug": "gift-box", "weight_grams": 1000},
    ]
    
    packages = {}
    for data in packages_data:
        obj = create_or_link_package_type(data["name"], data["slug"], data["weight_grams"], stdout)
        packages[data["slug"]] = obj
    
    stdout.write(f'✅ Created {len(packages_data)} package types')
    return packages