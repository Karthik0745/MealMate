# MealMate - Smart Meal Logging and Nutrition Tracker

A comprehensive full-stack web application for smart meal logging and nutrition tracking with AI-powered dietary suggestions, real-time updates, and comprehensive analytics.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure JWT-based authentication with user profiles
- **Meal Logging**: Comprehensive meal tracking with nutritional data
- **Dashboard Analytics**: Interactive charts and nutrition insights
- **AI Dietary Suggestions**: Personalized recommendations using Azure OpenAI
- **Audio Notes**: Voice recordings for meal notes
- **Real-time Updates**: Live data synchronization with WebSocket
- **Admin Panel**: User and category management
- **Responsive Design**: Mobile-first, modern UI

### Advanced Features
- **BMR/TDEE Calculations**: Automatic metabolic rate calculations
- **Macro Tracking**: Detailed protein, carbs, and fat tracking
- **Goal Progress**: Visual progress tracking toward nutrition goals
- **Category Management**: Color-coded meal categories
- **Pagination & Search**: Efficient data browsing
- **Audio Recording**: Browser-based voice note recording
- **Chart Visualizations**: Interactive nutrition charts
- **Role-based Access**: Admin and user roles

## 🏗️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Real-time**: Flask-SocketIO for WebSocket connections
- **AI Integration**: Azure OpenAI API
- **File Handling**: Audio file upload and management
- **API Documentation**: RESTful API design

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Chart.js with react-chartjs-2
- **Forms**: React Hook Form with validation
- **State Management**: React Context + useReducer
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **UI Components**: Custom component library
- **Notifications**: React Hot Toast

### Development & Deployment
- **Package Management**: npm (frontend), pip (backend)
- **Build Tools**: Create React App, Webpack
- **Environment**: Environment variables configuration
- **Deployment**: Render (backend) + Vercel (frontend)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Azure OpenAI API access (optional)

### Backend Setup

1. **Clone and navigate to backend directory**
```bash
git clone <repository-url>
cd backend
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

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
# Create PostgreSQL database
createdb mealmate

# Initialize database
python init_db.py
```

6. **Run the application**
```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment configuration**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Start development server**
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

## 📁 Project Structure

### Backend Structure
```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── init_db.py           # Database initialization
├── requirements.txt      # Python dependencies
├── models/
│   ├── __init__.py
│   ├── user.py          # User model with BMR/TDEE calculations
│   ├── meal.py          # Meal model with nutrition data
│   ├── category.py      # Category model
│   └── audio_note.py    # Audio note model
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── meals.py         # Meal CRUD operations
│   ├── dashboard.py     # Analytics and dashboard data
│   ├── ai.py           # AI-powered suggestions
│   ├── admin.py        # Admin management
│   └── audio.py        # Audio file handling
├── services/
│   ├── __init__.py
│   ├── ai_service.py   # Azure OpenAI integration
│   └── utils.py        # Helper functions
└── uploads/            # Audio file storage
```

### Frontend Structure
```
frontend/
├── public/
│   ├── index.html      # Main HTML file
│   └── manifest.json   # PWA manifest
├── src/
│   ├── App.tsx         # Main application component
│   ├── index.tsx       # Entry point
│   ├── index.css       # Global styles
│   ├── components/
│   │   ├── common/     # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── layout/     # Layout components
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── charts/     # Chart components
│   │   │   └── DailyCaloriesChart.tsx
│   │   └── audio/      # Audio recording
│   │       └── AudioRecorder.tsx
│   ├── pages/          # Main application pages
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── MealsPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── AdminPage.tsx
│   ├── contexts/       # React contexts
│   │   └── AuthContext.tsx
│   ├── hooks/          # Custom hooks
│   │   └── useSocket.ts
│   ├── services/       # API services
│   │   ├── api.ts      # Base API service
│   │   ├── auth.ts     # Authentication service
│   │   ├── meals.ts    # Meals service
│   │   ├── dashboard.ts # Dashboard service
│   │   └── admin.ts    # Admin service
│   ├── types/          # TypeScript definitions
│   │   └── index.ts
│   └── utils/          # Utility functions
├── package.json        # Dependencies and scripts
├── tailwind.config.js  # Tailwind configuration
└── tsconfig.json       # TypeScript configuration
```

## 🔧 Configuration

### Backend Environment Variables
```env
# Database
DATABASE_URL=postgresql://username:password@localhost/mealmate

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Frontend Environment Variables
```env
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_SOCKET_URL=http://localhost:5000
REACT_APP_VERSION=1.0.0
```

## � Database Schema

### Key Models

**User Model**
- Authentication and profile data
- BMR/TDEE calculations
- Activity level and goals
- Admin role management

**Meal Model**
- Comprehensive nutritional data
- Category relationships
- Macronutrient percentages
- Timestamp tracking

**Category Model**
- Color-coded organization
- Meal count tracking
- Admin management

**Audio Note Model**
- File metadata
- Meal associations
- Duration and size tracking

## 🎨 UI/UX Features

### Design System
- **Colors**: Primary brand colors with semantic variants
- **Typography**: Inter font with consistent hierarchy
- **Components**: Reusable design components
- **Responsive**: Mobile-first responsive design
- **Accessibility**: WCAG compliant design patterns

### Interactive Elements
- **Charts**: Interactive nutrition visualizations
- **Forms**: Real-time validation and feedback
- **Navigation**: Intuitive sidebar navigation
- **Modals**: Contextual action dialogs
- **Toast Notifications**: User feedback system

## 🤖 AI Integration

### Azure OpenAI Features
- **Dietary Analysis**: Meal nutrition analysis
- **Personalized Suggestions**: Based on user goals
- **Food Recommendations**: Smart meal suggestions
- **Nutrition Insights**: AI-powered health insights

### Implementation
- Secure API integration
- Error handling and fallbacks
- Rate limiting protection
- Privacy-focused data handling

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- Secure password hashing (bcrypt)
- Token refresh mechanism
- Role-based access control

### Data Protection
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Input validation and sanitization
- File upload security

## 📱 Real-time Features

### WebSocket Integration
- Live meal updates
- Real-time dashboard refresh
- User activity notifications
- Automatic data synchronization

## 🔧 Development

### Available Scripts

**Backend**
```bash
python app.py          # Start development server
python init_db.py      # Initialize database
pip install -r requirements.txt  # Install dependencies
```

**Frontend**
```bash
npm start             # Start development server
npm build             # Build for production
npm test              # Run tests
npm run lint          # Lint code
```

### Code Quality
- **TypeScript**: Type-safe development
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Component Documentation**: Comprehensive commenting

## 🚀 Deployment

### Backend Deployment (Render)
1. Connect GitHub repository
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

### Frontend Deployment (Vercel)
1. Connect GitHub repository
2. Configure environment variables
3. Build command: `npm run build`
4. Output directory: `build`

## 🧪 Testing

### Test Coverage
- Unit tests for utility functions
- Integration tests for API endpoints
- Component testing for React components
- End-to-end testing scenarios

## 📈 Performance

### Optimization Features
- **Database**: Indexed queries and relationship optimization
- **Frontend**: Code splitting and lazy loading
- **API**: Efficient pagination and filtering
- **Caching**: Strategic data caching
- **Bundle**: Optimized production builds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For support, email support@mealmate.app or create an issue on GitHub.

## 🗺️ Roadmap

### Upcoming Features
- Mobile app (React Native)
- Barcode scanning
- Recipe import
- Social features
- Wearable device integration
- Advanced AI recommendations

---

**MealMate** - Making nutrition tracking smart, simple, and effective! 🍎📊