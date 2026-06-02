from shop.models import Category


def create_or_link_category(title, slug, stdout):
    category, created = Category.objects.get_or_create(
        slug=slug,
        defaults={"title": title}
    )
    if created:
        stdout.write(f'  Category "{title}" created')
    return category


def create_categories(stdout):
    categories_data = [
        {"title": "Black Tea", "slug": "black-tea"},
        {"title": "Green Tea", "slug": "green-tea"},
        {"title": "Teabag", "slug": "teabag"},
        {"title": "Herbal Tea", "slug": "herbal-tea"},
        {"title": "Lahijan Tea", "slug": "lahijan-tea"},
    ]
    
    categories = {}
    for data in categories_data:
        obj = create_or_link_category(data["title"], data["slug"], stdout)
        categories[data["slug"]] = obj
    
    stdout.write(f'✅ Created {len(categories_data)} categories')
    return categories