# FinAgent-AI 📈

**AI-Powered Financial Analysis Platform**

FinAgent-AI is a full-stack mobile application that leverages artificial intelligence to analyze SEC 10-Q earnings reports and provide real-time investment insights. Built with React Native and FastAPI, the platform combines AI technology with financial data to help users make informed investment decisions.

## Features

-  AI-Powered Analysis**: OpenAI GPT-4 automatically analyzes complex 10-Q financial reports
-  Mobile-First Design**: Cross-platform React Native app with intuitive user interface
-  Real-Time Data**: Live stock prices and market data via Yahoo Finance API
-  Asynchronous Processing**: Background AI processing ensures fast user experience
-  Intelligent Caching**: Database caching reduces API calls and improves performance
-  Secure Authentication**: Firebase authentication with JWT token verification
-  Watchlist Management**: Track favorite stocks with real-time updates
-  Investment Insights**: AI-generated summaries of key financial metrics

## Architecture

### Frontend (Mobile App)
- **React Native** with TypeScript and Expo
- **Firebase Authentication** for user management
- **Real-time polling** for AI summary status updates

### Backend (API Server)
- **FastAPI** with Python for API requests
- **SQLAlchemy ORM** with PostgreSQL database
- **Background Tasks** for asynchronous AI processing
- **JWT Authentication** with Firebase integration

### AI Pipeline
- **OpenAI GPT-4** for natural language processing
- **SEC EDGAR API** for financial document extraction
- **Custom AI pipelines** for document analysis, extraction, and summarization
- **Intelligent caching** to prevent redundant API calls

### External Integrations
- **Yahoo Finance API** for real-time stock data
- **SEC EDGAR API** for regulatory filings
- **Firebase Authentication** for user management

## Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.11+
- PostgreSQL (or SQLite for development)
- OpenAI API key
- Firebase project
- SEC API key (sec-api.io)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FinAgent-AI/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   # Update API_BASE_URL in services/api.js to match your backend
   ```

4. **Start the development server**
   ```bash
   npx expo start
   ```

5. **Run on device/simulator**
   - Scan QR code with Expo Go app
   - Or press 'i' for iOS simulator, 'a' for Android

## 📱 Usage

### Getting Started
1. **Sign up/Login**: Use Firebase authentication to create an account
2. **Add Stocks**: Search and add stocks to your watchlist
3. **View Details**: Tap on any stock to see real-time data and AI analysis
4. **AI Insights**: Wait for AI-generated summary of the latest 10-Q filing

### Features Walkthrough
- **Dashboard**: View your watchlist with real-time price updates
- **Stock Details**: See price, market cap, P/E ratio, and AI summary
- **AI Analysis**: Automatically generated insights from SEC filings
- **Real-time Updates**: Live data and polling for AI summary status

## 🔧 Configuration

### Environment Variables (Backend)
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# SEC API Configuration
SEC_API_KEY=your_sec_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/finagent

# Firebase Configuration
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
```

### Environment Variables (Frontend)
```javascript
// services/api.js
const API_BASE_URL = "http://your-backend-url:8000";
```

## 🏛️ Project Structure

```
FinAgent-AI/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models.py         # Database models
│   │   └── database.py       # Database configuration
│   ├── requirements.txt      # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── app/                 # React Native screens
│   ├── services/            # API service layer
│   ├── components/          # Reusable components
│   └── package.json         # Node.js dependencies
└── README.md
```

## 🔍 API Endpoints

### Authentication Required
- `GET /stock/{ticker}` - Get stock details and AI summary
- `POST /summary-by-ticker` - Trigger AI summary generation
- `GET /stock-prices` - Batch fetch stock prices

## AI Processing Pipeline

1. **Document Fetching**: Retrieve latest 10-Q filing from SEC EDGAR
2. **Section Extraction**: Extract key sections (Management Discussion, Risk Factors, etc.)
3. **Text Processing**: Clean and concatenate extracted text
4. **AI Analysis**: Send to OpenAI GPT-4 with custom prompts
5. **Caching**: Store results in database for future requests
6. **Real-time Updates**: Frontend polls for completion status

## Performance Optimizations

- **Asynchronous Processing**: Background tasks prevent UI blocking
- **Database Caching**: Reduces redundant AI API calls
- **Intelligent Polling**: Efficient status checking for AI completion
- **Error Handling**: Graceful degradation when APIs fail
- **Connection Pooling**: Optimized database connections

### Database Management
```bash
# Clear error entries
python clear_summary_error.py TICKER

# Reset database
python init_db.py
```

## 🚀 Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t finagent-backend .
docker run -p 8000:8000 finagent-backend

# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
# Build for production
npx expo build:android
npx expo build:ios

# Or use EAS Build
eas build --platform all
```

## Acknowledgments

- **OpenAI** for GPT-4 API access
- **SEC EDGAR** for financial data
- **Yahoo Finance** for market data
- **Firebase** for authentication services
- **React Native** and **FastAPI** communities

**Built using React Native, FastAPI, Firebase, PostgreSQL, and OpenAI GPT-4**
