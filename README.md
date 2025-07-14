# MealMate - Smart Meal Logging & Nutrition Tracker

A full-stack web application for meal logging, nutrition tracking, and AI-powered dietary suggestions.

## 📃 Project Overview

MealMate allows users to log their meals, track calorie intake, record audio notes, and receive AI-generated dietary suggestions with a clean, responsive dashboard to visualize nutritional data.

## ⚙️ Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS + Chart.js
- **Backend**: Python (Flask) + SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **External APIs**: Azure OpenAI for dietary tips
- **Real-Time Updates**: Flask-SocketIO
- **Deployment**: Render (backend) & Vercel (frontend)

## 📦 Core Features

### 🔐 User Authentication
- JWT-based registration and login
- User profiles with calorie goals and health info

### 🍽️ Meal Logging
- Log meals with name, category, quantity, and calories
- View, edit, delete meals linked to user accounts

### 📊 Dashboard
- Daily calorie summary
- Bar & pie charts for calorie/macronutrient breakdown
- Meal history and trends

### 🤖 AI Suggestions
- Azure OpenAI integration for dietary feedback
- Personalized recommendations based on meal history

### 🎙️ Audio Notes
- Record voice notes for meals
- Store and playback notes via backend

### 👨‍💼 Admin Panel
- Manage food categories
- View user activity and meal analytics
- Role-based access control

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL 12+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/mealmate
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint
```

Initialize the database:

```bash
flask db upgrade
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
mealmate/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   └── package.json
└── README.md
```

## 🔧 Environment Variables

Create `.env` files in both backend and frontend directories:

### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/mealmate
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint
```

### Frontend (.env)
```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

## 🚀 Deployment

### Backend (Render)
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy with automatic builds

### Frontend (Vercel)
1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set environment variables
4. Deploy with automatic builds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.