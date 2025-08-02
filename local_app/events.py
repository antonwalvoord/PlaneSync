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
            case "Operations":
                return "9"
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

        # If there is no new due date we cannot update the
        # calendar appropriately and should return an exception
        if due_date is None:
            print("DUE DATE IS NONE")
            return Exception

    # There may only be an id if this is an update
    # due to a deletion
    except Exception:
        if color is not None:
            event['colorId'] = color
        print("\n\n    ran into exception\n\n")
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


def remove_module(hook, event):
    print("Removing from module...")
    event['colorId'] = None
    return event
