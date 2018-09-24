# -*- coding: utf-8 -*-
import os
import datetime

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from email_app.models import GetEmail

# Gmail API access
SCOPES = 'https://mail.google.com/'
basedir = os.path.abspath(os.path.dirname(__file__))
credential_json = basedir + '/credentials.json'
token_json = basedir + '/token.json'
store = file.Storage(token_json)
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(credential_json, SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# label_list =  service.users().labels().list(userId='me').execute()

def get_email_content(user_id, email_data_results):
    """ Retrieve the emails"""
    message_list = []
    output_list = []
    # Get max 20 results
    gmail_message_ids = service.users().messages().list(userId=str(user_id), maxResults=20).execute()
    if 'messages' in gmail_message_ids:
        message_list.extend(gmail_message_ids['messages'])
    for message in message_list:
        if message['id'] not in email_data_results:
            result = service.users().messages().get(userId='me', id=message['id']).execute()
            payloads = result['payload']
            headers = payloads['headers']
            for header in headers:
                if header['name'] == 'Subject':
                    email_subject = header['value']
                elif header['name'] == 'From':
                    from_email = header['value']
                elif header['name'] == 'Date':
                    email_date = header['value']
                elif header['name'] == 'To':
                    to_email = header['value']
                else:
                    pass
            # Convert into the datetime format
            email_dt = email_date.split(' ');
            email_date = ' '.join(email_dt[:5])
            email_date = datetime.datetime.strptime(email_date,'%a, %d %b %Y %H:%M:%S')

            output_list.append(GetEmail(message_id=message['id'],
                                        from_address=from_email,
                                        to_address=to_email,
                                        subject=email_subject,
                                        email_date=email_date,
                                        email_content=result['snippet']))
        else:
            print "Message ID already exists"
    if output_list:
        # Bulk Create
        GetEmail.objects.bulk_create(output_list)
    # Get the Emails from DB
    updated_results = GetEmail.objects.all()
    return updated_results

def create_filter(userId, myfilter):
    """ Create a email filter by gmail API """
    print "Create filter is working"
    try:
        r = service.users().settings().filters().create(userId=userId, body=myfilter).execute()
        return r
    except Exception as e:
        return str(e)

def get_matching_threads(userId, labelIds, query):
    """Get all threads from gmail that match the query"""
    print "Get Matching threads working"
    try:
        response = service.users().threads().list(userId=userId, labelIds=labelIds,
                                                  q=query).execute()
        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])

        # Do the response while there is a next page to receive.
        while 'nextPageToken' in response:
            pageToken = response['nextPageToken']
            response = service.users().threads().list(
                userId=userId,
                labelIds=labelIds,
                q=query,
                pageToken=pageToken).execute()
            threads.extend(response['threads'])

        return threads
    except Exception as e:
        return str(e)

def build_search_query(criteria):
    """ Build a gmail query """
    print "Build search query"
    try:
        queryList = []
        positiveStringKeys = ["from", "to", "subject"]
        for k in positiveStringKeys:
            v = criteria.get(k)
            if v is not None:
                queryList.append("(" + k + ":" + v + ")")

        v = criteria.get("query")
        if v is not None:
            queryList.append("(" + v + ")")

        return " AND ".join(queryList)
    except Exception as e:
        return str(e)

def apply_filter_to_matching_threads(userId, filterObject):
    """Apply the filter to matching threads"""
    print "Apply filter"
    try:
        query = build_search_query(filterObject["criteria"])
        threads = get_matching_threads(userId, [], query)
        addLabels = []
        removelabels = []
        try:
            addLabels = filterObject["action"]["addLabelIds"]
            removelabels = filterObject["action"]["removeLabelIds"]
        except Exception as e:
            print str(e)

        print("Adding labels {} to {} threads".format(addLabels, len(threads)))

        for t in threads:
            body = {
                "addLabelIds": addLabels,
                "removeLabelIds": removelabels,
                }
            service.users().threads().modify(userId=userId, id=t["id"],
                                             body=body).execute()
        print "Success"
        return "Successfully updated"
    except Exception as e:
        return str(e)
