# LINE API Webhook Handler Guide

## Overview

This guide explains how to use the `handle_webhook` function and how to access user messages when sending messages using the LINE API integration library.

## 1. Using `handle_webhook`

The `handle_webhook` function is the main entry point for processing LINE webhook events. It handles signature verification, event parsing, and routing events to your registered handlers.

### Basic Setup

```python
from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessagingClient,
    LineMessageEvent,
    LinePostbackEvent,
    TextMessage,
)

# Initialize configuration
config = LineAPIConfig()  # Loads from environment variables

# Create webhook handler
webhook_handler = LineWebhookHandler(config)

# Create messaging client for sending messages
messaging_client = LineMessagingClient(config)
```

### Required Environment Variables

```bash
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
```

### FastAPI Integration Example

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    # Get request data
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    # Parse JSON payload
    payload_dict = await request.json()
    
    # Process webhook with handler
    response = await webhook_handler.handle_webhook(
        request_body=body,
        signature=signature,
        payload_dict=payload_dict,
    )
    
    return JSONResponse(
        status_code=200,
        content=response.model_dump(),
    )
```

### Key Parameters for `handle_webhook`

- `request_body`: Raw request body as bytes (for signature verification)
- `signature`: X-Line-Signature header value from LINE
- `payload_dict`: Parsed JSON payload as dictionary

### Return Value

The function returns a `WebhookResponse` object with:
- `status`: "OK" or "ERROR"
- `message`: Optional response message
- `processed_events`: Number of events processed

## 2. Registering Event Handlers

The webhook handler provides decorators for different event types:

### Message Handler

```python
@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    """Handle incoming message events."""
    
    # Access user information
    user_id = event.source.userId
    
    # Handle different message types
    if event.message.type == "text":
        user_text = event.message.text
        print(f"User {user_id} sent: {user_text}")
        
        # Send reply using replyToken
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=f"You said: {user_text}")],
            )
```

### Postback Handler

```python
@webhook_handler.postback_handler
async def handle_postback_event(event: LinePostbackEvent) -> None:
    """Handle postback events from interactive elements."""
    
    user_id = event.source.userId
    postback_data = event.postback.data
    
    print(f"User {user_id} clicked: {postback_data}")
    
    if event.replyToken:
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text=f"You clicked: {postback_data}")],
        )
```

### Other Event Handlers

```python
@webhook_handler.follow_handler
async def handle_follow_event(event: LineEvent) -> None:
    """Handle follow events when users add the bot as a friend."""
    user_id = event.source.userId
    print(f"New follower: {user_id}")

@webhook_handler.unfollow_handler
async def handle_unfollow_event(event: LineEvent) -> None:
    """Handle unfollow events when users remove the bot."""
    user_id = event.source.userId
    print(f"User unfollowed: {user_id}")

@webhook_handler.join_handler
async def handle_join_event(event: LineEvent) -> None:
    """Handle join events when bot is added to a group."""
    group_id = event.source.groupId
    print(f"Bot joined group: {group_id}")
```

## 3. Getting User Messages When Sending Messages

### Method 1: Using Reply Token (Recommended)

When handling webhook events, you can use the `replyToken` to respond directly to the user's message:

```python
@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    # Get user message
    user_message = event.message.text if event.message.type == "text" else None
    user_id = event.source.userId
    
    # Process user message
    if user_message:
        response_text = f"You said: {user_message}"
        
        # Reply using replyToken (FREE - no charge)
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response_text)],
            )
```

### Method 2: Using Push Messages

For sending messages outside of webhook events, use push messages:

```python
async def send_push_message_to_user(user_id: str, message_text: str):
    """Send a push message to a specific user."""
    
    # Note: Push messages are charged
    await messaging_client.push_message(
        user_id=user_id,
        messages=[TextMessage(text=message_text)],
    )
```

### Method 3: Storing User Context

To access user messages in different contexts, store user data:

```python
# Simple in-memory storage (use database in production)
user_context = {}

