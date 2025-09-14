# Milo AI - Yale Career Assistant

A FastAPI-based career guidance application that helps Yale students plan their career paths using AI and real alumni data.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables
Create a `.env` file in the project root with your OpenAI API key:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

Replace `your_actual_api_key_here` with your actual OpenAI API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 3. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:8000`

## Features

- AI-powered career analysis using OpenAI GPT
- Real Yale alumni data integration
- Personalized action plans
- Success probability calculations
- Modern web interface

## API Endpoints

- `GET /` - Serves the main web interface
- `POST /analyze` - Analyzes career goals and returns actionable plan

## Security Note

Never commit your `.env` file to version control. The `.env` file contains sensitive API keys.
