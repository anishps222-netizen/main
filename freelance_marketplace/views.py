
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from .models import Category, Freelancer, Notification, Customer, Gig, GigOrder, Order, Review, ProjectPost
from .models import Order, ChatMessage
from .forms import SignUpForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse

User = get_user_model()


def home(request):
    categories = Category.objects.all()
    gigs = Gig.objects.all().order_by('-created_at')[:8]  
    return render(request, 'home.html', {'categories': categories, 'gigs': gigs})


def about_page(request):
    return render(request, 'about.html')


def mission_page(request):
    return render(request, 'mission.html')


def how_it_works_page(request):
    return render(request, 'how_it_works.html')


def contact_page(request):
    return render(request, 'contact.html')

def select_login(request):
    return render(request, 'freelance_marketplace/select_login.html')


def login_choice(request):
    return render(request, 'freelance_marketplace/login_choice.html')


def register_choice(request):
    return render(request, 'register_choice.html')


def admin_logout(request):
    logout(request)
    return redirect('freelance_marketplace:admin_login')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('email') 
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('freelance_marketplace:admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')
            return redirect('admin_login')

    return render(request, 'freelance_marketplace/admin_login.html')


def all_freelancers(request):
    freelancers = Freelancer.objects.select_related('user').all()

    context = {
        'freelancers': freelancers
    }
    return render(request, 'freelance_marketplace/all_freelancers.html', context)


