from django.shortcuts import render, redirect
from LMS.models import Profile, Notification, New, GalleryImage

# Views are here
def home(request):
    context = {
        "title": 'خانه',
        "subtitle": "به مدرسه شهید طهماسبی خوش آمدید",
        "first_news": New.objects.all().order_by('-id')[:5],
        "second_news": New.objects.all().order_by('-id')[5:10],
        "gallery": GalleryImage.objects.all(),
    }
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            notifications = []
            for notification_public in Notification.objects.filter(to='همه کاربران'):
                notifications.append(notification_public)
            if Profile.objects.filter(user=request.user)[0].role == "Student":
                for notif in Notification.objects.filter(to='همه دانش آموزان'):
                    notifications.append(notif)
            else:
                for notif in Notification.objects.filter(to='همه معلمان'):
                    notifications.append(notif)
            context['notifications'] = notifications
    
    return render(request, 'home.html', context)

def about_us(request):
    context = {
        'title': 'درباره ما',
    }
    return render(request, 'about-us.html', context)
def contact_us(request):
    context = {
        'title': 'تماس با ما',
    }
    return render(request, 'contact-us.html', context)

def news(request):
    context = {
        'title': 'اخبار مدرسه',
        'news': New.objects.all().order_by('-id'),
        'famous_news': New.objects.all().order_by('-id')[:5]
    }
    return render(request, 'news.html', context)
def new_view(request, slug):
    new = New.objects.filter(slug=slug)[0]
    context = {
        'title': f"{new.title}",
        'new': new,
    }
    return render(request, 'new.html', context)