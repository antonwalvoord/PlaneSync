from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

calendarId = "c_9b8b46149298c87aa84286fe32d75401e47c2ebea0f285dd6dc455fc2a2ddf86@group.calendar.google.com"


# Build the calendar
def build_service(token):
    # SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = Credentials(token)

    try:
        service = build("calendar", "v3", credentials=creds)

    except HttpError as error:
        print(f"An error occurred: {error}")

    else:
        return service


def get_event(service, eventId):
    try:
        event = service.events().get(
            calendarId=calendarId,
            eventId=eventId,
        ).execute()
    except Exception:
        return Exception
    else:
        return event


def determine_color(hook):
    # Need to check if the activity is update to module
    activity = hook["activity"]["field"]
    if activity == "modules":
        module = hook["activity"]["new_value"]

        match module:
            case "Accumulator":
                return "1"
            case "Aerodynamics":
                return "2"
            case "Full Car Schedule":
                return "3"
            case "Data Acquisition":
                return "4"
            case "Chassis":
                return "5"
            case "High Voltage Electronics":
                return "6"
            case "Low Voltage Electronics":
                return "7"
            case "Suspension":
                return "8"
    return None


def confirm_deletion(hook):
    new_module = hook["activity"]["new_value"]
    old_module = hook["activity"]["old_value"]

    if new_module == old_module:
        return True
    else:
        return False


def create_event(hook):
    due_date = hook["data"]["target_date"]
    eventId = hook["data"]["id"].replace("-", "")
    color = determine_color(hook)

    # We can only create an event if it has a due date
    if due_date:
        event = {
            'summary': hook["data"]["name"],
            'description': hook["data"]["description_html"],
            'id': eventId,
            'colorId': color,
            'start': {
                'date': due_date,
            },
            'end': {
                'date': due_date,
            },
        }
        return event
    else:
        print("No due date found, cannot create event")


def update_event(hook, event):
    color = determine_color(hook)

    # Gather updated information
    try:
        due_date = hook["data"]["target_date"]
        title = hook["data"]["name"]
        information = hook["data"]["description_html"]

    # There may only be an id if this is an update
    # due to a deletion
    except Exception:
        if color is not None:
            event['colorId'] = color
        return event

    else:
        # Update the event accordingly
        event['summary'] = title
        event['description'] = information
        if color is not None:
            event['colorId'] = color
        event['start'] = {
            'date': due_date,
        }
        event['end'] = {
            'date': due_date,
        }

        return event


# Confirm we have a valid event and return
# what action was taken to it
def determine_event_type(hook):
    event_type = hook["event"]
    action_type = hook["action"]

    # We only care if we have an "issue" event
    # based on webhook config, this should always
    # be the case
    if event_type != "issue":
        return False

    # If we have an "issue" we want to return
    # what action was taken to the issue
    return action_type


# Create a calendar event based on a new
# issue on Plane
def create_issue(service, hook):
    print("Creating issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # Sometimes Plane sends a create issue when it should
    # send update instead, check for this case
    event = get_event(service, issueId)
    if event == Exception:
        print("No event found, creating new")
        # Attempt to create a new event object
        new_event = create_event(hook)
        if new_event:
            try:
                event = (
                    service.events()
                    .insert(
                        calendarId=calendarId,
                        body=new_event
                    ).execute()
                )
            except Exception as e:
                print("Event creation failed, id likely already exists")
                print(f"Exception details: {e}")
            else:
                print(f"Event created: {event.get('htmlLink')}")
        else:
            print("Malformed request, cancelled creation")
    else:
        print("Only a module update, updating instead")
        # An event was found so we need to update instead
        update_issue(service, hook)


# Delete a calendar event based on changes
# within Plane
def delete_issue(service, hook):
    print("Deleting issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # First check actually exists on calendar
    event = get_event(service, issueId)
    if event == Exception:
        print("Issue already has no calendar event")
        return
    # If it exists and isn't cancelled, try to delete
    if event["status"] != "cancelled":
        # First confirm it's an actual deletion and
        # not just an update to the module
        real_deletion = confirm_deletion(hook)
        if real_deletion:
            service.events().delete(
                calendarId=calendarId,
                eventId=issueId,
            ).execute()
            print("Issue deleted")
        else:
            print("Only a module update, update instead of delete")
            update_issue(service, hook)
    else:
        print("Event already cancelled")


# Update a calendar event based on changes
# to the issue on Plane
def update_issue(service, hook):
    print("Updating issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # First check actually exists on calendar
    event = get_event(service, issueId)
    # if it doesn't, call create issue instead
    if event == Exception:
        print("Issue has no calendar event, creating new event")
        create_issue(hook)
        return
    # if it does, confirm it isn't cancelled and then update it
    if event["status"] != "cancelled":
        event = update_event(hook, event)
        service.events().update(
            calendarId=calendarId,
            eventId=issueId,
            body=event
        ).execute()
    else:
        print("Event already cancelled")


# Handle webhook json when recieved
def handle_webhook(service, hook):
    action = determine_event_type(hook)
    if action:
        match action:
            case "created":
                create_issue(service, hook)
            case "updated":
                update_issue(service, hook)
            case "deleted":
                delete_issue(service, hook)


def handler(pd: "pipedream"):
    hook = pd.steps["trigger"]["event"]
    token = f'{pd.inputs["google_calendar"]["$auth"]["oauth_access_token"]}'
    service = build_service(token)
    handle_webhook(service, hook)
