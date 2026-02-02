
# LegalEase

## LLM-Orchestrated Legal Intelligence System

An AI-powered platform that demystifies complex legal documents by providing clear, accessible summaries and explanations using Google Cloud's generative AI technologies.

### Demo - https://lexi-simplify-822987556610.us-central1.run.app/
## Features

- **Document Upload**: Upload PDF legal documents for analysis
- **AI Analysis**: Get plain English summaries and key clause explanations
- **Q&A Interface**: Ask specific questions about your documents
- **Risk Flagging**: Identify potentially concerning clauses
- **Secure Processing**: Documents are processed securely and can be deleted after analysis

## Technology Stack

- **Frontend**: React with TypeScript, Material-UI
- **Backend**: Python Flask with Google Cloud AI integration
- **AI Services**: Google Cloud Vertex AI / Gemini API
- **Deployment**: Docker containers on Google Cloud Run

## Project Structure

```
lexi-simplify/
├── frontend/           # React TypeScript frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/            # Python Flask backend
│   ├── app.py
│   ├── services/
│   └── requirements.txt
├── Dockerfile          # Multi-stage Docker build
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Cloud Project with Vertex AI API enabled
- Docker (for deployment)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lexi-simplify
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your Google Cloud credentials
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Run development servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

### Google Cloud Setup

1. Create a Google Cloud Project
2. Enable the Vertex AI API
3. Create a service account with Vertex AI permissions
4. Download the service account key JSON file
5. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### Deployment

The application is containerized and ready for Google Cloud Run deployment:

```bash
# Build and deploy to Google Cloud Run
gcloud run deploy lexi-simplify \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Usage

1. Visit the web application
2. Upload a PDF legal document
3. Review the AI-generated summary and key points
4. Ask specific questions about the document
5. Review any flagged concerning clauses

## Security & Privacy

- All documents are processed securely over HTTPS
- Documents can be deleted after analysis
- No persistent storage of sensitive information
- Clear disclaimers about informational purposes

## Contributing

This is a prototype application. For production use, additional security measures, testing, and features should be implemented.

## License


This project is for educational and demonstration purposes.




