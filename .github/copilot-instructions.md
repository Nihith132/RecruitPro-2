# RecruitPro 2 - Copilot Instructions

This is an AI-powered recruitment management system built with:

## Tech Stack
- **Backend**: FastAPI (Python 3.11+) with MongoDB
- **Frontend**: React 19 with Material-UI v7
- **AI**: Google Gemini 2.0 Flash API
- **Database**: MongoDB with GridFS for file storage
- **Auth**: Firebase Authentication

## Key Features
1. AI-powered resume and job description parsing
2. Intelligent candidate-JD matching with semantic skills analysis
3. Multi-category scoring system (Skills, Experience, Education, Certifications)
4. Dashboard with recruitment analytics
5. Bulk operations (upload, delete, export)
6. Dark/Light mode theme support
7. Export functionality (CSV, PDF)

## Project Structure
- `backend/` - FastAPI application
  - `llmservices/` - Enhanced AI prompts with bias mitigation and semantic matching
  - `routes/` - API endpoints including bulk operations
  - `database/` - MongoDB connection and GridFS handlers
  - `models/` - Pydantic data models
- `frontend/` - React application
  - `pages/` - Dashboard, Candidates, JDs, TopMatches
  - `components/` - Reusable UI components
  - `context/` - Theme and state management

## Coding Guidelines
- Use type hints in Python code
- Follow RESTful API conventions
- Implement proper error handling with user-friendly messages
- Use Material-UI components for consistent UI
- Keep AI prompts well-structured with clear instructions
- Implement bias mitigation in AI scoring
- Use semantic skills matching (synonyms, hierarchies, clusters)
