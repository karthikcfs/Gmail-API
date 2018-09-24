# -*- coding: utf-8 -*-
from django.db import models
from email_util.models import Audit
from email_util.constants import CONDITION_CHOICES

# Create your models here.

class Rules(Audit):
    """ Store the rules details """

    rule_name = models.CharField(max_length=50)
    rule_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    rule_criteria = models.TextField(blank=True, null=True, verbose_name='Criteria')
    rule_action = models.TextField(blank=True, null=True, verbose_name='Action')
    create_filter_response = models.TextField(blank=True, null=True)
    apply_filter_response = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.rule_name

class GetEmail(Audit):
    """ Store the email details """

    message_id = models.CharField(max_length=50, null=True, blank=True)
    from_address = models.CharField(max_length=255, verbose_name='From')
    to_address = models.CharField(max_length=255, verbose_name='To')
    subject = models.CharField(max_length=255, null=True, blank=True)
    email_date = models.DateTimeField(blank=True, null=True)
    email_content = models.TextField(verbose_name='Body')

    def __unicode__(self):
        return "%s[%s]" % (self.from_address, self.subject)
