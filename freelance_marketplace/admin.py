from django.contrib import admin
from .models import CustomUser, Category, Gig, ProjectPost, Offer,Order, GigOrder, Review, Freelancer, Customer
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomAdmin

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + ((None, {'fields': ('role',)}),)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'gig', 'customer', 'freelancer', 'is_pending', 'is_completed', 'created_at')
    list_filter = ('is_pending', 'is_completed', 'created_at')
    search_fields = ('gig__title', 'customer__username', 'freelancer__username')


admin.site.register(Category)
admin.site.register(Gig)
admin.site.register(ProjectPost)
admin.site.register(Offer)
admin.site.register(GigOrder)
admin.site.register(Review)
admin.site.register(Freelancer)
admin.site.register(Customer)
admin.site.register(CustomAdmin)