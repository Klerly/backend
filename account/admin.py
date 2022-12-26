from django.contrib import admin

from django.contrib import admin
from account.models import EmailTokenVerificationModel, ResetPasswordVerificationModel

# Register your models here.
admin.site.register(EmailTokenVerificationModel)
admin.site.register(ResetPasswordVerificationModel)
