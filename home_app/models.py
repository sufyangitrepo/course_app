from datetime import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from video_app.libs.storage import CourseStorage
from ckeditor.fields import RichTextField
# Create your models here.

User = get_user_model()

class UserProfile(models.Model):

    class SubscriptionChoices(models.TextChoices):
        FREE = 'f', 'free'
        MONTHLY = 'm', 'monthly'
        YEARLY = 'y', 'yearly'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_pro = models.BooleanField(default=False)
    pro_expiry_date = models.DateTimeField(null=True, blank=True)
    subscription_type = models.CharField(
        max_length=50,
        choices=SubscriptionChoices.choices,
        default=SubscriptionChoices.FREE
    )

    @property
    def subscription_valid(self):
        if not self.pro_expiry_date:
            return False
        return timezone.now() < self.pro_expiry_date

    class Meta:
        db_table = 'profile_users'

class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'

def _upload_to(instance, filename):
    ext = filename.split('.')[-1]
    created_at = int(round((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000))
    filename = '{}-{}.{}'.format(instance.id, created_at, ext)
    return filename

class Course(models.Model):

    course_name = models.CharField(max_length=30)
    course_description = models.TextField()
    is_premium = models.BooleanField(default=False)
    course_img = models.ImageField(storage=CourseStorage(), upload_to=_upload_to, null=True, blank=True)
    slug = models.SlugField(blank=True)

    class Meta:
        db_table = 'courses'

    def save(self, **kwargs) -> None:
        self.slug = slugify(self.course_name)
        return super().save(**kwargs)

    def __str__(self) -> str:
        return self.course_name

class CourseModule(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    course_module_name = models.CharField(max_length=100)
    module_description = models.TextField()
    can_view = models.BooleanField(default=False)
    video_url = models.URLField(max_length=300)

    def __str__(self) -> str:
        return f'{self.course.course_name}|{self.course_module_name}'

    class Meta:
        db_table = 'course_modules'

