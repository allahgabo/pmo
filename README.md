# PMO AI Assistant

> **Enterprise-Grade Project Management Office System with AI Integration**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com)

A complete, production-ready PMO system built with Django, featuring **multi-user authentication**, **role-based access control**, **AI-powered analysis**, and comprehensive project portfolio management.

---

## ✨ Features

### 🔐 Authentication & Authorization
- Multi-user authentication with secure login/logout
- 4 user roles with granular permissions (Admin, PMO Director, Project Manager, Team Member)
- Self-service registration
- Activity logging for all actions
- Session management with CSRF protection

### 📊 Project Management
- 8 sample projects with realistic data
- Project health scoring algorithm
- SPI/CPI performance tracking
- Budget variance analysis
- 30 risks with severity tracking
- 65 tasks with assignments
- 83 resources with roles
- 36 milestones

### 🎨 User Interface
- 7 complete web pages (Login, Register, Dashboard, Projects, Project Detail, Tasks, Profile)
- Responsive design - works on all devices
- Modern UI with Tailwind CSS
- Interactive charts with Chart.js
- Dynamic filtering and search

### 🤖 AI Integration
- Claude AI powered analysis
- Project summaries with insights
- Portfolio-level reporting
- Risk analysis with recommendations
- Q&A functionality
- Demo mode included (no API key required)

### 🔌 REST API
- 30+ endpoints with full CRUD
- Interactive documentation (Swagger UI)
- Token authentication
- Filtering and pagination

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- 4GB RAM
- 500MB disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pmo-ai-assistant.git
cd pmo-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Load sample data (optional)
python populate_data.py

# Collect static files
python manage.py collectstatic --noinput

# Start server
python manage.py runserver
```

**Access:** http://localhost:8000

**Login:** Use the credentials you created

---

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - 3-step getting started
- **[Authentication Guide](AUTHENTICATION_GUIDE.md)** - User system details
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete feature list
- **[Visual Demo](VISUAL_DEMO.html)** - Interactive walkthrough

---

## 🏗️ Project Structure

```
pmo-ai-assistant/
├── accounts/              # Authentication & user profiles
├── ai_engine/             # AI integration
├── analytics/             # Reporting
├── projects/              # Core project management
├── pmo_core/             # Django settings
├── templates/            # HTML pages
├── static/               # CSS, JS, images
├── manage.py             # Django CLI
└── requirements.txt      # Dependencies
```

---

## 👥 User Roles

| Role | Access | Capabilities |
|------|--------|--------------|
| **Administrator** | Full | All operations, admin panel, AI |
| **PMO Director** | Portfolio | All projects, analytics, reporting |
| **Project Manager** | Projects | Assigned projects, monitoring |
| **Team Member** | Tasks | Assigned tasks, updates |

---

## 🎯 Usage

### Web Interface
```
1. Login at http://localhost:8000/login/
2. Explore Dashboard
3. View Projects
4. Manage Tasks
5. Check Profile
```

### API
```bash
# Get dashboard stats
curl http://localhost:8000/api/projects/dashboard_stats/

# Get AI summary
curl http://localhost:8000/api/ai/portfolio-summary/

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 🔧 Configuration

### Environment Variables
Create `.env`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
ANTHROPIC_API_KEY=your-api-key  # Optional
```

### Database
Default: SQLite

Production (PostgreSQL):
```python
# In pmo_core/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pmo_db',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📦 Tech Stack

**Backend:**
- Django 5.0
- Django REST Framework 3.14
- SQLite/PostgreSQL
- Anthropic Claude AI

**Frontend:**
- Tailwind CSS 2.2
- Chart.js 3.9
- Font Awesome 6.0
- Vanilla JavaScript

---

## 🚀 Deployment

### Heroku
```bash
heroku create your-app
git push heroku main
heroku run python manage.py migrate
```

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/Feature`)
3. Commit changes (`git commit -m 'Add Feature'`)
4. Push to branch (`git push origin feature/Feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/pmo-ai-assistant/issues)
- **API Docs:** http://localhost:8000/api/docs/

---

## 🔄 Changelog

### v2.0 (2025-12-18)
- ✅ Multi-user authentication
- ✅ Role-based access control
- ✅ 7 web pages
- ✅ Activity logging
- ✅ Responsive UI
- ✅ Enhanced API
- ✅ AI integration

---

## ⭐ Star this repo if you find it useful!

**Built with ❤️ using Django & Claude AI**
