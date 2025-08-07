import os
import shutil
from datetime import datetime
import webhooks

webhook_file = "/home/aewal/NFR26/timeline_tools/local_app/data/webhooks.json"

current_date = datetime.now().strftime("%Y-%m-%d")
webhook_backup = f"/home/aewal/NFR26/timeline_tools/local_app/data/{
    current_date}-Backup.json"

line_num = 1

with open(webhook_file, 'r') as webhook_json:

    print(f"Processing file: {webhook_json.name}")

    for line in webhook_json:
        print(f"\nProcessing line {line_num}")
        if line:
            hook = webhooks.parse_webhook(line)
            webhooks.handle_webhook(hook)
        line_num += 1

prompt_clear = input("\n\n\nBack up webhook data? (y/n)\n")
if prompt_clear == "y":
    print("...Backing up webhook data")
    shutil.copy(webhook_file, webhook_backup)
    print("Webhook data backed up to file: ")

else:
    print("No backup created")

prompt_clear = input("\n\n\nClear webhook data? (y/n)\n")
if prompt_clear == "y":
    print("...Clearing webhook data")
    os.remove(webhook_file)
    print("Webhook data cleared")

else:
    print("Exiting without clearing")
