# Cortex API Server

Backend server for the Cortex Engineering Thinking Training Platform.

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB Atlas
- **Authentication**: JWT (Custom)
- **AI**: Google Gemini (gemini-2.0-flash-exp) via LangChain

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- MongoDB Atlas account
- Google Gemini API key

### 2. Installation

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the server directory:

```bash
cp .env.example .env
```

Update the `.env` file with your credentials:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=cortex
SECRET_KEY=your-secure-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
GEMINI_API_KEY=your-gemini-api-key
HOST=0.0.0.0
PORT=8000
```

### 4. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### 5. Seed Initial Data (Optional)

```bash
python seed_data.py
```

This will populate the database with:

- Sample tasks for all 4 roles
- Sample thinking drills

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Users

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Tasks

- `POST /api/tasks` - Create new task
- `GET /api/tasks` - Get all tasks (with filters)
- `GET /api/tasks/{task_id}` - Get specific task
- `GET /api/tasks/random/pick` - Get random task

### Responses

- `POST /api/responses` - Submit response to task
- `GET /api/responses/user/history` - Get user's responses
- `GET /api/responses/{response_id}` - Get specific response
- `POST /api/responses/{response_id}/feedback` - Request AI feedback (time-gated)

### Progress

- `GET /api/progress/stats` - Get user's progress statistics

### Thinking Drills

- `POST /api/drills` - Create new drill
- `GET /api/drills/random` - Get random drill
- `POST /api/drills/submit` - Submit drill answer
- `GET /api/drills/history` - Get drill submission history
- `GET /api/drills/stats` - Get drill statistics

## Project Structure

```
server/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration settings
├── database.py            # MongoDB connection
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── models/               # Database models
│   ├── user.py
│   ├── task.py
│   ├── response.py
│   ├── progress.py
│   └── drill.py
├── schemas/              # Pydantic schemas
│   ├── user.py
│   ├── task.py
│   ├── response.py
│   ├── progress.py
│   └── drill.py
├── routers/              # API route handlers
│   ├── auth.py
│   ├── users.py
│   ├── tasks.py
│   ├── responses.py
│   ├── progress.py
│   └── drills.py
└── utils/                # Utility functions
    ├── auth.py           # JWT & password handling
    ├── ai.py             # Gemini AI integration
    └── progress.py       # Streak & progress logic
```

## Features

### 1. Role-Based Tasks

- Backend Engineer
- Frontend Engineer
- Systems Engineer
- Data Engineer

Each task includes:

- Scenario description
- Guiding prompts
- Difficulty level
- Estimated time

### 2. Response Evaluation

Users submit:

- Assumptions
- Architecture description
- Trade-offs analysis
- Failure scenarios

AI evaluates on 5 dimensions:

- Clarity (0-10)
- Constraints Awareness (0-10)
- Trade-off Reasoning (0-10)
- Failure Anticipation (0-10)
- Simplicity (0-10)

### 3. Time-Gated AI Assistance

- AI feedback unlocks 5 minutes after submission
- Encourages independent thinking first
- Provides constructive feedback without solutions

### 4. Progress Tracking

- Daily streaks
- Total tasks completed
- Average scores
- Activity history

### 5. Thinking Drills

Short exercises covering:

- Spotting flawed assumptions
- Ranking failure modes
- Predicting scaling issues
- Choosing between trade-offs

## Development Notes

### AI Integration

The system uses Google Gemini for:

1. **Scoring**: Evaluates reasoning quality
2. **Feedback**: Provides constructive guidance
3. **No Solutions**: AI guides thinking, doesn't solve problems

### Time-Gating Logic

- Responses are scored immediately upon submission
- AI feedback requires 5-minute wait after submission
- Encourages reflection before seeking assistance

### Streak Calculation

- Updates automatically when tasks are completed
- Considers consecutive days of activity
- Breaks if a day is missed

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS middleware configured
- Environment variables for secrets

## Production Deployment

1. Set strong `SECRET_KEY` in production
2. Configure proper CORS origins
3. Use MongoDB Atlas production cluster
4. Enable rate limiting (not included in MVP)
5. Add admin authentication for task/drill creation
6. Set up logging and monitoring

## License

Proprietary - Cortex Platform

