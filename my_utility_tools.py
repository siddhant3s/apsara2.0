#Required libs
import os 
from langchain.tools import tool
import psutil as ps 
import subprocess 
import datetime 
from datetime import timedelta

import pytz
import re

#Gmail tool libs 
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials)
from google.oauth2.credentials import Credentials
from langchain_community.tools.gmail.send_message import GmailSendMessage
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain_community.tools.gmail.get_message import GmailGetMessage
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.get_thread import GmailGetThread



#Get the gmail required credential 
def get_gmail_credential(service_name='gmail', service_version='v1'):
    #Read this to create your own credentials: https://developers.google.com/gmail/api/quickstart/python        
    credentials = get_gmail_credentials(
        token_file='token.json', 
        scopes=["https://mail.google.com/", "https://www.googleapis.com/auth/calendar"],
        client_secrets_file="../credentials.json",
    )

    api_resource = build_resource_service(service_name=service_name, service_version= service_version, credentials=credentials)
    
    return api_resource
    # return gmail_tool_kit.get_tools()

#Gmail tools  - Completed 
send_mail = GmailSendMessage(api_resource=get_gmail_credential())
create_draft = GmailCreateDraft(api_resource=get_gmail_credential())
get_message = GmailGetMessage(api_resource=get_gmail_credential())
search_google = GmailSearch(api_resource=get_gmail_credential())
get_thread = GmailGetThread(api_resource=get_gmail_credential())


#Set calendar meeting 
@tool
def get_date(text: str ) -> datetime.date:
    '''
    Useful to to get date for setting calendar meeting/events. 
    text: str: query of the user from which date will be extracted. 
    Use this tool first to get the calendar meeting then use the output of the tool as an input parameter of `date` to create_event tool. 
    returns datetime.date 
    '''
    MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    DAY_EXTENTIONS= ["nd", "rd", "th", "st"]
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    if text.count("tomorrow") > 0:
        return today + timedelta(1)
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # THE NEW PART STARTS HERE
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  
        return datetime.date(month=month, day=day, year=year)

#get upcoming events tool
@tool
def get_events(day:str="today") -> list[dict]:
    '''
    useful when to check upcoming google calendar events or meetings. 
    day: get date from user query. e.g: 'today', 'tomorrow'. Default is today
    '''
    service = get_gmail_credential(service_name='calendar', service_version='v3')
    day = get_date(day)
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    ist = pytz.timezone("Asia/Kolkata")
    date = date.astimezone(ist)
    end_date = end_date.astimezone(ist)
    event_result = service.events().list(calendarId = 'primary', timeMin=date.isoformat(),timeMax = end_date.isoformat(),singleEvents = True, orderBy='startTime').execute()# maxResults = n, 
    events = event_result.get('items', [])
    if not events:
        return 'No upcoming events found'
    else:
        print(f'You have {len(events)} events on this day.')        
        get_events = []
        for event in events:
            get_events.append(event)
        return get_events

#Create event/Meeting tool
@tool 
def create_event(day: datetime.date, mail: list = [], summary: str = '', meeting_time: str = '') -> str:
    """
    Useful when creating Google Calendar events or meetings.
    day: datetime.date: The date of the event. [Get the date from user query] 
    mail: List of emails to whom you want to invite.
    summary: Short description of the event.
    meeting_time: Time of the event to be held (format: "HH:MM AM/PM").
    """

    try:
        # Parsing the meeting time from the input string if not provided
        match = re.search(r'at (\d{1,2}:\d{2} [ap]m)', meeting_time)
        if match:
            meeting_time = datetime.strptime(match.group(1), '%I:%M %p').strftime('%H:%M')
        print(meeting_time)
        meeting_time = meeting_time.replace('AM', '').replace('PM', '').replace('am', '').replace('pm', '').strip()

        # Parsing time and setting start and end times
        start_time = datetime.datetime.combine(day, datetime.datetime.strptime(meeting_time, '%H:%M').time())
        end_time = start_time + timedelta(minutes=59)

        # Setting timezone
        timezone = 'Asia/Kolkata'

        # Creating event object
        event = {
            'summary': summary,
            'location': 'Delhi',
            'description': summary,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': timezone,
            },
            'attendees': [{'email': mail}],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # Inserting event into calendar
        service = get_gmail_credential(service_name='calendar', service_version='v3')
        event = service.events().insert(calendarId='shubharthaksangharsha@gmail.com', sendUpdates='all',
                                          body=event).execute()
        return f'Event has been created: {event.get("htmlLink")}'

    except Exception as e:
        return f'Unable to create the event: {e}'


#function to get bluetooth devices list 
def bluetooth_list() -> list:
    '''
    useful when to find the available devices list of bluetooth devices
    use this tool to find the mac address of bluetooth device before connecting to bluetooth device
    returns: list
    '''
    output = subprocess.check_output("bluetoothctl devices", shell=True, universal_newlines=True)
    output = str(output).strip('\n')
    lines = output.split('\n')
    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            mac_address = parts[1]
            device_name = ' '.join(parts[2:])
            devices.append({device_name: mac_address})
    return devices

