# LINE Webhook Setup Guide

This guide provides comprehensive instructions for setting up and configuring LINE webhooks using the LINE API Integration Library.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Quick Start](#quick-start)
5. [Webhook Handler Implementation](#webhook-handler-implementation)
6. [Supported Event Types](#supported-event-types)
7. [Security and Signature Verification](#security-and-signature-verification)
8. [Framework Integration](#framework-integration)
9. [Testing Your Webhook](#testing-your-webhook)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

## Introduction

LINE webhooks enable real-time communication between LINE Platform and your application. When users interact with your LINE bot (sending messages, clicking buttons, etc.), LINE sends webhook events to your server, allowing you to process these events and respond accordingly.

This library provides a comprehensive, type-safe webhook handling system with:

- **Type-safe event models** with Pydantic validation
- **Automatic signature verification** for security
- **Flexible event handler system** with decorators
- **Comprehensive error handling** and logging
- **Support for all LINE webhook event types**

## Prerequisites

### LINE Bot Channel Setup

1. **Create a LINE Bot Channel** in [LINE Developers Console](https://developers.line.biz/console/)
2. **Get your credentials**:
   - Channel Access Token
   - Channel Secret
3. **Configure webhook URL** in your channel settings

### Development Environment

```bash
# Install dependencies
pip install line-api fastapi uvicorn

# Or using uv (recommended)
uv add line-api fastapi uvicorn
```

## Environment Configuration

Create a `.env` file in your project root:

```bash
# Required: LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here

# Optional: Development Configuration
LINE_API_DEBUG=true
LINE_API_TIMEOUT=30
LINE_API_MAX_RETRIES=3
```

### Configuration Loading

The library automatically discovers and loads configuration:

```python
from line_api.core import LineAPIConfig

# Automatically loads from .env file and environment variables
config = LineAPIConfig()
```

## Quick Start

Here's a minimal webhook implementation:

```python
from fastapi import FastAPI, Request
from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessageEvent,
    LineMessagingClient,
    TextMessage,
)

app = FastAPI()

# Initialize components
config = LineAPIConfig()
webhook_handler = LineWebhookHandler(config)
messaging_client = LineMessagingClient(config)

@webhook_handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    """Handle incoming messages."""
    if event.message.type == "text":
        # Echo the message back
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text=f"You said: {event.message.text}")],
        )

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """Main webhook endpoint."""
    response = await webhook_handler.handle_webhook(
        request_body=await request.body(),
        signature=request.headers.get("X-Line-Signature"),
        payload_dict=await request.json()
    )
    return response.model_dump()
```

## Webhook Handler Implementation

### Basic Handler Setup

```python
from line_api.webhook import LineWebhookHandler
from line_api.core import LineAPIConfig

# Initialize configuration
config = LineAPIConfig()

# Create webhook handler
handler = LineWebhookHandler(
    config=config,
    verify_signature=True,  # Enable signature verification (recommended)
    track_processed_events=True,  # Enable duplicate event detection
)
```

### Event Handler Registration

#### Using Decorators (Recommended)

```python
@handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    """Handle message events."""
    print(f"Received message: {event.message.text}")

@handler.postback_handler
async def handle_postback(event: LinePostbackEvent) -> None:
    """Handle postback events."""
    print(f"Postback data: {event.postback.data}")

@handler.follow_handler
async def handle_follow(event: LineFollowEvent) -> None:
    """Handle follow events."""
    print(f"New follower: {event.source.userId}")
```

#### Manual Registration

```python
async def my_message_handler(event: LineEvent) -> None:
    if isinstance(event, LineMessageEvent):
        print(f"Message: {event.message.text}")

# Register the handler
handler.register_handler("message", my_message_handler)
```

## Supported Event Types

### Message Events

Handle various message types from users:

```python
@handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    """Handle different message types."""
    message = event.message

    if message.type == "text":
        text_msg = message  # LineTextMessage
        print(f"Text: {text_msg.text}")

    elif message.type == "image":
        image_msg = message  # LineImageMessage
        print(f"Image ID: {image_msg.id}")

    elif message.type == "video":
        video_msg = message  # LineVideoMessage
        print(f"Video duration: {video_msg.duration}")

    elif message.type == "audio":
        audio_msg = message  # LineAudioMessage
        print(f"Audio duration: {audio_msg.duration}")

    elif message.type == "file":
        file_msg = message  # LineFileMessage
        print(f"File: {file_msg.fileName}")

    elif message.type == "location":
        location_msg = message  # LineLocationMessage
        print(f"Location: {location_msg.latitude}, {location_msg.longitude}")

    elif message.type == "sticker":
        sticker_msg = message  # LineStickerMessage
        print(f"Sticker: {sticker_msg.packageId}/{sticker_msg.stickerId}")
```

### Postback Events

Handle button clicks and interactive element interactions:

```python
@handler.postback_handler
async def handle_postback(event: LinePostbackEvent) -> None:
    """Handle postback events from buttons and interactive elements."""
    postback_data = event.postback.data

    if postback_data == "action=menu":
        # Handle main menu selection
        pass
    elif postback_data.startswith("action=select_"):
        # Handle item selection
        item = postback_data.replace("action=select_", "")
        print(f"Selected: {item}")
```

### User Lifecycle Events

```python
@handler.follow_handler
async def handle_follow(event: LineFollowEvent) -> None:
    """Handle when user follows the bot."""
    user_id = event.source.userId
    print(f"New follower: {user_id}")

    # Send welcome message
    if event.replyToken:
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text="Welcome! Thanks for following!")],
        )

@handler.unfollow_handler
async def handle_unfollow(event: LineUnfollowEvent) -> None:
    """Handle when user unfollows the bot."""
    user_id = event.source.userId
    print(f"User unfollowed: {user_id}")
    # Note: Cannot send messages to unfollowed users
```

### Group/Room Events

```python
@handler.join_handler
async def handle_join(event: LineJoinEvent) -> None:
    """Handle when bot joins a group or room."""
    if event.source.type == "group":
        print(f"Joined group: {event.source.groupId}")
    elif event.source.type == "room":
        print(f"Joined room: {event.source.roomId}")

@handler.leave_handler
async def handle_leave(event: LineLeaveEvent) -> None:
    """Handle when bot leaves a group or room."""
    print("Bot left group/room")
```

### Other Event Types

```python
@handler.unsend_handler
async def handle_unsend(event: LineUnsendEvent) -> None:
    """Handle when user unsends a message."""
    print(f"Message unsent: {event.unsend}")

# Additional event handlers available:
# - member_join_handler
# - member_leave_handler
# - beacon_handler
# - account_link_handler
# - video_play_complete_handler
```

## Security and Signature Verification

### Automatic Signature Verification

The library automatically verifies webhook signatures using your channel secret:

```python
# Signature verification is enabled by default
handler = LineWebhookHandler(config, verify_signature=True)
```

### Manual Signature Verification

```python
from line_api.webhook import verify_webhook_signature, safe_verify_webhook_signature

# Manual verification
is_valid = verify_webhook_signature(
    request_body=request_body,
    signature=signature,
    channel_secret=config.channel_secret
)

# Safe verification (handles None values)
is_valid = safe_verify_webhook_signature(
    request_body=request_body,
    signature=signature,
    channel_secret=config.channel_secret
)
```

### Security Best Practices

1. **Always verify signatures** in production
2. **Use HTTPS** for webhook endpoints
3. **Validate payload structure** with Pydantic models
4. **Handle errors gracefully** to prevent information leakage
5. **Log security events** for monitoring

## Framework Integration

### FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """LINE webhook endpoint."""
    try:
        response = await webhook_handler.handle_webhook(
            request_body=await request.body(),
            signature=request.headers.get("X-Line-Signature"),
            payload_dict=await request.json()
        )
        return JSONResponse(content=response.model_dump())
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "line-webhook"}
```

### Flask Integration

```python
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE webhook endpoint."""
    try:
        # Run async handler in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            webhook_handler.handle_webhook(
                request_body=request.data,
                signature=request.headers.get('X-Line-Signature'),
                payload_dict=request.get_json()
            )
        )

        return jsonify(response.model_dump())
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

## Testing Your Webhook

### Local Development

1. **Use ngrok** for local testing:
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start your local server
uvicorn main:app --reload --port 8000

# In another terminal, expose your local server
ngrok http 8000

# Use the ngrok URL in LINE Developers Console
# Example: https://abc123.ngrok.io/webhook
```

2. **Test with LINE Bot SDK**:
```python
# Test webhook payload parsing
test_payload = {
    "destination": "bot_user_id",
    "events": [
        {
            "type": "message",
            "timestamp": 1234567890,
            "source": {"type": "user", "userId": "user123"},
            "mode": "active",
            "webhookEventId": "event123",
            "deliveryContext": {"isRedelivery": False},
            "replyToken": "reply123",
            "message": {
                "id": "msg123",
                "type": "text",
                "text": "Hello, bot!"
            }
        }
    ]
}

# Test parsing
from line_api.webhook import LineWebhookPayload
payload = LineWebhookPayload.model_validate(test_payload)
```

### Unit Testing

```python
import pytest
from line_api.webhook import LineWebhookHandler, LineMessageEvent
from line_api.core import LineAPIConfig

@pytest.fixture
def webhook_handler():
    config = LineAPIConfig()
    return LineWebhookHandler(config, verify_signature=False)

@pytest.mark.asyncio
async def test_message_handler(webhook_handler):
    """Test message handler registration and execution."""
    handled_events = []

    @webhook_handler.message_handler
    async def handle_message(event: LineMessageEvent):
        handled_events.append(event)

    # Test with mock event
    test_event = LineMessageEvent(
        type="message",
        timestamp=1234567890,
        source={"type": "user", "userId": "user123"},
        mode="active",
        webhookEventId="event123",
        deliveryContext={"isRedelivery": False},
        message={"id": "msg123", "type": "text", "text": "test"}
    )

    await webhook_handler._process_event(test_event)
    assert len(handled_events) == 1
```

## Advanced Features

### Duplicate Event Detection

```python
# Enable duplicate event detection (default: True)
handler = LineWebhookHandler(
    config=config,
    track_processed_events=True
)

# Events with the same webhookEventId will be processed only once
```

### Multiple Event Handlers

```python
# Register multiple handlers for the same event type
@handler.message_handler
async def log_message(event: LineMessageEvent) -> None:
    """Log all messages."""
    logger.info(f"Message received: {event.message.text}")

@handler.message_handler
async def respond_to_message(event: LineMessageEvent) -> None:
    """Respond to messages."""
    if event.message.type == "text":
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text="Message received!")]
        )
```

### Error Handling

```python
@handler.message_handler
async def handle_message_with_error_handling(event: LineMessageEvent) -> None:
    """Handle messages with comprehensive error handling."""
    try:
        # Process message
        if event.message.type == "text":
            await process_text_message(event)
    except Exception as e:
        logger.error(f"Failed to process message {event.webhookEventId}: {e}")
        # Send error response to user
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text="Sorry, I encountered an error.")]
            )
```

## Troubleshooting

### Common Issues

#### 1. Signature Verification Failures

**Problem**: Webhook returns "Invalid signature" error

**Solutions**:
- Verify `LINE_CHANNEL_SECRET` is correct
- Ensure you're using the raw request body (not parsed JSON)
- Check that the signature header is `X-Line-Signature`

```python
# Debug signature verification
import logging
logging.basicConfig(level=logging.DEBUG)

# Check signature manually
from line_api.webhook import verify_webhook_signature
is_valid = verify_webhook_signature(
    request_body=request_body,
    signature=signature,
    channel_secret=config.channel_secret
)
print(f"Signature valid: {is_valid}")
```

#### 2. Event Not Being Processed

**Problem**: Events are received but handlers are not called

**Solutions**:
- Check handler registration: `handler.get_handler_count()`
- Verify event type matches handler decorator
- Check for exceptions in handler functions

```python
# Debug handler registration
print(f"Registered handlers: {handler.get_handler_count()}")

# Add debug logging to handlers
@handler.message_handler
async def debug_message_handler(event: LineMessageEvent) -> None:
    print(f"Handler called for event: {event.webhookEventId}")
```

#### 3. Webhook Timeout

**Problem**: Webhook requests timing out

**Solutions**:
- Optimize handler performance
- Use async operations
- Implement background task processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

@handler.message_handler
async def handle_message_async(event: LineMessageEvent) -> None:
    """Handle message with background processing."""
    # Quick response
    if event.replyToken:
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text="Processing your request...")]
        )

    # Background processing
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, process_message_background, event)
```

### Debug Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Debug webhook processing
handler = LineWebhookHandler(
    config=config,
    verify_signature=True,
    track_processed_events=True
)
```

## Best Practices

### 1. Environment Configuration

```python
# Use environment-specific configuration
import os
from line_api.core import LineAPIConfig

config = LineAPIConfig()

# Development vs Production
if os.getenv("ENVIRONMENT") == "development":
    # Disable signature verification for testing
    handler = LineWebhookHandler(config, verify_signature=False)
else:
    # Always verify signatures in production
    handler = LineWebhookHandler(config, verify_signature=True)
```

### 2. Error Handling and Logging

```python
import logging
from line_api.webhook import WebhookHandlerError

logger = logging.getLogger(__name__)

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """Webhook endpoint with comprehensive error handling."""
    try:
        response = await webhook_handler.handle_webhook(
            request_body=await request.body(),
            signature=request.headers.get("X-Line-Signature"),
            payload_dict=await request.json()
        )

        logger.info(f"Webhook processed: {response.processed_events} events")
        return response.model_dump()

    except WebhookHandlerError as e:
        logger.error(f"Webhook handler error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Webhook processing failed"}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

### 3. Performance Optimization

```python
# Use connection pooling for messaging client
messaging_client = LineMessagingClient(
    config=config,
    timeout=30.0,
    max_retries=3
)

# Batch message processing
@handler.message_handler
async def handle_message_batch(event: LineMessageEvent) -> None:
    """Handle messages with batching for performance."""
    # Add to processing queue instead of immediate processing
    await message_queue.put(event)

# Process messages in batches
async def process_message_batch():
    """Process messages in batches for efficiency."""
    messages = []
    while len(messages) < 10:  # Batch size
        try:
            message = await asyncio.wait_for(message_queue.get(), timeout=1.0)
            messages.append(message)
        except asyncio.TimeoutError:
            break

    if messages:
        await process_messages_batch(messages)
```

### 4. Monitoring and Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
webhook_events_total = Counter('webhook_events_total', 'Total webhook events', ['event_type'])
webhook_processing_duration = Histogram('webhook_processing_duration_seconds', 'Webhook processing duration')

@handler.message_handler
async def handle_message_with_metrics(event: LineMessageEvent) -> None:
    """Handle messages with metrics collection."""
    webhook_events_total.labels(event_type='message').inc()

    with webhook_processing_duration.time():
        # Process message
        await process_message(event)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

---

## Next Steps

1. **Review the [webhook example](../examples/webhook_example.py)** for a complete implementation
2. **Check the [messaging documentation](../docs/README.md)** for sending responses
3. **Explore [Flex Messages](../docs/flex-messages/README.md)** for rich interactive content
4. **Set up monitoring** for your webhook endpoint
5. **Test thoroughly** in a staging environment before production deployment

For more advanced features and examples, check the [examples directory](../examples/) and the [API documentation](../docs/README.md).
