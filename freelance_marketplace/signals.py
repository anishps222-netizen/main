from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Order, Notification

@receiver(post_save, sender=Order)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            order=instance,
            message=f"New order for your gig: {instance.gig.title}"
        )

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name != 'freelance_marketplace':
        return

    default_cats = [
        ("Programming & Tech", "programming-tech"),
        ("Graphic & Design", "graphic-design"),
        ("Digital Marketing", "digital-marketing"),
        ("Writing & Translations", "writing-translations"),
        ("Video & Animation", "video-animation"),
        ("AI Services", "ai-services"),
    ]

    from .models import Category
    for name, slug in default_cats:
        Category.objects.get_or_create(slug=slug, defaults={'name': name})
