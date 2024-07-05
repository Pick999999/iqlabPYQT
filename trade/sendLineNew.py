import requests

def send_line_notify(message, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token
    }
    data = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

# Example data
data = [
    {"currency": "EURUSD", "amount": 1, "profit": 0.85},
    {"currency": "GBPUSD", "amount": 1, "profit": 1.2},
    {"currency": "USDJPY", "amount": 1, "profit": -0.5}
]

# Create a plain text table
message = "Trade Results:\n"
message += "{:<10} {:<10} {:<10}\n".format("Currency", "Amount", "Profit")
message += "-"*30 + "\n"
for item in data:
    message += "{:<10} {:<10} {:<10.2f}\n".format(item["currency"], str(item["amount"]), item["profit"])

# Line Notify Token
token = "YOUR_LINE_NOTIFY_TOKEN"
token = "nhEKEQa0ugEgqGolp580dMr2wxylcgJK4q63L7fL9pW"
# Send the message
status_code = send_line_notify(message, token)
if status_code == 200:
    print("Message sent successfully")
else:
    print("Failed to send message")
