# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.

class BaseAuditAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'modified_at',)
    save_on_top = True

class AuditAdmin(BaseAuditAdmin, admin.ModelAdmin):
    pass