def admin_freelancers(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    freelancers = Freelancer.objects.all()
    return render(request, 'freelance_marketplace/admin_freelancers.html', {'freelancers': freelancers})

def admin_customers(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    customers = Customer.objects.all()
    return render(request, 'freelance_marketplace/admin_customers.html', {'customers': customers})

def admin_gigs(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    gigs = Gig.objects.all()
    return render(request, 'freelance_marketplace/admin_gigs.html', {'gigs': gigs})

def admin_orders(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    orders = Order.objects.all()
    return render(request, 'freelance_marketplace/admin_orders.html', {'orders': orders})

def admin_reviews(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    reviews = Review.objects.all()
    return render(request, 'freelance_marketplace/admin_reviews.html', {'reviews': reviews})


def freelancer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and user.role == 'freelancer':
            login(request, user)
            return redirect('freelance_marketplace:home')

        messages.error(request, "Invalid username or password.")
        return redirect('freelance_marketplace:freelancer_login')

    return render(request, 'freelance_marketplace/freelancer_login.html')



def freelancer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('freelance_marketplace:freelancer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('freelance_marketplace:freelancer_register')

        user = User.objects.create_user(username=username, email=email, password=password, role='freelancer')
        Freelancer.objects.create(user=user)
        login(request, user)
        return redirect('freelance_marketplace:freelancer_dashboard')

    return render(request, 'freelance_marketplace/freelancer_register.html')




def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and user.role == 'customer':
            login(request, user)
            return redirect('freelance_marketplace:home')

        messages.error(request, "Invalid username or password.")
        return redirect('freelance_marketplace:customer_login')

    return render(request, 'freelance_marketplace/customer_login.html')


def customer_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('freelance_marketplace:customer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('freelance_marketplace:customer_register')

        user = User.objects.create_user(username=username, email=email, password=password, role='customer')
        Customer.objects.create(user=user)
        login(request, user)
        return redirect('freelance_marketplace:customer_dashboard')

    return render(request, 'freelance_marketplace/customer_register.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('freelance_marketplace:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('freelance_marketplace:register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('freelance_marketplace:home')
    return render(request, 'register.html')


def role_context(request):
    user = request.user
    return {
        'is_freelancer': hasattr(user, 'freelancer'),
        'is_customer': hasattr(user, 'customer'),
    }



def login_user(request):
    if request.method == "POST":
        pass
    return render(request, 'freelance_marketplace/login.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'freelancer') or getattr(user, 'role', None) == 'freelancer':
                return redirect('freelance_marketplace:freelancer_dashboard')
            elif hasattr(user, 'customer') or getattr(user, 'role', None) == 'customer':
                return redirect('freelance_marketplace:customer_dashboard')
            elif user.is_superuser or user.is_staff:
                return redirect('freelance_marketplace:admin_dashboard')
            else:
                messages.warning(request, "No dashboard assigned to your role.")
                return redirect('freelance_marketplace:home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('freelance_marketplace:select_login')

def logout_view(request):
    logout(request)
    return redirect('freelance_marketplace:select_login')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role = getattr(user, 'role', None)
            if role == 'freelancer' or getattr(user, 'is_freelancer', False):
                return redirect('freelance_marketplace:freelancer_dashboard')
            elif role == 'customer' or getattr(user, 'is_customer', False):
                return redirect('freelance_marketplace:customer_dashboard')
            elif user.is_superuser:
                return redirect('freelance_marketplace:admin_dashboard')
            else:
                return redirect('freelance_marketplace:home')
        else:
            return render(request, 'freelance_marketplace/login.html', {'error': 'Invalid username or password'})

    return render(request, 'freelance_marketplace/login.html')


def logout_user(request):
    logout(request)
    return redirect('freelance_marketplace:home')


@login_required
def dashboard_redirect(request):
    """
    Redirect users to the correct dashboard based on their type.
    """
    user = request.user

    if hasattr(user, 'customer'):
        return redirect('freelance_marketplace:customer_dashboard')
    elif hasattr(user, 'freelancer'):
        return redirect('freelance_marketplace:freelancer_dashboard')
    elif hasattr(user, 'admin'):
        return redirect('freelance_marketplace:admin_dashboard') 

def freelancer_order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('freelance_marketplace:freelancer_login')
    order = get_object_or_404(Order, id=order_id, gig__freelancer=request.user)

    context = {
        'order': order
    }
    return render(request, 'freelance_marketplace/freelancer_order_detail.html', context)


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('freelance_marketplace:admin_login')
    freelancers = Freelancer.objects.all()
    customers = Customer.objects.all()
    gigs = Gig.objects.all()
    orders = Order.objects.all()
    reviews = Review.objects.all()
    total_freelancers = freelancers.count()
    total_customers = customers.count()
    total_gigs = gigs.count()
    total_orders = orders.count()
    total_reviews = reviews.count()
    recent_gigs = gigs.order_by('-created_at')[:5]

    context = {
        'freelancers': freelancers,
        'customers': customers,
        'gigs': gigs,
        'orders': orders,
        'reviews': reviews,
        'total_freelancers': total_freelancers,
        'total_customers': total_customers,
        'total_gigs': total_gigs,
        'total_orders': total_orders,
        'total_reviews': total_reviews,
        'recent_gigs': recent_gigs,
    }

    return render(request, 'freelance_marketplace/admin_dashboard.html', context)


@login_required
def customer_dashboard(request):
    orders = GigOrder.objects.filter(customer=request.user)
    return render(request, 'freelance_marketplace/customer_dashboard.html', {'orders': orders})

@login_required
def freelancer_dashboard(request):
    user = request.user
    gigs =request. user.freelancer_gigs.all()
    total_gigs = gigs.count()
    orders = Order.objects.filter(gig__freelancer=request.user).order_by('-created_at')
    pending_orders = orders.filter(is_pending=True, is_completed=False)
    completed_orders = orders.filter(is_completed=True)

    context = {
        'gigs': gigs,
        'total_gigs':gigs.count(),
        'orders': orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
    }
    return render(request, 'freelance_marketplace/freelancer_dashboard.html', context)

@login_required
def freelancer_pending_orders(request):
    orders = Order.objects.filter(gig__freelancer=request.user, is_pending=True)
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.filter(id=order_id, gig__freelancer=request.user).first()
        if order:
            order.is_pending = False
            order.is_completed = True
            order.save()
        return redirect('freelance_marketplace:freelancer_pending_orders')
    return render(request, 'freelance_marketplace/freelancer_pending_orders.html', {'orders': orders})

def freelancer_completed_orders(request):
    orders = Order.objects.filter(gig__freelancer=request.user, is_completed=True)
    return render(request, 'freelance_marketplace/freelancer_completed_orders.html', {'orders': orders})



@login_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, gig__freelancer=request.user)
    if request.method == "POST":
        order.is_pending = False
        order.is_completed = False 
        order.save()
    return HttpResponseRedirect(reverse('freelance_marketplace:freelancer_dashboard'))


@login_required
def place_order(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)

    if request.method == "POST":
        order = Order.objects.create(
            gig=gig,
            customer=request.user,
            freelancer=gig.freelancer
        )
        return redirect('customer_dashboard') 

    return render(request, 'freelance_marketplace/place_order.html', {'gig': gig})


@login_required
def post_project(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget = request.POST.get('budget')
        category_id = request.POST.get('category')
        deadline = request.POST.get('deadline')
        image = request.FILES.get('image')

        if title and description and category_id:
            category = Category.objects.get(id=category_id)
            ProjectPost.objects.create(
                customer=request.user,
                title=title,
                description=description,
                budget=budget or None,
                category=category,
                deadline=deadline or None,
                image=image or None
            )
            messages.success(request, "✅ Your project has been posted successfully!")
            return redirect('freelance_marketplace:customer_dashboard')
        else:
            messages.error(request, "Please fill all required fields.")

    return render(request, 'post_project.html', {'categories': categories})


def all_gigs(request):
    gigs = Gig.objects.all().order_by('-created_at')
    return render(request, 'freelance_marketplace/gigs.html', {'gigs': gigs})


@login_required
def add_gig(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        category = Category.objects.get(id=category_id) if category_id else None

        Gig.objects.create(
            freelancer=request.user,
            title=title,
            description=description,
            price=price,
            category=category,
            image=image,
            created_by=request.user
        )
        return redirect('freelance_marketplace:freelancer_dashboard')  

    categories = Category.objects.all()
    return render(request, 'freelance_marketplace/add_gig.html', {'categories': categories})


@login_required
def my_gigs(request):
    gigs = Gig.objects.filter(freelancer=request.user)
    return render(request, 'gigs/my_gigs.html', {'gigs': gigs})



def gigs_list(request):
    gigs = Gig.objects.all()
    return render(request, 'gigs.html', {'gigs': gigs})


@login_required
def gig_detail(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    reviews = gig.reviews.all()
    if hasattr(request.user, 'customer'):
        if request.method == 'POST':
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment')
            Review.objects.create(
                gig=gig,
                customer=request.user,
                rating=rating,
                comment=comment
            )
            return redirect('freelance_marketplace:gig_detail', gig_id=gig.id)

    return render(request, 'gig_detail.html', {'gig': gig, 'reviews': reviews})



@login_required
def order_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    if getattr(request.user, 'role', None) != 'customer':
        messages.error(request, "Only customers can place orders.")
        return redirect('freelance_marketplace:home')

    if request.method == 'POST':
        GigOrder.objects.create(gig=gig, customer=request.user)
        messages.success(request, f'Order placed successfully for "{gig.title}"!')
        return redirect('freelance_marketplace:customer_dashboard')

    return render(request, 'freelance_marketplace/order_gig.html', {'gig': gig})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(GigOrder, id=order_id)
    if order.customer != request.user and order.gig.freelancer != request.user:
        messages.error(request, "Access denied.")
        return redirect('freelance_marketplace:home')

    review = Review.objects.filter(order=order).first()

    return render(request, 'freelance_marketplace/order_detail.html', {'order': order, 'review': review})

@login_required
def add_review(request, order_id):
    order = get_object_or_404(GigOrder, id=order_id)
    if order.customer != request.user:
        messages.error(request, "You cannot review this order.")
        return redirect('freelance_marketplace:home')

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review_text', '')
        if order.status != 'Completed':
            messages.error(request, "You can only review completed orders.")
            return redirect('freelance_marketplace:order_detail', order_id=order.id)

        review, created = Review.objects.update_or_create(
            order=order,
            defaults={'rating': rating, 'review_text': review_text}
        )
        messages.success(request, "Your review has been submitted.")
        return redirect('freelance_marketplace:order_detail', order_id=order.id)

    return render(request, 'freelance_marketplace/add_review.html', {'order': order})

@login_required
def freelancer_orders(request):
    gigs = Gig.objects.filter(freelancer=request.user)
    orders = GigOrder.objects.filter(gig__in=gigs)
    return render(request, 'orders/freelancer_orders.html', {'orders': orders})


@login_required
def chat_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    messages_list = ChatMessage.objects.filter(order=order).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('message')
        if content.strip():
            ChatMessage.objects.create(order=order, sender=request.user, message=content)
        return redirect('freelance_marketplace:chat_view', order_id=order.id)
    return render(request, 'freelance_marketplace/chat.html', {'order': order, 'messages': messages_list})



@login_required
def update_order_status(request, order_id, new_status):
    order = get_object_or_404(GigOrder, id=order_id)
    if order.gig.freelancer != request.user:
        messages.error(request, "You don't have permission to change this order.")
        return redirect('freelance_marketplace:freelancer_orders')

    if new_status in ['Accepted', 'Completed']:
        order.status = new_status
        order.save()
        messages.success(request, f"Order for {order.gig.title} marked as {new_status}.")
    else:
        messages.error(request, "Invalid status update.")

    return redirect('freelance_marketplace:freelancer_orders')



@staff_member_required
def admin_delete_order(request, order_id):
    order = get_object_or_404(GigOrder, id=order_id)
    order.delete()
    messages.success(request, f"Order for {order.gig.title} has been deleted.")
    return redirect('freelance_marketplace:admin_orders')


@staff_member_required
def revenue_summary(request):
    total_completed = GigOrder.objects.filter(status='Completed').count()
    total_earnings = GigOrder.objects.filter(status='Completed').aggregate(Sum('id'))['id__sum'] or 0

    top_freelancers = (
        GigOrder.objects.filter(status='Completed')
        .values('gig__freelancer__username')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    context = {
        'total_completed': total_completed,
        'total_earnings': total_earnings,
        'top_freelancers': top_freelancers,
    }
    return render(request, 'orders/revenue_summary.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = request.POST.get('role', 'customer')
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('freelance_marketplace:dashboard_redirect')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'freelance_marketplace/signup.html', {'form': form})


def category_gigs(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    gigs = Gig.objects.filter(category=category)
    return render(request, 'category_gigs.html', {
        'category': category,
        'gigs': gigs
    })


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    gigs = Gig.objects.filter(category=category)
    context = {
        'category': category,
        'gigs': gigs,
    }
    return render(request, 'freelance_marketplace/category_page.html', context)



def create_sample_gigs():
    freelancer_user, _ = User.objects.get_or_create(
        username="default_freelancer",
        defaults={"role": "freelancer", "password": "test1234"}
    )

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
        category = Category.objects.get(slug=slug)
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


class FreelanceMarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'freelance_marketplace'

    def ready(self):
        from .utils import create_sample_gigs
        post_migrate.connect(lambda **kwargs: create_sample_gigs(), sender=self)

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            freelancer=instance.gig.freelancer,
            order=instance,
            message=f"New order for '{instance.gig.title}' by {instance.customer.username}"
        )


@login_required
def chat_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user != order.freelancer and request.user != order.customer:
        return HttpResponse("You are not allowed to view this chat.", status=403)
    messages = order.messages.all() if hasattr(order, 'messages') else []

    context = {
        'order': order,
        'messages': messages,
    }
    return render(request, 'freelance_marketplace/chat.html', context)


@login_required
def edit_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)

    if request.method == "POST":
        gig.title = request.POST.get("title")
        gig.description = request.POST.get("description")
        category_id = request.POST.get("category")
        gig.price = request.POST.get("price")
        image = request.FILES.get("image")

        if category_id:
            gig.category = Category.objects.get(id=category_id)

        if image:
            gig.image = image

        gig.save()
        messages.success(request, "Gig updated successfully!")
        return redirect("freelance_marketplace:freelancer_dashboard")

    categories = Category.objects.all()
    context = {"gig": gig, "categories": categories}
    return render(request, "freelance_marketplace/edit_gig.html", context)



@login_required
def delete_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
    gig.delete()
    messages.success(request, "Gig deleted successfully!")
    return redirect("freelance_marketplace:freelancer_dashboard")


@login_required
def freelancer_gigs(request):
    gigs = Gig.objects.filter(freelancer=request.user)
    return render(request, 'freelance_marketplace/freelancer_gigs.html', {'gigs': gigs})