"""
LINE Webhook Text Message Handler Example

This example demonstrates how to receive and handle user text messages
from LINE webhooks using the LINE API integration library.

Requirements:
    pip install fastapi uvicorn line-api

Environment Variables:
    LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
    LINE_CHANNEL_SECRET=your_channel_secret
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessagingClient,
    LineMessageEvent,
    TextMessage,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="LINE Text Message Handler", version="1.0.0")

# Initialize LINE API components
config = LineAPIConfig()
webhook_handler = LineWebhookHandler(config)
messaging_client = LineMessagingClient(config)

# Store user messages (use database in production)
user_messages = {}


@webhook_handler.message_handler
async def handle_text_message(event: LineMessageEvent) -> None:
    """Handle incoming text messages from users."""
    
    # Get user information
    user_id = event.source.userId
    
    # Check if it's a text message
    if event.message.type == "text":
        # Get the user's text message
        user_text = event.message.text
        
        # Log the received message
        logger.info(f"Received text from user {user_id}: {user_text}")
        
        # Store the message (optional - for conversation history)
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append(user_text)
        
        # Process the message and create response
        response_text = process_user_message(user_text, user_id)
        
        # Send reply using replyToken (FREE)
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response_text)],
            )
    else:
        # Handle non-text messages
        logger.info(f"Received non-text message from user {user_id}: {event.message.type}")
        
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text="I can only handle text messages for now.")],
            )


def process_user_message(user_text: str, user_id: str) -> str:
    """Process user text message and return appropriate response."""
    
    # Convert to lowercase for easier matching
    text_lower = user_text.lower().strip()
    
    # Simple command responses
    if text_lower in ["hello", "hi", "hey", "good morning", "good evening"]:
        return f"Hello! 👋 How can I help you today?"
    
    elif text_lower in ["bye", "goodbye", "see you", "good night"]:
        return "Goodbye! Have a great day! 🌟"
    
    elif text_lower == "help":
        return (
            "🤖 Available commands:\n"
            "• hello - Greet the bot\n"
            "• help - Show this help message\n"
            "• status - Check bot status\n"
            "• history - Show your recent messages\n"
            "• clear - Clear your message history\n"
            "• bye - Say goodbye"
        )
    
    elif text_lower == "status":
        return "🟢 Bot is running perfectly!"
    
    elif text_lower == "history":
        if user_id in user_messages and user_messages[user_id]:
            messages = user_messages[user_id][-5:]  # Last 5 messages
            history = "\n".join([f"• {msg}" for msg in messages])
            return f"📝 Your recent messages:\n{history}"
        else:
            return "📝 No message history found."
    
    elif text_lower == "clear":
        if user_id in user_messages:
            user_messages[user_id] = []
        return "🗑️ Message history cleared!"
    
    elif text_lower.startswith("echo "):
        # Echo command - repeat what user said
        echo_text = user_text[5:]  # Remove "echo " prefix
        return f"🔄 You said: {echo_text}"
    
    elif text_lower.startswith("reverse "):
        # Reverse command - reverse the text
        reverse_text = user_text[8:]  # Remove "reverse " prefix
        return f"🔄 Reversed: {reverse_text[::-1]}"
    
    elif text_lower.startswith("count "):
        # Count command - count characters
        count_text = user_text[6:]  # Remove "count " prefix
        char_count = len(count_text)
        word_count = len(count_text.split())
        return f"📊 Characters: {char_count}, Words: {word_count}"
    
    else:
        # Default response for unrecognized messages
        return (
            f"Thanks for your message: '{user_text}'\n"
            f"💡 Try typing 'help' to see available commands!"
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "LINE Text Message Handler is active",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "LINE Text Message Handler",
        "webhook_handler": "ready",
        "messaging_client": "ready",
        "total_users": len(user_messages),
        "total_messages": sum(len(msgs) for msgs in user_messages.values())
    }


@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    """
    Main webhook endpoint for receiving LINE text messages.
    
    This endpoint receives webhook events from LINE Platform and processes them.
    """
    try:
        # Get request data
        body = await request.body()
        signature = request.headers.get("X-Line-Signature")
        
        if not signature:
            logger.error("Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature header")
        
        # Parse JSON payload
        try:
            payload_dict = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process webhook with handler
        response = await webhook_handler.handle_webhook(
            request_body=body,
            signature=signature,
            payload_dict=payload_dict,
        )
        
        logger.info(f"Webhook processed successfully: {response.processed_events} events")
        
        return JSONResponse(
            status_code=200,
            content=response.model_dump(),
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Additional endpoint to send push messages (optional)
@app.post("/send-message")
async def send_push_message(user_id: str, message: str):
    """
    Send a push message to a specific user.
    
    This is useful for sending proactive messages outside of webhook events.
    Note: Push messages are charged by LINE.
    """
    try:
        await messaging_client.push_message(
            user_id=user_id,
            messages=[TextMessage(text=message)],
        )
        
        return {"status": "success", "message": "Push message sent"}
    
    except Exception as e:
        logger.error(f"Failed to send push message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting LINE Text Message Handler server...")
    logger.info("Make sure to set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET")
    
    # Run the server
    uvicorn.run(
        "webhook_text_message_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )