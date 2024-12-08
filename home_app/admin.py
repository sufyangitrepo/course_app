from django.contrib import admin
from home_app.models import Course, CourseModule, UserProfile, Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_date', 'amount', 'payment_id', 'user')

# Register your models here.
admin.site.register(Course)
admin.site.register(CourseModule)
admin.site.register(UserProfile)
admin.site.register(Payment, PaymentAdmin)
