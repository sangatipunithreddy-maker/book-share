from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

@receiver(post_migrate)
def seed_users(sender, **kwargs):
    if User.objects.count() == 0:
        demo = [
            ('Riya Student','student@bookshare.edu','student123','student'),
            ('Arun Faculty','faculty@bookshare.edu','faculty123','faculty'),
            ('Kavya Admin','admin@bookshare.edu','admin123','admin'),
        ]
        for name,email,pwd,role in demo:
            first,last = (name.split(' ',1)+[''])[:2]
            User.objects.create(
                username=email,
                email=email,
                first_name=first,
                last_name=last,
                password=make_password(pwd),
                role=role
            )


from .models import Ad, Material, InterviewPost, Notification
@receiver(post_migrate)
def seed_content(sender, **kwargs):
    User = get_user_model()
    try:
        stu = User.objects.get(email='student@bookshare.edu')
        fac = User.objects.get(email='faculty@bookshare.edu')
        # Ads
        if Ad.objects.count()==0:
            Ad.objects.create(title='DBMS by Korth', description='Slightly used.', price=350, seller=stu)
            Ad.objects.create(title='Operating Systems', description='Clean copy.', price=400, seller=stu)
        # Materials
        if Material.objects.count()==0:
            Material.objects.create(subject='OS Midterm Notes', filename='os_midterm.pdf', uploaded_by=fac, verified=False)
        # Blog
        if InterviewPost.objects.count()==0:
            InterviewPost.objects.create(title='Google Internship — Round Tips', content='Be strong with DS & Algo', author=stu)
        # Notifs
        if Notification.objects.count()==0:
            Notification.objects.create(user=stu, content='Your ad #1 is now live!', read=False)
    except Exception:
        pass
