"""
Simple LINE Text Message Webhook Example

This is a minimal example showing how to receive user text messages from LINE webhooks.

Environment Variables Required:
    LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
    LINE_CHANNEL_SECRET=your_channel_secret

Install Dependencies:
    pip install fastapi uvicorn line-api
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessagingClient,
    LineMessageEvent,
    TextMessage,
)

# Initialize LINE API components
config = LineAPIConfig()
webhook_handler = LineWebhookHandler(config)
messaging_client = LineMessagingClient(config)

# FastAPI app
app = FastAPI()


@webhook_handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    """Handle incoming messages from users."""
    
    # Get user ID
    user_id = event.source.userId
    
    # Check if it's a text message
    if event.message.type == "text":
        # Get the user's text message
        user_text = event.message.text
        
        print(f"User {user_id} sent: {user_text}")
        
        # Create response
        response_text = f"You said: {user_text}"
        
        # Send reply back to user
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response_text)],
            )


@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    """Webhook endpoint to receive LINE events."""
    
    # Get request data
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")
    payload_dict = await request.json()
    
    # Process webhook
    response = await webhook_handler.handle_webhook(
        request_body=body,
        signature=signature,
        payload_dict=payload_dict,
    )
    
    return JSONResponse(status_code=200, content=response.model_dump())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)