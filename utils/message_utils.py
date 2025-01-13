from firebase_admin import messaging

def send_topic_notification(topic):

    prayer = topic.split('_')[0].capitalize()
    reminder_type = topic.split('_')[1].capitalize()
    title = f'{prayer} {reminder_type}'
    body = ''
    ios_sound = 'default'
    android_sound = 'default'
    if prayer == "Jumaa":
        body = f'{prayer} {reminder_type} is in 1 Hour'
        ios_sound = "iqama.wav"
        android_sound = "iqama"
    elif reminder_type == 'Adhan':
        body = f"It's time for {prayer} prayer"
        ios_sound = 'adhan.wav'
        android_sound = 'adhan'
    else:
        body = f"{prayer} Iqama is in 20 Minutes"
        ios_sound = 'iqama.wav'
        android_sound = 'iqama'

    message = messaging.Message(
        topic=topic,
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(sound=android_sound)
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(sound=ios_sound)
            )
        )
    )

    payload = {
        "message": {
            "topic": topic,
            "notification": {
                "title": title,
                "body": body,
            },
            "android": {
                "notification": {
                    "sound": android_sound,  # For Android devices
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "sound": ios_sound  # For iOS devices
                    }
                }
            }
        }
    }

    try:
        # Send the message
        response = messaging.send(message)
        print(f"Notification sent successfully: {response}")
    except Exception as e:
        print(f"Failed to send notification: {e}")