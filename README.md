# Intended Functionality:
Be able to create calendar events from work items
Be able to update calendar events from work items
Be able to delete calendar events from work items

# What information do you need to create / update
## Create:
"data","target_date" -- Due date
"data","name" -- Name
"data","description_html" -- Details
"data","id" -- ID

## Update:
There is a dedicated google calendar method for this function.

When creating a new event, specify it's id to match Plane's id and then you can use "get" and "update" based on the shared id
"data","name" -- Name?
"data","id" -- ID
"data","target_date" -- Due date
