from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from .models import Course, UserProfile, Payment
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()

def login_decorator(view):
    def check_login(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('login')
            return redirect(login_url)

        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            request.session['is_pro'] = profile.is_pro
            request.session['profile'] = profile.id
            request.session['valid'] = profile.subscription_valid

        return view(request, *args, **kwargs)
    return check_login

@login_decorator
def index(request: HttpRequest):
    courses = Course.objects.all()
    return render(request, 'index.html', {'courses': courses})

@login_decorator
def course_detail(request: HttpRequest, slug):
    course = Course.objects.filter(slug=slug).prefetch_related('modules').first()

    if course and course.is_premium:
        profile: UserProfile = UserProfile.objects.filter(id=request.session['profile']).first()
        if not profile.subscription_valid:
            home_url = reverse('index')
            return redirect(home_url)

    return render(request, 'course_detail.html', {'course': course})

@login_decorator
def become_pro(request: HttpRequest):
    if request.method == 'POST':
        membership = request.POST.get('membership', 'monthly')
        course_amount = 1000

        if membership == 'yearly':
            course_amount = 4000

        customer = stripe.Customer.create(
            email=request.user.email,
            source=request.POST['requestToken']
        )
        intent: stripe.PaymentIntent = stripe.PaymentIntent.create(
            customer=customer,
            amount=course_amount * 100,
            currency='PKR',
            description='membership',
            confirm=True,
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never',
            },

        )

        if intent and intent['status'] == 'succeeded':
            profile = UserProfile.objects.filter(user=request.user).first()
            amount = intent['amount_received']
            payment = Payment()
            payment.payment_id = intent['id']
            payment.user = request.user
            if amount == 100000:
                payment.amount = 1000
                profile.is_pro = True
                profile.pro_expiry_date = datetime.now() + timedelta(30)
                profile.subscription_type = UserProfile.SubscriptionChoices.MONTHLY
                profile.save()
                payment.save()
            elif amount == 400000:
                profile.pro_expiry_date = datetime.now() + timedelta(365)
                profile.is_pro = True
                profile.subscription_type = UserProfile.SubscriptionChoices.YEARLY
                payment.amount = 4000
                profile.save()
                payment.save()
            charge_url = reverse('charge')
            return redirect(charge_url)

    return render(request, 'become_pro.html', {'publishable_key': settings.STRIPE_PUBLISH_KEY})

@login_decorator
def charge(request: HttpRequest):
    return render(request, 'charge.html', {})

def login_user(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        db_user = User.objects.filter(username=username).first()
        if not db_user:
            context = {'message': 'user does not exist'}
            return render(request, 'login.html', context)
        else:
            user = authenticate(username=username, password=password)
            if not user:
                context = {'message': 'password or email is not correct'}
                return render(request, 'login.html', context)
            login(request, user)
            home_url = reverse('index')
            return redirect(home_url)

    return render(request, 'login.html', {})

def register(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        db_user = User.objects.filter(username=username).first()
        if db_user:
            context = {'message': 'user already exist'}
            return render(request, 'register.html', context)
        new_user = User.objects.create(email=email, username=username)
        new_user.set_password(password)
        new_user.save()
        UserProfile.objects.create(user=new_user)
        login_url = reverse('login')
        return redirect(login_url)

    return render(request, 'register.html', {})

def logout_user(request: HttpRequest):
    logout(request)
    login_url = reverse('login')
    return redirect(login_url)
