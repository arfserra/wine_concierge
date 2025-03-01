# Wine Concierge

A web application for wine enthusiasts to manage their collection with precise location tracking and receive AI-powered pairing recommendations based on wines they currently own.

## Features

- Storage configuration for wine collections
- Wine label scanning and identification
- Position tracking for each wine
- AI-powered wine pairing recommendations
- Food image analysis for pairing suggestions

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update with your settings
6. Run the application: `uvicorn app.main:app --reload`

## API Documentation

Once running, visit <http://localhost:8000/docs> for interactive API documentation.
