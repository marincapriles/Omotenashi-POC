# Omotenashi POC

A FastAPI-based API project with OpenAI integration.

## Setup

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

- Copy `.env.example` to `.env`
- Add your OpenAI API key to `.env`

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

- Main API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API Documentation: http://localhost:8000/redoc

## API Endpoints

- `GET /`: Root endpoint with welcome message
- `GET /health`: Health check endpoint

## Development

- The project uses FastAPI for the API framework
- OpenAI integration is configured through environment variables
- CORS is enabled for development (configure appropriately for production)