@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    user_id = event.source.userId
    
    if event.message.type == "text":
        user_text = event.message.text
        
        # Store user's last message
        user_context[user_id] = {
            "last_message": user_text,
            "timestamp": event.timestamp,
        }
        
        # Use stored context in response
        if user_id in user_context:
            last_msg = user_context[user_id]["last_message"]
            response = f"Your current message: {user_text}\nYour last message: {last_msg}"
        else:
            response = f"Your message: {user_text}"
        
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response)],
            )
```

## 4. Advanced Message Handling

### Handling Different Message Types

```python
@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    user_id = event.source.userId
    
    if event.message.type == "text":
        # Text message
        user_text = event.message.text
        response = f"Text received: {user_text}"
        
    elif event.message.type == "image":
        # Image message
        response = "Thanks for the image!"
        
    elif event.message.type == "sticker":
        # Sticker message
        package_id = event.message.packageId
        sticker_id = event.message.stickerId
        response = f"Nice sticker! Package: {package_id}, Sticker: {sticker_id}"
        
    elif event.message.type == "location":
        # Location message
        title = event.message.title
        address = event.message.address
        response = f"Location: {title} at {address}"
        
    else:
        response = f"Received {event.message.type} message"
    
    if event.replyToken:
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text=response)],
        )
```

### Accessing User Information

```python
@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    # Source information
    source = event.source
    
    if source.type == "user":
        # Direct message from user
        user_id = source.userId
        context = "private chat"
        
    elif source.type == "group":
        # Message from group
        user_id = source.userId
        group_id = source.groupId
        context = f"group {group_id}"
        
    elif source.type == "room":
        # Message from room
        user_id = source.userId
        room_id = source.roomId
        context = f"room {room_id}"
    
    # Get message content
    message_text = event.message.text if event.message.type == "text" else "[non-text message]"
    
    print(f"User {user_id} in {context} said: {message_text}")
```

## 5. Error Handling

```python
@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    try:
        user_id = event.source.userId
        
        if event.message.type == "text":
            user_text = event.message.text
            
            # Process message
            response_text = process_user_message(user_text)
            
            # Send reply
            if event.replyToken:
                await messaging_client.reply_message(
                    reply_token=event.replyToken,
                    messages=[TextMessage(text=response_text)],
                )
                
    except Exception as e:
        print(f"Error handling message: {e}")
        
        # Send error message to user
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text="Sorry, something went wrong.")],
            )
```

## 6. Best Practices

### 1. Always Use Reply Token When Available
- Reply tokens are free and faster
- Only available for 1 minute after the event

### 2. Handle Different Message Types
- Not all messages are text messages
- Handle images, stickers, locations, etc.

### 3. Store User Context
- Use databases for persistent storage
- Store user preferences and conversation state

### 4. Implement Error Handling
- Always handle exceptions gracefully
- Provide meaningful error messages to users

### 5. Validate User Input
- Check message content before processing
- Implement rate limiting if needed

### 6. Use Async/Await
- All messaging operations are asynchronous
- Handle concurrent events properly

## 7. Complete Example

```python
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessagingClient,
    LineMessageEvent,
    LinePostbackEvent,
    TextMessage,
)

app = FastAPI()

# Initialize LINE API components
config = LineAPIConfig()
webhook_handler = LineWebhookHandler(config)
messaging_client = LineMessagingClient(config)

# User context storage
user_sessions = {}

@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    user_id = event.source.userId
    
    if event.message.type == "text":
        user_text = event.message.text
        
        # Store user message
        if user_id not in user_sessions:
            user_sessions[user_id] = {"messages": []}
        
        user_sessions[user_id]["messages"].append(user_text)
        
        # Create response based on conversation history
        message_count = len(user_sessions[user_id]["messages"])
        response = f"Message #{message_count}: {user_text}"
        
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response)],
            )

@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    try:
        body = await request.body()
        signature = request.headers.get("X-Line-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        payload_dict = await request.json()
        
        response = await webhook_handler.handle_webhook(
            request_body=body,
            signature=signature,
            payload_dict=payload_dict,
        )
        
        return JSONResponse(status_code=200, content=response.model_dump())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This guide provides a comprehensive overview of using `handle_webhook` and accessing user messages in the LINE API integration library. The key is to use the webhook events to capture user messages and respond appropriately using reply tokens or push messages.