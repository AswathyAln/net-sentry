import requests
try:
    requests.post('https://ntfy.sh/bunny_alert_123', data='🚨 Net-Sentry: The Voice is Working!')
    print('✅ Message Sent! Go check the website.')
except Exception as e:
    print(f'❌ Error: {e}')
