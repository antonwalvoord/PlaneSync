import os
import webhooks

webhook_file = "/home/aewal/NFR26/timeline_tools/local_app/data/webhooks.json"
line = 1

with open(webhook_file, 'r') as webhook_json:

    print(f"Processing file: {webhook_json.name}")

    for line in webhook_json:
        print(f"\nProcessing line {line}")
        if line:
            hook = webhooks.parse_webhook(line)
            webhooks.handle_webhook(hook)

prompt_clear = input("\n\n\nClear webhook data? (y/n)\n")
if prompt_clear == "y":
    print("...Clearing webhook data")
    os.remove(webhook_file)
    print("Webhook data cleared")

else:
    print("Exiting without clearing")
