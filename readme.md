## WHMCS GSM and Dialpad Onboarding function

#### This Google Cloud Functions implementation has the following features:
- Subscribed to a Pub/Sub topic: Push subscription.
- Messages from the Pub/Sub topic contains WHMCS order data
- This function then creates the equivalent Asana project based on the order type.
- Function also send the Pub/Sub message into a Zapier webhook.