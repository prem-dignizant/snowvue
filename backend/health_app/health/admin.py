from django.contrib import admin

# Register your models here.
from health.models import (
    UserHealthProfile,
    Contract,
    ContractRecipient,
    
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

admin.site.register(UserHealthProfile,UserHealthProfileAdmin)

class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_id","seller","created_at",)

admin.site.register(Contract,ContractAdmin)

class ContractRecipientAdmin(admin.ModelAdmin):
    list_display = ("contract_recipient_id","created_at","buyer","price")

admin.site.register(ContractRecipient,ContractRecipientAdmin)