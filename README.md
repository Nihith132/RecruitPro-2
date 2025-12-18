# RecruitPro 2 - AI-Powered Recruitment Management System

An intelligent recruitment management platform powered by AI for resume parsing, candidate-JD matching, and recruitment analytics.

## 🚀 Features

- **AI-Powered Resume Parsing**: Automatically extract structured data from PDF/DOCX resumes
- **Smart Job Description Analysis**: Parse and understand JD requirements
- **Intelligent Matching**: AI-driven candidate scoring with multi-category analysis:
  - Skills (50% weight)
  - Experience (30% weight)
  - Education (15% weight)
  - Certifications (5% weight)
- **AI Chat Assistant**: Natural language queries for candidate search and insights
- **Dashboard Analytics**: Visual recruitment pipeline statistics
- **Bulk Operations**: Upload, delete, and export multiple candidates/JDs
- **Dark/Light Mode**: Modern UI with theme support
- **Export Functionality**: CSV and PDF exports

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB Atlas with GridFS
- **AI**: Groq Llama 3.3 70B Versatile
- **Auth**: Firebase Authentication
- **File Processing**: PyPDF2, python-docx

### Frontend
- **Framework**: React 19
- **UI Library**: Material-UI v7
- **Animation**: Framer Motion
- **Build Tool**: Vite 6.4.1

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB Atlas account
- Groq API key ([Get free key](https://console.groq.com/))
- Firebase project ([Create project](https://console.firebase.google.com/))

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd recruit-pro-2
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

**Edit `backend/.env` with your credentials:**

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/recruitpro?retryWrites=true&w=majority
DATABASE_NAME=recruitpro

# Groq AI
GROQ_API_KEY=your_groq_api_key_here

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-adminsdk.json

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Get Firebase Admin SDK:**
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save the JSON file and update the path in `.env`

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file if needed
echo "VITE_API_URL=http://localhost:8000" > .env
```

## 🚀 Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run at: **http://localhost:5173**

## 📁 Project Structure

```
recruit-pro-2/
├── backend/
│   ├── database/
│   │   └── mongodb.py          # MongoDB connection & GridFS
│   ├── llmservices/
│   │   ├── parser_llm.py       # Resume & JD parsing
│   │   ├── topscore_gemini.py  # AI matching & scoring
│   │   └── chat_llm.py         # Chat assistant
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── routes/
│   │   ├── candidates.py       # Candidate endpoints
│   │   ├── job_descriptions.py # JD endpoints
│   │   ├── matching.py         # Matching endpoints
│   │   ├── analytics.py        # Dashboard analytics
│   │   ├── chat.py             # Chat endpoints
│   │   └── auth.py             # Firebase auth
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx   # Analytics dashboard
│   │   │   ├── Candidates.jsx  # Candidate management
│   │   │   ├── JobDescriptions.jsx
│   │   │   └── TopMatches.jsx  # Match results
│   │   ├── components/         # Reusable components
│   │   ├── context/
│   │   │   └── ThemeContext.jsx
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎯 Usage Guide

### 1. Upload Candidates
- Navigate to "Candidates" page
- Click "Upload Resume"
- Select PDF or DOCX files
- AI automatically parses and extracts data

### 2. Upload Job Descriptions
- Navigate to "Job Descriptions" page
- Click "Upload JD"
- AI parses requirements and auto-matches with candidates

### 3. View Top Matches
- Navigate to "Top Matches" page
- Select a JD to see ranked candidates
- View detailed score breakdowns:
  - Skills matched vs missing
  - Experience analysis
  - Education fit
  - Certification relevance

### 4. Use AI Chat
- Click chat icon in sidebar
- Ask natural language queries:
  - "Who knows Python?"
  - "Show me top matches"
  - "What is John's score?"
  - "Compare all candidates"

### 5. Export Data
- Use export buttons for CSV/PDF downloads
- Bulk operations for multiple selections

## 🔒 Security Notes

- **Never commit `.env` files** - They contain sensitive credentials
- **Firebase credentials** - Keep JSON file secure, use environment variable for path
- **MongoDB URI** - Use strong passwords and IP whitelisting
- **CORS Origins** - Update for production domains

## 🧪 Testing

### Backend Testing (Coming Soon)
```bash
cd backend
pytest tests/
```

### Frontend Testing (Coming Soon)
```bash
cd frontend
npm test
```

## 📊 AI Scoring Methodology

The system uses a weighted scoring approach:

1. **Skills (50%)**: Semantic matching with synonyms and hierarchies
2. **Experience (30%)**: Years + relevance to role
3. **Education (15%)**: Degree relevance and GPA
4. **Certifications (5%)**: Industry certifications

**Bias Mitigation**: AI avoids discriminatory factors (age, gender, ethnicity, religion)

## 🌐 Deployment

### Backend Deployment (AWS/GCP/Azure)
1. Set production environment variables
2. Update CORS origins
3. Use production MongoDB cluster
4. Deploy with Gunicorn/Uvicorn

### Frontend Deployment (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **Nihith Reddy Arramareddy** - Initial work

## 🙏 Acknowledgments

- Groq for fast Llama inference
- MongoDB Atlas for database hosting
- Firebase for authentication
- Material-UI for UI components

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using AI**
