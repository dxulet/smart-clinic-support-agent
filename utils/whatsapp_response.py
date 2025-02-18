import os
import httpx
import requests
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")


async def send_response(response_text: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    json_data = {
        "messaging_product": "whatsapp",
        "to": "787077146923",
        "type": "text",
        "text": {"body": response_text},
    }

    print(headers)
    print(json_data)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://graph.facebook.com/v22.0/543652922169927/messages",
            headers=headers,
            json=json_data,
        )

    return response.status_code == 200

# def send_whatsapp_text_message():
#     url = "https://graph.facebook.com/v22.0/543652922169927/messages"
#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json",
#     }
    
#     json_data = {
#         "messaging_product": "whatsapp",
#         "to": "787077146923",
#         "type": "template", 
#         "template": { "name": "hello_world", "language": { "code": "en_US" } }
#     }
#     response = requests.post(url, headers=headers, json=json_data)
#     return response

