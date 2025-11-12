from django.contrib import admin
from .models import User, Ad, Material, Notification, InterviewPost, ReportedAd

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','email','role','year','branch','is_active')
    search_fields = ('email','username')
    list_filter = ('role','is_active')

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id','title','price','status','seller','created_at')
    list_filter = ('status',)
    search_fields = ('title','description')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id','subject','filename','verified','uploaded_by','created_at')
    list_filter = ('verified',)
    search_fields = ('subject','filename')

@admin.register(InterviewPost)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('id','title','author','created_at')

@admin.register(Notification)
class NotifAdmin(admin.ModelAdmin):
    list_display = ('id','user','content','read','created_at')
    list_filter = ('read',)

@admin.register(ReportedAd)
class ReportedAdmin(admin.ModelAdmin):
    list_display = ('id','ad','reporter','reason','resolved','created_at')
    list_filter = ('resolved',)
