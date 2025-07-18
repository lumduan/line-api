# LineKit - LINE API Integration Library

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Safety: mypy](https://img.shields.io/badge/type%20safety-mypy-blue.svg)](http://mypy-lang.org/)

A comprehensive, type-safe Python library for integrating with LINE's APIs. Built with modern async/await patterns, full Pydantic type safety, and designed for production use.

**🎉 LATEST UPDATE (July 2025)**: Successfully completed comprehensive FlexMessage model updates with full LINE API specification compliance, added new FlexSpan and FlexVideo components, achieved 100% mypy strict mode compliance, and created production-ready pull request #3.

## 🚀 Features

- 🚀 **Push Messages**: Send messages directly to users
- 📢 **Multicast Messages**: Efficiently send messages to multiple users (up to 500)
- 📱 **Multiple Message Types**: Text, images, locations, stickers, and Flex messages
- 🎨 **Flex Messages**: Type-safe Flex Message creation with Pydantic models
  - **NEW**: FlexSpan component for styled text within text components
  - **NEW**: FlexVideo component for video content in hero blocks
  - **ENHANCED**: Complete enum support and modern properties
- 📡 **Webhook Handling**: Complete webhook integration with signature verification
- 🎯 **Event Handlers**: Decorator-based event handling for messages, postbacks, follows
- 🛡️ **Security**: LINE signature verification for webhook authenticity
- 📋 **JSON Export**: Export Flex Messages for LINE simulator testing
- 📋 **Clipboard Integration**: Automatic clipboard copy for testing
- 🔒 **Type Safety**: Full Pydantic integration with comprehensive type hints
- ⚡ **Async-First**: Built for high-performance async/await operations
- 🛡️ **Error Handling**: Comprehensive error handling with typed exceptions
- 🔄 **Retry Logic**: Built-in retry mechanisms with exponential backoff
- 📊 **Rate Limiting**: Automatic rate limit handling
- 🔇 **Silent Notifications**: Option to send messages without push notifications
- 📊 **Analytics Integration**: Custom aggregation units for message tracking
- 🔄 **Idempotent Requests**: Retry keys to prevent duplicate message sending

## 🛠 Installation

```bash
# Using pip
pip install linekit

# Using uv
uv pip install linekit
```

## ⚡ Quick Start

### 1. Configuration

Set up your LINE channel credentials:

```bash
# Environment variables
export LINE_CHANNEL_ACCESS_TOKEN="your_channel_access_token"
export LINE_CHANNEL_SECRET="your_channel_secret"
```

Or create a `.env` file:

```env
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
```

### 2. Send a Push Message

```python
import asyncio
from line_api import LineAPIConfig, LineMessagingClient, TextMessage

async def send_message():
    # Load configuration
    config = LineAPIConfig.from_env_file()

    # Create message
    message = TextMessage.create("Hello from LINE API! 🚀")

    # Send push message
    async with LineMessagingClient(config) as client:
        success = await client.push_message("USER_ID_HERE", [message])
        if success:
            print("Message sent successfully!")

# Run the example
asyncio.run(send_message())
```

### 3. Send Multicast Messages

```python
import asyncio
import uuid
from line_api import LineAPIConfig, LineMessagingClient, TextMessage

async def send_multicast():
    # Load configuration
    config = LineAPIConfig.from_env_file()

    # User IDs to send to (get these from webhook events)
    user_ids = [
        "U1234567890abcdef1234567890abcdef",  # User ID 1
        "U0987654321fedcba0987654321fedcba",  # User ID 2
        "Uabcdef1234567890abcdef1234567890",  # User ID 3
    ]

    # Create messages (up to 5 messages)
    messages = [
        TextMessage.create("🎉 Hello everyone!"),
        TextMessage.create("This message was sent to multiple users simultaneously."),
    ]

    async with LineMessagingClient(config) as client:
        # Basic multicast
        success = await client.multicast_message(
            user_ids=user_ids,
            messages=messages,
        )

        if success:
            print(f"✅ Multicast sent to {len(user_ids)} users!")

        # Advanced multicast with options
        success = await client.multicast_message(
            user_ids=user_ids,
            messages=[TextMessage.create("📊 Campaign message")],
            notification_disabled=False,  # Users get push notifications
            custom_aggregation_units=["summer_campaign_2024"],  # For analytics
            retry_key=str(uuid.uuid4()),  # For request idempotency
        )

        # Silent multicast (no push notifications)
        success = await client.multicast_message(
            user_ids=user_ids,
            messages=[TextMessage.create("🔇 Silent update")],
            notification_disabled=True,  # No push notifications
        )

# Run the example
asyncio.run(send_multicast())
```

### 4. Create Flex Messages

```python
from line_api import (
    FlexBox,
    FlexBubble,
    FlexLayout,
    FlexMessage,
    FlexText,
    FlexSpan,
    FlexTextWeight,
    print_flex_json,
)

# Create a simple flex message
def create_welcome_message():
    # Create text with styled spans
    title = FlexText.create(
        text="Rich text with spans",
        contents=[
            FlexSpan.create("Welcome", weight=FlexTextWeight.BOLD, color="#1E3A8A"),
            FlexSpan.create(" to our ", color="#666666"),
            FlexSpan.create("LINE API Library!", weight=FlexTextWeight.BOLD, color="#00C300")
        ]
    )

    subtitle = FlexText.create(
        text="Thank you for using our comprehensive LINE integration library!",
        wrap=True,
        color="#555555",
        margin="md"
    )

    # Create a vertical box layout
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, subtitle],
        spacing="md",
        padding_all="20px",
    )

    # Create bubble
    bubble = FlexBubble.create(body=body)

    # Create flex message
    return FlexMessage.create(
        alt_text="Welcome Message",
        contents=bubble,
    )

# Create and export to JSON for testing
message = create_welcome_message()
print_flex_json(message, "Welcome Message")
# JSON is automatically copied to clipboard!
# Paste it into https://developers.line.biz/flex-simulator/
```

### 5. Handle LINE Webhooks

```python
from fastapi import FastAPI, Request
from line_api import (
    LineAPIConfig,
    LineWebhookHandler,
    LineMessagingClient,
    LineMessageEvent,
    TextMessage,
)

app = FastAPI()

# Initialize components
config = LineAPIConfig()
webhook_handler = LineWebhookHandler(config)
messaging_client = LineMessagingClient(config)

# Register event handlers using decorators
@webhook_handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    """Handle incoming text messages."""
    if event.message.type == "text":
        user_text = event.message.text

        # Create smart responses
        if user_text.lower() in ["hello", "hi", "hey"]:
            response = "Hello! How can I help you today?"
        elif user_text.lower() == "help":
            response = "Available commands: hello, help, status"
        else:
            response = f"You said: {user_text}"

        # Reply to user
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response)]
            )

@webhook_handler.follow_handler
async def handle_follow(event) -> None:
    """Welcome new followers."""
    welcome_msg = "🎉 Welcome! Thanks for adding me as a friend!"
    reply_token = getattr(event, "replyToken", None)
    if reply_token:
        await messaging_client.reply_message(
            reply_token=reply_token,
            messages=[TextMessage(text=welcome_msg)]
        )

# FastAPI webhook endpoint
@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """Receive webhooks from LINE Platform."""
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")
    payload_dict = await request.json()

    # Process webhook with automatic signature verification
    response = await webhook_handler.handle_webhook(
        request_body=body,
        signature=signature,
        payload_dict=payload_dict
    )

    return response.model_dump()

# Run with: uvicorn your_app:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### ✅ What's Working

- ✅ Core configuration management with Pydantic
- ✅ LINE Messaging API integration
- ✅ Text message support with type safety
- ✅ **Multicast Messages**: Complete multicast messaging with advanced options
  - ✅ Send to up to 500 users simultaneously
  - ✅ Silent notifications support
  - ✅ Custom aggregation units for analytics
  - ✅ Retry keys for idempotent requests
- ✅ **Flex Messages**: Complete type-safe Flex Message creation
- ✅ **JSON Export**: Export to LINE Flex Message Simulator
- ✅ **Clipboard Integration**: Automatic copy-to-clipboard functionality
- ✅ **Webhook Handling**: Complete webhook integration with FastAPI
- ✅ **Event Processing**: Message, postback, follow/unfollow event handling
- ✅ **Signature Verification**: LINE webhook signature verification for security
- ✅ **Type-Safe Events**: Pydantic models for all LINE webhook event types
- ✅ Modern Python packaging with `pyproject.toml`
- ✅ Development tools (ruff, mypy, pytest)
- ✅ Comprehensive test framework
- ✅ Async-first architecture

### 🚧 To Be Implemented

The following modules will be implemented:

- **rich_menu/**: Rich Menu management
- **login/**: LINE Login OAuth2 authentication
- **liff/**: LIFF (LINE Front-end Framework) integration
- **advanced_messaging/**: Image, video, audio message types

## 📦 Installation

### Development Setup

```bash
git clone <your-repository>
cd line-api
uv sync --dev
```

### Basic Installation

```bash
pip install -e .
```

## 🚀 Quick Start

Here's how to get started with the basic `LineAPI` class:

```python
from line_api import LineAPI

# Initialize with your credentials
line_api = LineAPI(
    channel_access_token="YOUR_CHANNEL_ACCESS_TOKEN",
    channel_secret="YOUR_CHANNEL_SECRET"
)

# Use the client in an async context
async with line_api as client:
    # Your API calls will go here
    print(f"Client ready: {client}")
```

## 🧪 Testing

Run the current test suite:

```bash
# Using the test runner
python test_runner.py

# Using pytest directly
pytest tests/

# With coverage
python test_runner.py --coverage
```

## 🔧 Development

### Setup Validation

```bash
python setup_validation.py
```

### Run Examples

```bash
python examples/basic_example.py
python comprehensive_demo.py
```

### Code Quality

```bash
# Format and lint
ruff format .
ruff check .

# Type checking
mypy line_api/
```

## 🏗️ Project Structure

```text
line-api/
├── line_api/                 # Main package
│   ├── __init__.py          # Package exports
│   ├── core/                # Core functionality
│   │   └── client.py        # Main LineAPI client
│   ├── messaging/           # Messaging API
│   ├── flex_messages/       # Flex Message components
│   ├── rich_menu/           # Rich Menu management
│   ├── login/               # LINE Login
│   └── liff/                # LIFF integration
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   └── test_core.py        # Core module tests
│
├── examples/                # Usage examples
│   └── basic_usage.py      # Basic API usage
│
├── docs/                   # Documentation
├── scripts/                # Development scripts
│
├── .github/                # GitHub configurations
├── .gitignore             # Git ignore rules
├── pyproject.toml         # Project configuration
├── README.md              # This file
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # Contribution guidelines
└── CODE_OF_CONDUCT.md    # Community guidelines
```

## 🎯 Project Goals

- **Type Safety**: Full Pydantic v2 integration with strict type checking
- **Async-First**: Built with `asyncio` for high performance
- **Developer Experience**: Excellent IDE support with complete type hints
- **Comprehensive**: Covers all major LINE platform features
- **Well-Tested**: High test coverage with property-based testing
- **Modular**: Independent components that work together seamlessly

## 🚧 Implementation Status

### ✅ Completed

- Core configuration management with Pydantic
- LINE Messaging API with async support
- Text message creation and sending
- **Flex Messages**: Complete type-safe Flex Message creation
- **JSON Export utilities**: Export to LINE Flex Message Simulator
- **Clipboard integration**: Automatic copy functionality
- **Webhook Integration**: Complete webhook handling with FastAPI
- **Event Processing**: Message, postback, follow/unfollow events
- **Signature Verification**: LINE webhook signature verification
- **Type-Safe Models**: Pydantic models for all LINE event types
- Comprehensive test infrastructure
- Development tooling setup

### 🔄 In Progress

- Advanced message types (images, videos, audio)
- Rate limiting enhancements

### 📅 Planned

- Rich Menu management
- LINE Login integration
- LIFF SDK integration

## 🤝 How to Contribute

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

1. Check the [open issues](https://github.com/yourusername/line-api-integration/issues)
2. Fork the repository and create your feature branch
3. Write tests for your changes
4. Ensure all tests pass and code is properly formatted
5. Submit a pull request with a clear description

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

### Official LINE Documentation
- [LINE Developers Portal](https://developers.line.biz/)
- [Messaging API Reference](https://developers.line.biz/en/reference/messaging-api/)
- [LINE Login Documentation](https://developers.line.biz/en/docs/line-login/)
- [LIFF Documentation](https://developers.line.biz/en/docs/liff/)
- [Flex Message Simulator](https://developers.line.biz/flex-simulator/)

### Related Projects
- [Official LINE SDK for Python](https://github.com/line/line-bot-sdk-python)
- [Unofficial LINE SDK for Python](https://github.com/line/line-bot-sdk-python)

---

Ready to build the future of LINE API integration! 🚀
