from django.contrib.auth.admin import UserAdmin
from account.models import User
from django.contrib import admin
from account.models import EmailTokenVerificationModel, ResetPasswordTokenVerificationModel

# Register your models here.
admin.site.register(EmailTokenVerificationModel)
admin.site.register(ResetPasswordTokenVerificationModel)
admin.site.register(User, UserAdmin)
