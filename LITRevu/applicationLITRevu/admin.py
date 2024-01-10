from django.contrib import admin
from .models import CustomUser, Ticket, Review, UserFollows, UserBlock


# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'time_created']
    search_fields = ['title', 'user__username']
    list_filter = ['time_created']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'rating', 'user', 'headline', 'time_created']
    search_fields = ['headline', 'user__username', 'ticket__title']
    list_filter = ['rating', 'time_created']


@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ['user', 'followed_user']
    search_fields = ['user__username', 'followed_user__username']


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    search_fields = ['blocker__username', 'blocked__username']
