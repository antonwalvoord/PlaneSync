import json

from flask import Flask, request

app = Flask(__name__)
webhook_file = "data/webhooks.json"


@app.route('/')
def hello_world():
    return 'PlaneSync Webhook Intercept'


@app.route('/webhook', methods=['POST'])
def handle_webhooks():
    webhook = request.get_json()
    print(f"\nRecieved info:\n{webhook}")

    with open(webhook_file, "a") as file:
        file.write(json.dumps(webhook))
        file.write("\n")

        print(f"\nWebhook saved to {file.name}")

    return "Data recieved"


@app.route('/clear_memory')
def clear_memory():
    with open(webhook_file, 'w') as file:
        file.write("")

    return "Memory cleared"
