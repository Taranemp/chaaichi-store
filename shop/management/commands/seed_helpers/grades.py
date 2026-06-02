from shop.models import Grade


def create_or_link_grade(name, slug, level, stdout):
    grade, created = Grade.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "level": level}
    )
    if created:
        stdout.write(f'  Grade "{name}" (level {level}) created')
    return grade


def create_grades(stdout):
    grades_data = [
        {"name": "Premium", "slug": "premium", "level": 1},
        {"name": "Grade 1", "slug": "grade-1", "level": 2},
        {"name": "Grade 2", "slug": "grade-2", "level": 3},
        {"name": "Special", "slug": "special", "level": 4},
        {"name": "Economy", "slug": "economy", "level": 5},
    ]
    
    grades = {}
    for data in grades_data:
        obj = create_or_link_grade(data["name"], data["slug"], data["level"], stdout)
        grades[data["slug"]] = obj
    
    stdout.write(f'✅ Created {len(grades_data)} grades')
    return grades