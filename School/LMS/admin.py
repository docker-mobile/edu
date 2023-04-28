from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import *

# change user model admin area
admin.site.unregister(Group)
admin.site.unregister(User)
# inline for Profile
class ProfileInline(admin.TabularInline):
    model = Profile
    fields = ['role']
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]

# register all models
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Score)
admin.site.register(Homework)
admin.site.register(Exam)
admin.site.register(ExamScore)
admin.site.register(Notification)
admin.site.register(PrivateTicket)
admin.site.register(SupportTicket)
admin.site.register(SampleExam)
admin.site.register(Festival)
admin.site.register(Request)
admin.site.register(New)
admin.site.register(GalleryImage)