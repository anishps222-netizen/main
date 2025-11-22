from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('freelancer', 'Freelancer'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Gig(models.Model):
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_gigs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='gigs/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_gigs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_orders'
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_orders'
    )
    gig = models.ForeignKey('Gig', on_delete=models.CASCADE)
    is_pending = models.BooleanField(default=True)   
    is_completed = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.gig.title}"

class ChatMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} on Order {self.order.id}"


class ProjectPost(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'customer'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    def __str__(self):
        return self.title


class Offer(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='offers')
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'freelancer'}
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer on {self.gig.title} by {self.freelancer.username}"


class GigOrder(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} ordered {self.gig.title}"


class Review(models.Model):
    gig = models.ForeignKey(Gig, related_name='reviews', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.gig.title}"


class Freelancer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    skills = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class AdminManager(BaseUserManager):
    def create_admin(self, email, password=None):
        if not email:
            raise ValueError("Admins must have an email address")
        admin = self.model(email=self.normalize_email(email))
        admin.set_password(password)
        admin.save(using=self._db)
        return admin

class CustomAdmin(AbstractBaseUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = AdminManager()

    def __str__(self):
        return self.full_name


class Notification(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

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

    for name, slug in default_cats:
        Category.objects.get_or_create(slug=slug, defaults={'name': name})


@receiver(post_migrate)
def create_default_gigs(sender, **kwargs):
    if sender.name != 'freelance_marketplace':
        return

    freelancer, created = CustomUser.objects.get_or_create(
        username='default_freelancer',
        defaults={
            'role': 'freelancer',
            'email': 'freelancer@example.com',
        }
    )
    if created:
        freelancer.set_password('pass1234')
        freelancer.save()

    gigs_data = {
        "programming-tech": [
            ("Full Stack Web Development", "I will develop a full stack web application using Django and React.", 500),
            ("Python Automation Scripts", "I will write Python scripts to automate your repetitive tasks.", 150),
            ("Custom API Development", "I will create REST APIs for your web or mobile app.", 300),
            ("Website Bug Fixing & Optimization", "I will fix bugs and optimize your website performance.", 100),
        ],
        "graphic-design": [
            ("Logo Design", "I will create a professional and creative logo for your brand.", 120),
            ("Business Card Design", "I will design elegant and minimal business cards.", 80),
            ("Social Media Banners", "I will create engaging banners for your social media.", 90),
            ("UI/UX Design", "I will design intuitive UI/UX for web or mobile apps.", 250),
        ],
        "digital-marketing": [
            ("SEO Optimization", "I will optimize your website for better search rankings.", 200),
            ("Social Media Marketing", "I will manage and grow your social media accounts.", 300),
            ("Email Campaign Setup", "I will create and automate your email campaigns.", 150),
            ("Google Ads Setup", "I will set up high-converting Google Ads campaigns.", 250),
        ],
        "writing-translations": [
            ("Blog Article Writing", "I will write SEO-friendly blog articles.", 80),
            ("Website Copywriting", "I will write persuasive copy for your website.", 120),
            ("Proofreading & Editing", "I will proofread and edit your content for clarity.", 60),
            ("Technical Writing", "I will write professional technical documents.", 200),
        ],
        "video-animation": [
            ("Explainer Video", "I will create animated explainer videos for your business.", 300),
            ("Logo Animation", "I will animate your logo in a professional way.", 150),
            ("YouTube Intro/Outro", "I will create intro and outro videos for your channel.", 100),
            ("Motion Graphics", "I will create stunning motion graphic animations.", 400),
        ],
        "ai-services": [
            ("AI Chatbot Development", "I will build a custom AI chatbot for your business.", 500),
            ("AI Image Generation", "I will generate stunning AI images using advanced models.", 200),
            ("Text-to-Speech Setup", "I will implement AI-based voice synthesis for your project.", 250),
            ("Data Analysis with AI", "I will analyze your data using AI tools and models.", 350),
        ],
    }

    for slug, gigs in gigs_data.items():
        category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': slug.replace("-", " ").title()})
        for title, description, price in gigs:
            Gig.objects.get_or_create(
                title=title,
                freelancer=freelancer,
                defaults={
                    'description': description,
                    'category': category,
                    'price': price,
                    'created_by': freelancer,
                }
            )
