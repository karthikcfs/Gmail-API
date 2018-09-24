# -*- coding: utf-8 -*-
from django.contrib import admin
from email_util.admin import AuditAdmin
from email_app.models import Rules, GetEmail

# Register your models here.
class RulesAdmin(AuditAdmin):
    list_display = ('rule_name', 'rule_condition', 'rule_criteria', 'rule_action') + AuditAdmin.list_display

class GetEmailAdmin(AuditAdmin):
    list_display = ('from_address', 'to_address', 'subject') + AuditAdmin.list_display

admin.site.register(Rules, RulesAdmin)
admin.site.register(GetEmail, GetEmailAdmin)
