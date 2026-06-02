# shop/management/commands/seed_helpers/products.py
from shop.models import Product, ProductStatusType


def create_or_link_product(
    title, slug, brand, grade, package, 
    price, stock, description, brief_description, stdout
):
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "title": title,
            "brand": brand,
            "grade": grade,
            "package": package,
            "price": price,
            "stock": stock,
            "description": description,
            "brief_description": brief_description,
            "status": ProductStatusType.PUBLISH.value,
        }
    )
    if created:
        stdout.write(f'  Product "{title}" created - {price:,} Toman')
    return product


def create_products(stdout, categories, brands, grades, packages):
    products_data = [
        {
            "title": "Black Tea",
            "slug": "noorjafari-black-tea",
            "brand_key": "noorjafari",
            "grade_key": "premium",
            "package_key": "box",
            "price": 315000,
            "stock": 50,
            "description": "Premium black tea from NoorJafari.",
            "brief_description": "Premium black tea",
            "category_keys": ["black-tea"]
        },
        {
            "title": "Lahijan Tea",
            "slug": "noorjafari-lahijan-tea",
            "brand_key": "noorjafari",
            "grade_key": "special",
            "package_key": "tin",
            "price": 280000,
            "stock": 45,
            "description": "Special tea from Lahijan region.",
            "brief_description": "Lahijan special tea",
            "category_keys": ["lahijan-tea", "black-tea"]
        },
        {
            "title": "Special Qalam",
            "slug": "noorjafari-special-qalam",
            "brand_key": "noorjafari",
            "grade_key": "special",
            "package_key": "bag",
            "price": 240000,
            "stock": 75,
            "description": "Special Qalam large leaf black tea.",
            "brief_description": "Special Qalam tea",
            "category_keys": ["black-tea"]
        },
        {
            "title": "Premium Tea",
            "slug": "noorjafari-premium-tea",
            "brand_key": "noorjafari",
            "grade_key": "premium",
            "package_key": "gift-box",
            "price": 120000,
            "stock": 200,
            "description": "Premium tea in gift box.",
            "brief_description": "Gift box tea",
            "category_keys": ["black-tea", "lahijan-tea"]
        },
        {
            "title": "Black Tea",
            "slug": "ghazal-black-tea",
            "brand_key": "ghazal",
            "grade_key": "grade-1",
            "package_key": "box",
            "price": 180000,
            "stock": 60,
            "description": "Iranian black tea from Ghazal.",
            "brief_description": "Ghazal black tea",
            "category_keys": ["black-tea"]
        },
        {
            "title": "Green Tea",
            "slug": "ghazal-green-tea",
            "brand_key": "ghazal",
            "grade_key": "grade-1",
            "package_key": "box",
            "price": 190000,
            "stock": 55,
            "description": "Fresh green tea from Ghazal.",
            "brief_description": "Ghazal green tea",
            "category_keys": ["green-tea"]
        },
        {
            "title": "Black Tea",
            "slug": "refaah-black-tea",
            "brand_key": "refaah",
            "grade_key": "economy",
            "package_key": "loose",
            "price": 85000,
            "stock": 150,
            "description": "Economy black tea from Refaah.",
            "brief_description": "Refaah black tea",
            "category_keys": ["black-tea"]
        },
        {
            "title": "Teabag",
            "slug": "refaah-teabag",
            "brand_key": "refaah",
            "grade_key": "economy",
            "package_key": "bag",
            "price": 75000,
            "stock": 200,
            "description": "Convenient teabags from Refaah.",
            "brief_description": "Refaah teabag",
            "category_keys": ["teabag"]
        },
    ]
    
    created_count = 0
    for data in products_data:
        product = create_or_link_product(
            title=data["title"],
            slug=data["slug"],
            brand=brands.get(data["brand_key"]),
            grade=grades.get(data["grade_key"]),
            package=packages.get(data["package_key"]),
            price=data["price"],
            stock=data["stock"],
            description=data["description"],
            brief_description=data["brief_description"],
            stdout=stdout
        )
        
        for cat_key in data["category_keys"]:
            cat = categories.get(cat_key)
            if cat:
                product.category.add(cat)
        
        created_count += 1
    
    stdout.write(f'✅ Created {created_count} products')