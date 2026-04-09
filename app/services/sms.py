from twilio.rest import Client

from app.core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER


def send_bill_sms(bill: dict) -> str:
    lines = [f"🧾 Bill #{bill['id']} from {bill['customer_name']}"]
    lines.append("─" * 20)

    for item in bill["items"]:
        lines.append(f"{item['item_name']} x{item['quantity']} = ₹{item['price']:.2f}")
    lines.append("─" * 20)

    lines.append(f"TOTAL: ₹{bill['total_amount']:.2f}")
    lines.append(f"Status: {bill['payment_status'].upper()}")

    message_body = "\n".join(lines)

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=bill["customer_phone"],
        )
        return f"SMS sent successfully (SID: {message.sid})"
    except Exception:
        return "SMS failed"
