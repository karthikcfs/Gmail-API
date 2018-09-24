# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import ast

from django.shortcuts import render
from django.template.context_processors import csrf
from django.http import HttpResponse

from .models import Rules, GetEmail
from email_util.views import get_email_content, create_filter, apply_filter_to_matching_threads

def email_dict_data(email_results):
    """ Create email dict to store into DB"""

    email_dict = {}
    email_result_list = []
    for result in email_results:
        email_dict = {'message_id': result.message_id,
                      'date': result.email_date,
                      'from': result.from_address,
                      'to': result.to_address,
                      'subject': result.subject,
                      'email_content': result.email_content
                      }
        email_result_list.append(email_dict)
    return email_result_list

def email_report(request):
    """ Email log report """

    c={}
    c.update(csrf(request))
    emails = GetEmail.objects.all()
    email_data_results = email_dict_data(emails)
    if request.GET.get('fetch_email'):
        results = get_email_content('me', email_data_results)
        email_fetch_results = email_dict_data(results)
        return render(request, 'email_report.html', {'email_data_results': email_fetch_results})
    return render(request, 'email_report.html', {'email_data_results': email_data_results})

def rules_action(request,action):
    """ Rules actions - Create, List, Update, Delete"""
    c={}
    c.update(csrf(request))
    rule_crud = GmailRuleActions()

    # Delete Rule
    if action == 'delete':
        delete_rule_id = request.POST.get('rule_id')
        rule_crud = GmailRuleActions(delete_rule_id)
        delete_rule_result = rule_crud.delete_rule()
        return HttpResponse(json.dumps({'response_data': delete_rule_result}),
                            content_type="application/json")
    # Create Rule
    elif action == 'create':
        if request.POST.get('filter_action_create'):
            rule_description = request.POST.get('rule_description')
            overall_condition = request.POST.get('overall_condition')
            gmail_rules_json = request.POST.get('gmail_rules_json')
            gmail_action_json = request.POST.get('gmail_action_json')
            gmail_rules_json = ast.literal_eval(gmail_rules_json)
            gmail_action_json = ast.literal_eval(gmail_action_json)
            # Create Rule
            rule_creation = rule_crud.create_rule(rule_description, overall_condition,
                                                  gmail_rules_json, gmail_action_json)
            create_rule_result = rule_creation

            # Filter action format in Gmail API
            print "my_filters"
            my_filters = [{ "criteria":{},"action":{}},]
            my_filters[0]['criteria'] = gmail_rules_json
            my_filters[0]['action'] = gmail_action_json
            print my_filters
            # Gmail roles based actions
            for my_filter in my_filters:
                filter_create_response = create_filter("me", my_filter)
                print "filter_create_response"
                print filter_create_response
                filter_apply_response = apply_filter_to_matching_threads("me", my_filter)
                print "filter_apply_response"
                print filter_apply_response
                create_rule_result.create_filter_response = filter_create_response
                create_rule_result.apply_filter_response = filter_apply_response
                create_rule_result.save()
            return HttpResponse(json.dumps({'response_data': "Success"}),
                                content_type="application/json")
        return render(request, 'email_rules_actions.html', {})
    # Update the action
    elif action == 'update':
        pass

    # View the all rules
    elif action == 'list':
        list_rule_rows = rule_crud.list_rule()
        list_rule_results = list_rule_rows
        return render(request, 'list_gmail_rules.html', {'list_rule_results': list_rule_results})
    else:
        return render(request, '404.html', {})

class GmailRuleActions:
    def __init__(self, gmail_role_id='NA'):
        self.gmail_role_id = gmail_role_id

    def create_rule(self, rule_description, overall_condition,
                    gmail_rules_json, gmail_action_json):
        try:
            gmail_new_rule = Rules.objects.create(rule_name=rule_description,
                                                  rule_condition=overall_condition,
                                                  rule_criteria=gmail_rules_json,
                                                  rule_action=gmail_action_json)
            return gmail_new_rule
        except Exception as e:
            return "Create operation issue " + str(e)

    def delete_rule(self):
        try:
            delete_rule_data = Rules.objects.get(id=self.gmail_role_id)
            if delete_rule_data:
                delete_rule_name = delete_rule_data.rule_name
                delete_rule_data.delete()
                return str(delete_rule_name) + ' rule successfully deleted'
            else:
                return "Specifiled rule is not available in our system"
        except Exception as e:
            return "Delete operation issue " +str(e)

    def list_rule(self):
        try:
            get_rule_list = []
            rules_data = Rules.objects.all()
            for rule in rules_data:
                created_rule_data = {'rule_id': rule.id,
                                     'rule_name': rule.rule_name,
                                     'rule_condition': rule.rule_condition,
                                     'rule_criteria': rule.rule_criteria,
                                     'rule_action': rule.rule_action}
                get_rule_list.append(created_rule_data)
            return get_rule_list
        except Exception as e:
            return "List operation issue " +str(e)