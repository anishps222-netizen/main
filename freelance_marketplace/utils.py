
from .models import User, Category, Gig

def create_sample_gigs():
    freelancer_user, _ = User.objects.get_or_create(username="default_freelancer", defaults={"role": "freelancer"})

    categories = {
        "programming-tech": [
            {"title": "Website Development", "price": 50},
            {"title": "Python Automation", "price": 40},
            {"title": "Mobile App Development", "price": 60},
            {"title": "API Integration", "price": 45},
        ],
        "graphic-design": [
            {"title": "Logo Design", "price": 30},
            {"title": "Business Card Design", "price": 20},
            {"title": "Flyer Design", "price": 25},
            {"title": "Banner Design", "price": 15},
        ],
        "digital-marketing": [
            {"title": "SEO Optimization", "price": 40},
            {"title": "Social Media Marketing", "price": 35},
            {"title": "Email Marketing", "price": 30},
            {"title": "Content Marketing", "price": 25},
        ],
        "writing-translations": [
            {"title": "Blog Writing", "price": 20},
            {"title": "Copywriting", "price": 25},
            {"title": "Proofreading", "price": 15},
            {"title": "Translation Service", "price": 30},
        ],
        "video-animation": [
            {"title": "Explainer Video", "price": 50},
            {"title": "Animation Video", "price": 45},
            {"title": "Video Editing", "price": 35},
            {"title": "Social Media Video", "price": 25},
        ],
        "ai-services": [
            {"title": "AI Chatbot Development", "price": 60},
            {"title": "AI Data Analysis", "price": 55},
            {"title": "AI Image Generation", "price": 50},
            {"title": "AI Automation Scripts", "price": 45},
        ],
    }

    for slug, gigs_list in categories.items():
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            print(f"Category with slug '{slug}' not found, skipping...")
            continue

        for gig_data in gigs_list:
            Gig.objects.get_or_create(
                freelancer=freelancer_user,
                category=category,
                title=gig_data['title'],
                defaults={
                    "description": gig_data['title'] + " description",
                    "price": gig_data['price'],
                    "created_by": freelancer_user,
                }
            )
    print("Sample gigs created successfully!")
