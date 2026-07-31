# AI Learning Agent Application

## Overview

This is an AI-powered learning application that helps students study course materials through an interactive interface. The application features:

- A lesson navigation panel
- A PDF viewer for course materials
- An AI tutor chatbot that can answer questions about the lesson content
- Backend services powered by a ecosystem of specialized tools for knowledge retrieval, conversation memory, quiz generation, and more

## Prerequisites

- Node.js (v18+ recommended)
- Python (v3.8+ recommended)
- Git
- OpenRouter API key (for the AI tutor)

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Backend Setup
```bash
# Navigate to the backend directory
cd test

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_key_here
```

### 3. Frontend Setup
```bash
# Navigate to the frontend directory
cd ../frontend

# Install dependencies
npm install
```

### 4. Environment Variables
The backend requires a `.env` file in the `test` directory with at least:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

The frontend does not require any environment variables for development.

## Running the Application

### Start the Backend
```bash
# From the project root (test directory)
python server.py
```
The backend will start on `http://localhost:8000`

### Start the Frontend
```bash
# From the frontend directory
npm run dev
```
The frontend will start on `http://localhost:5178`

### Access the Application
Open your browser and navigate to `http://localhost:5178`

## Project Structure

```
├── test/                 # Backend (FastAPI)
│   ├── agents/           # AI agent implementations
│   ├── tools/            # Specialized tools for the agents
│   ├── providers/        # LLM providers (OpenRouter)
│   ├── server.py         # Main FastAPI application
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Frontend (React + Vite + TypeScript)
│   ├── src/              # Source code
│   │   ├── App.tsx       # Main application component
│   │   ├── components/   # Reusable components
│   │   └── services/     # API service layer
│   ├── public/           # Static assets (PDF files)
│   ├── package.json      # Node.js dependencies and scripts
│   └── tsconfig.json     # TypeScript configuration
│
└── README.md             # This file
```

## Features Implemented

### Frontend
- Reactive lesson navigation panel
- Integrated PDF viewer using `@react-pdf-viewer`
- AI tutor chat interface with message display and input
- Responsive layout with three panels (lessons, PDF, chat)
- Custom navigation controls for the PDF viewer

### Backend
- RESTful API endpoints for chat, lessons, and health checks
- Modular agent system with tool registry
- Specialized tools for:
  - Course knowledge retrieval
  - Conversation memory
  - Quiz generation
  - Learning state tracking
  - Content rewriting
  - Speech-to-text/text-to-speech
  - Recommendations
  - External learning resources
- OpenRouter AI integration for the tutor

## Known Limitations

1. **PDF Page Synchronization**: The custom "Previous" and "Next" buttons update the displayed page number but do not actually change the page in the PDF viewer. The PDF viewer has its own navigation controls (which are hidden). A future improvement would be to connect the viewer's API to synchronize the page state.

2. **AI Tutor Functionality**: The AI tutor currently returns a placeholder response. The backend chat endpoint is implemented and connected, but the actual AI responses depend on the OpenRouter API key and the agent configuration.

3. **Lesson Data**: Currently, lessons are hardcoded in `frontend/src/App.tsx`. In a production implementation, these would be fetched from the backend API.

## Future Enhancements

- Connect PDF viewer API to synchronize page numbers with state
- Implement actual AI responses using the configured agent and tools
- Fetch lesson list from backend API instead of hardcoding
- Add authentication and user persistence
- Implement quiz functionality and learning progress tracking
- Add file upload for external learning materials
- Enhance UI with loading states, error handling, and animations

## Troubleshooting

### Backend Issues
- **Module not found errors**: Ensure you're running from the `test` directory and have activated the virtual environment
- **OpenRouter API errors**: Verify your API key is correct and has sufficient credits
- **Port already in use**: Another process is using port 8000. Change the port in `server.py` or stop the conflicting process

### Frontend Issues
- **Dependency errors**: Try deleting `node_modules` and `package-lock.json` then run `npm install` again
- **Port already in use**: Another process is using port 5178. Change the port in `vite.config.js` or stop the conflicting process
- **PDF not loading**: Ensure the PDF files are in the `frontend/public` directory and the filenames match those in `App.tsx`

## License

This project is licensed under the MIT License.

## Acknowledgments

- [React PDF Viewer](https://react-pdf-viewer.dev/) for the PDF viewing component
- [OpenRouter](https://openrouter.ai/) for providing access to various LLMs
- The open-source community for the various libraries used in this project