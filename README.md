# LINE API Integration Library

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A comprehensive, type-safe Python library for integrating with LINE's APIs. Built with modern async/await patterns, full Pydantic type safety, and designed for production use.

## 🚀 Features

- 🚀 **Push Messages**: Send messages directly to users
- 📱 **Multiple Message Types**: Text, images, locations, stickers, and Flex messages
- 🔒 **Type Safety**: Full Pydantic integration with comprehensive type hints
- ⚡ **Async-First**: Built for high-performance async/await operations
- 🛡️ **Error Handling**: Comprehensive error handling with typed exceptions
- 🔄 **Retry Logic**: Built-in retry mechanisms with exponential backoff
- 📊 **Rate Limiting**: Automatic rate limit handling

## 🛠 Installation

```bash
# Using pip
pip install line-api-integration

# Using uv
uv pip install line-api-integration
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

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### ✅ What's Working

- ✅ Basic project structure
- ✅ Modern Python packaging with `pyproject.toml`
- ✅ Development tools (ruff, mypy, pytest)
- ✅ Clean `LineAPI` class foundation
- ✅ Test framework setup

### 🚧 To Be Implemented

The following modules will be implemented one by one:

- **core/**: Configuration management and HTTP client
- **messaging/**: LINE Messaging API integration
- **flex_messages/**: Flex Message builder with type safety
- **rich_menu/**: Rich Menu management
- **login/**: LINE Login OAuth2 authentication
- **liff/**: LIFF (LINE Front-end Framework) integration

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

- Basic project structure
- Core HTTP client with async support
- Initial test infrastructure
- Development tooling setup

### 🔄 In Progress

- Messaging API implementation
- Request/response models
- Error handling system

### 📅 Planned

- Flex Message builders
- Rich Menu management
- LINE Login integration
- LIFF SDK
- Webhook signature verification
- Rate limiting and retry mechanisms

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
