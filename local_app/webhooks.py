import json
import calendar_api
import events


# Parse webhook input and return Json information
def parse_webhook(input):
    json_object = input[input.find("{"):]
    json_dict: dict = json.loads(json_object)
    return json_dict


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
def create_issue(hook):
    print("Creating issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # Sometimes Plane sends a create issue when it should
    # send update instead, check for this case
    event = calendar_api.get_event(issueId)
    if event == Exception:
        print("No event found, creating new")
        # Attempt to create a new event object
        new_event = events.create_event(hook)
        if new_event:
            try:
                event = (
                    calendar_api.service.events()
                    .insert(
                        calendarId=calendar_api.calendarId,
                        body=new_event
                    ).execute()
                )
            except Exception:
                print("Event creation failed, id likely already exists")
            else:
                print(f"Event created: {event.get('htmlLink')}")
        else:
            print("Malformed request, cancelled creation")
    else:
        print("Only a module update, updating instead")
        # An event was found so we need to update instead
        update_issue(hook)


# Delete a calendar event based on changes
# within Plane
def delete_issue(hook):
    print("Deleting issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # First check actually exists on calendar
    event = calendar_api.get_event(issueId)
    if event == Exception:
        print("Issue already has no calendar event")
        return
    # If it exists and isn't cancelled, try to delete
    if event["status"] != "cancelled":
        # First confirm it's an actual deletion and
        # not just an update to the module
        real_deletion = events.confirm_deletion(hook)
        if real_deletion:
            calendar_api.service.events().delete(
                calendarId=calendar_api.calendarId,
                eventId=issueId,
            ).execute()
            print("Issue deleted")
        else:
            print("Only a module update, update instead of delete")
            update_issue(hook)
    else:
        print("Event already cancelled")


# Update a calendar event based on changes
# to the issue on Plane
def update_issue(hook):
    print("Updating issue...")
    issueId = hook["data"]["id"].replace("-", "")
    # First check actually exists on calendar
    event = calendar_api.get_event(issueId)
    # if it doesn't, call create issue instead
    if event == Exception:
        print("Issue has no calendar event, creating new event")
        create_issue(hook)
        return
    # if it does, confirm it isn't cancelled and then update it
    if event["status"] != "cancelled":
        event = events.update_event(hook, event)
        calendar_api.service.events().update(
            calendarId=calendar_api.calendarId,
            eventId=issueId,
            body=event
        ).execute()
    else:
        print("Event already cancelled")


# Handle webhook json when recieved
def handle_webhook(hook):
    action = determine_event_type(hook)
    if action:
        match action:
            case "created":
                create_issue(hook)
            case "updated":
                update_issue(hook)
            case "deleted":
                delete_issue(hook)
