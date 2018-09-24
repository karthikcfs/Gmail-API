# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Audit(models.Model):
    """ Create the common fields for the applications """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At", null=True, blank=True)

    class Meta:
        abstract = True