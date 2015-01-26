import gdata.calendar.data
import gdata.calendar.client
import atom


class GoogleCalendar:
    def __init__(self, G_EMAIL, G_PASSWORD):
        """Creates a CalendarService and provides ClientLogin auth details to it.
        The G_EMAIL and G_PASSWORD are required arguments for ClientLogin.  The
        CalendarService automatically sets the service to be 'cl', as is
        appropriate for calendar.  The 'source' defined below is an arbitrary
        string, but should be used to reference your name or the name of your
        organization, the app name and version, with '-' between each of the three
        values.  The account_type is specified to authenticate either
        Google Accounts or Google Apps accounts.  See gdata.service or
        http://code.google.com/apis/accounts/AuthForInstalledApps.html for more
        info on ClientLogin.  NOTE: ClientLogin should only be used for installed
        applications and not for multi-user web applications."""
        self.cal_client = gdata.calendar.client.CalendarClient(source='Roger Liu')
        self.cal_client.ClientLogin(G_EMAIL, G_PASSWORD, self.cal_client.source);

    def _InsertQuickAddEvent(self, content="Tennis with John today 3pm-3:30pm"):
        """
        Creates an event with the quick_add property set to true so the content
        is processed as quick add content instead of as an event description.
        http://support.google.com/calendar/bin/answer.py?hl=en&answer=36604
        """
        event = gdata.calendar.data.CalendarEventEntry()
        event.content = atom.data.Content(text=content)
        event.quick_add = gdata.calendar.data.QuickAddProperty(value='true')
        new_event = self.cal_client.InsertEvent(event)
        return new_event


def AddEvent(G_EMAIL, G_PASSWORD, event):
    """
    Creates an event with the quick_add property set to true so the content
    is processed as quick add content instead of as an event description.
    http://support.google.com/calendar/bin/answer.py?hl=en&answer=36604
    """
    gcalendar = GoogleCalendar(G_EMAIL, G_PASSWORD)
    gcalendar._InsertQuickAddEvent(event)


addevent = AddEvent