#Bluetooth available devices tool
@tool
def bluetooth_available_devices() -> list:
    '''
    useful when to find the available devices list of bluetooth devices
    use this tool to find the mac address of bluetooth device before connecting to bluetooth device
    returns: list
    '''
    output = subprocess.check_output("bluetoothctl devices", shell=True, universal_newlines=True)
    output = str(output).strip('\n')
    lines = output.split('\n')
    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            mac_address = parts[1]
            device_name = ' '.join(parts[2:])
            devices.append({device_name: mac_address})
    return devices

#Power off blueooth 
@tool 
def turn_off_bluetooth()-> str:
    '''
    useful when to turn off bluetooth
    returns: str
    '''
    power = subprocess.check_output(
        "bluetoothctl power off", shell = True, universal_newlines=True
    )
    print(power)
    return power

#Power on blueooth 
@tool
def turn_on_bluetooth()-> str:
    """
    useful when to turn on bluetooth
    returns: str
    """
    power = subprocess.check_output(
        "bluetoothctl power on", shell = True, universal_newlines=True
    )
    print(power)
    return power

#disconnect to bluetooth device
@tool 
def disconnect_bluetooth_device(disconnect='disconnect')-> str:
    '''
    useful when to disconnect to bluetooth device
    disconnect: str = disconnect
    returns: str
    '''
    disconnect = subprocess.check_output(
        "bluetoothctl disconnect", shell = True, universal_newlines=True
    )
    print(disconnect)
    return disconnect

# connect to bluetooth device
@tool
def connect_bluetooth_device() -> str:
    """
    useful when to connect to bluetooth device
    returns: str
    """
    name, mac = bluetooth_list()[0].popitem()
    print(name, mac)
    connected = subprocess.check_output(
        "bluetoothctl connect " + mac, shell = True, universal_newlines=True
    )
    print(connected)
    return 'Successfully connected to ' + name 

#check battery of laptop 
@tool
def check_battery(battery_string: str = "battery") -> str:
    '''
    useful when you need to find the current battery percentage and whether laptop battery is charging or not.
    battery_string: str = "battery", default value is "battery". it just for safety purpose so that it won't run into any errors.
    the tool will return the battery percentage and whether laptop is charging or not.
    returns: str
    '''
    try:
        percent = int(ps.sensors_battery().percent)
        charging = ps.sensors_battery().power_plugged
        if charging:
            return f"Laptop is {percent}% charged and currently charging"
        else:
            return f"Laptop is {percent}% charged and currently not charging"
    except Exception as e:
        print(e)
        return "Something went wrong while checking the battery"
    
    return check_battery(input_args={})

#Shutdown laptop tool
@tool
def shutdown_laptop() -> str: 
    '''
    useful when you user ask to power off or shutdown the laptop 
    '''
    try:
        os.system(f"shutdown")
        return f"Laptop will shutdown in 1 minute"
    except Exception as e:
        print(e)
        return "Something went wrong while shutting down the laptop"
    

#Restart laptop tool
@tool 
def restart_laptop() -> str: 
    '''
    useful when you user ask to restart the laptop 
    '''
    try:
        os.system(f"reboot")
    except Exception as e:
        print(e)
        return "Something went wrong while rebooting down the laptop"
    return f"Laptop will reboot in 1 minute"

#Increase volume tool
@tool
def increase_volume(volume_change: int = 10000) -> str:
    '''
    useful when you user ask to increase the volume of laptop 
    volume_change: int = 10000, default value is 10000
    volume_change = 1000 means 1% of volume will be increased
    volume_change = 2000 means 2% of volume will be increased
    if you want to increase the volume by 5% then volume_change = 5000
    returns: str
    #Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ +{volume_change}')
        return f"Successfully increased volume by {volume_change}"
    except Exception as e:
        print(e)
        return "Something went wrong while increasing the volume"

#Decrease volume tool    
@tool
def decrease_volume(volume_change: int = 10000) -> str:
    '''
    useful when you user ask to decrease the volume of laptop 
    volume_change: int = 10000, default value is 10000 
    volume_change = 1000 means 1% of volume will be decreased
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ -{volume_change}')
        return f"Successfully decreased volume by {volume_change}"
    except Exception as e:
        print(e)
        return "Something went wrong while decreasing the volume"

#Mute volume tool
@tool  
def mute_volume(muting_volume: str = "mute") -> str:
    '''
    useful when you user ask to mute the volume of laptop 
    muting_volume: str = mute. default value is "mute". it just for safety purpose so that it won't run into any errors.
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-mute @DEFAULT_SINK@ toggle')
        return f"Successfully muted the volume."
    except Exception as e:
        print(e)
        return "Something went wrong while muting the volume"
    
#Unmute volume tool    
@tool  
def umute_volume(unmuting_volume: str = "unmute") -> str:
    '''
    useful when you user ask to unmute the volume of laptop 
    unmuting_volume: str = unmute. default value is "unmute". it just for safety purpose so that it won't run into any errors.
    returns: str
    Return the final answer if found successfully in output
    '''
    try:
        os.system(f'pactl set-sink-mute @DEFAULT_SINK@ toggle')
        return f"Successfully unmuted the volume."
    except Exception as e:
        print(e)
        return "Something went wrong while unmuting the volume"

if __name__ == '__main__':
    pass