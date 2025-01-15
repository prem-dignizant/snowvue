from django.contrib import admin

from user.models import (
    EmailVerificationToken,
    User,
    UserProfile,
    MobileVerificationToken
)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "email",
        'mobile_number',
        "user_name",
        "is_active",
        "is_staff",
        "is_superuser",
        'mfa_enabled'
    )

class UserHealthProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "height",
        "weight",
        "weight_type",
        "waist",
        "waist_choices",
    )


admin.site.register(User, UserAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(UserProfile)
admin.site.register(MobileVerificationToken)