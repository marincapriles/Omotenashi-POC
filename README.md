# 🏨 Omotenashi Hotel Concierge

A sophisticated AI-powered hotel concierge system built with FastAPI and LangChain, providing personalized guest services through natural language interactions.

## Features

- 🤖 **AI-Powered Concierge**: Intelligent assistant using OpenAI's GPT models
- 👤 **Guest-Specific Context**: Personalized responses based on guest profiles and bookings
- 🛠️ **Service Tools**: Room cleaning, checkout modifications, transport requests
- 💬 **Conversation Memory**: Maintains chat history per guest session
- 🌐 **Modern Web Interface**: Clean, responsive frontend for guest interactions
- 📚 **Property Knowledge Base**: Vector-based information retrieval about hotel amenities

## Architecture

### Backend Services

- **VectorStoreService**: Manages property information using Chroma vector database
- **GuestService**: Handles guest profiles and booking data
- **MemoryService**: Manages conversation history with automatic cleanup

### Available Tools

- `schedule_cleaning`: Schedule room cleaning services
- `modify_checkout_time`: Change guest checkout times
- `request_transport`: Arrange airport transportation
- `guest_profile`: Retrieve guest information and preferences
- `booking_details`: Access reservation details
- `property_info`: Query hotel amenities and services

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and setup environment**:

```bash
git clone <repository-url>
cd omotenashi-poc
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure environment**:
   Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
MEMORY_EXPIRY_HOURS=1
PORT=8000
```

4. **Run the application**:

```bash
python main.py
```

The application will be available at http://localhost:8000

## API Endpoints

| Method   | Endpoint             | Description                 |
| -------- | -------------------- | --------------------------- |
| `GET`    | `/`                  | Serve frontend application  |
| `GET`    | `/guest_profile/all` | Get all guest profiles      |
| `POST`   | `/message`           | Send message to concierge   |
| `GET`    | `/session/{phone}`   | Get conversation history    |
| `DELETE` | `/session/{phone}`   | Delete conversation session |

## Data Structure

### Guest Profile

```json
{
  "guest_id": "G001",
  "name": "Carlos Marin",
  "phone_number": "+14155550123",
  "preferred_language": "English",
  "vip_status": true
}
```

### Booking Details

```json
{
  "booking_id": "B001",
  "guest_id": "G001",
  "property_id": "villa_azul",
  "check_in_date": "2024-01-15",
  "check_out_date": "2024-01-18",
  "room_type": "Deluxe Suite"
}
```

## Development

### Project Structure

```
omotenashi-poc/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── prompts.py           # System prompts and templates
├── guests.json          # Guest profile data
├── bookings.json        # Booking information
├── villa_azul.txt       # Property information
├── static/
│   └── index.html       # Frontend interface
├── chroma_db/           # Vector database storage
└── requirements.txt     # Python dependencies
```

### Key Components

**Service Classes**:

- Clean separation of concerns
- Lazy loading for performance
- Comprehensive error handling

**Tool System**:

- Guest-specific tool injection
- Automatic context retrieval
- Simplified function signatures

**Prompt Management**:

- Centralized prompt templates
- Dynamic guest context injection
- Extensible tool descriptions

### Adding New Tools

1. Define the tool function in `create_guest_tools()`
2. Add description to `TOOL_DESCRIPTIONS` in `prompts.py`
3. The tool will automatically have access to guest context

## Configuration

Environment variables:

- `OPENAI_API_KEY`: Required OpenAI API key
- `OPENAI_MODEL`: GPT model to use (default: gpt-3.5-turbo)
- `MEMORY_EXPIRY_HOURS`: Session timeout (default: 1 hour)
- `PORT`: Server port (default: 8000)

## Deployment

For production deployment:

1. Set appropriate CORS origins in `main.py`
2. Use a production WSGI server like Gunicorn
3. Configure proper logging levels
4. Set up monitoring and health checks

## License

This project is a proof of concept for demonstration purposes.
