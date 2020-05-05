from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import pandas as pd 
import numpy as np 
from datetime import timedelta
import os 
import pickle 

def get_list_of_events():
    creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', ['https://www.googleapis.com/auth/calendar.events.readonly'])
            creds = flow.run_local_server(port=0)


    #Build the service
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API and retrieve info 
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
    	calendarId='primary', 
    	timeMax=now, timeMin='2019-01-01T00:00:00Z',
    	maxResults=2500, singleEvents=True,
    	orderBy='startTime').execute()

    #Get the info we need from the events 
    events = events_result.get('items', [])
    output = [['status','start','end']]

    if not events:
        print('No events found.')
        return 0

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['start'].get('date'))
        status = event['status']
        output.append([status,start,end])


    #Create a DF with the data retrieved 
    events = pd.DataFrame(data=output[1:],columns=output[0])
    #Exclude non confirmed events 
    events = events[events['status']=='confirmed']
    #Modify dates to remove Z info and convert them to datetime
    events['start'] = events['start'].str.replace('\+.*','',regex=True)
    events['start'] = pd.to_datetime(events['start'],format='%Y-%m-%dT%H:%M:%S')
    events['end'] = events['end'].str.replace('\+.*','',regex=True)
    events['end'] = pd.to_datetime(events['end'],format='%Y-%m-%dT%H:%M:%S')
    #Calculate event duration in minutes 
    events['delta'] = (events['end'] - events['start'])
    events['delta'] = events['delta'].astype('timedelta64[m]')

    #Get the number of months between the first and the last event 
    events_days_size = (events['start'].min()) - (events['end'].max())
    events_days_size = np.absolute(events_days_size.days)
    events_days_size = events_days_size / 30

    #Calculate the average time spent per month oin meetimgs 
    result = int(events['delta'].sum())/events_days_size

    return result