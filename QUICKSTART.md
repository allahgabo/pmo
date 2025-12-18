# PMO AI Assistant - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Server
```bash
cd /home/claude/pmo-ai-assistant
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Access the Application
Open your browser and go to:
- **Main App**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

### Step 3: Login
```
Username: admin
Password: admin123
```

## 📊 What You'll See

### Dashboard (Home Page)
- **Portfolio Statistics**: Total projects, status distribution
- **Performance Metrics**: Average SPI, CPI, completion rates
- **Visual Charts**: Status distribution and performance indicators
- **At-Risk Projects**: Projects requiring immediate attention

### Projects Section
- **Project Grid**: All projects with health scores
- **Filters**: Search by status, priority, or name
- **Project Details**: Click any project for detailed information
- **AI Analysis**: Get AI-powered insights for any project

### AI Assistant Section
- **Quick Actions**: 
  - Portfolio Summary
  - Executive Report
  - Risk Analysis
- **Ask Questions**: Natural language queries about your projects
- **Intelligent Responses**: AI-powered insights and recommendations

## 🎯 Sample Data Included

The system comes with 8 pre-loaded projects:
1. **Alpha CRM** - At Risk (58% complete, SPI: 0.86)
2. **Beta Mobile App** - On Track (75% complete, SPI: 1.05)
3. **Gamma Data Warehouse** - Delayed (42% complete, SPI: 0.75)
4. **Delta API Gateway** - On Track (85% complete, SPI: 1.12)
5. **Epsilon Security** - At Risk (35% complete, SPI: 0.82)
6. **Zeta Cloud Migration** - On Track (65% complete, SPI: 0.98)
7. **Eta Analytics** - On Track (90% complete, SPI: 1.15)
8. **Theta Customer Portal** - Delayed (48% complete, SPI: 0.78)

Plus: 30 risks, 65 tasks, 83 resources, and 36 milestones

## 🔧 API Testing

### Using cURL

```bash
# Get dashboard statistics
curl http://localhost:8000/api/projects/dashboard_stats/ | jq

# List all projects
curl http://localhost:8000/api/projects/ | jq

# Get at-risk projects
curl http://localhost:8000/api/projects/at_risk_projects/ | jq

# Get AI portfolio summary
curl http://localhost:8000/api/ai/portfolio-summary/ | jq

# Ask AI a question
curl -X POST http://localhost:8000/api/ai/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Which projects need immediate attention?"}' | jq
```

### Using Python

```python
import requests

# Get dashboard stats
response = requests.get('http://localhost:8000/api/projects/dashboard_stats/')
stats = response.json()
print(f"Total Projects: {stats['total_projects']}")
print(f"On Track: {stats['by_status']['on_track']}")
print(f"At Risk: {stats['by_status']['at_risk']}")

# Get AI portfolio summary
response = requests.get('http://localhost:8000/api/ai/portfolio-summary/')
summary = response.json()
print(summary['health_summary']['overall_assessment'])
```

## 📱 Features Showcase

### 1. Real-Time Dashboard
- Live portfolio metrics
- Interactive charts (Chart.js)
- Status distribution visualization
- Performance trend indicators

### 2. Project Management
- Comprehensive CRUD operations
- Advanced filtering and search
- Health score calculation
- Budget variance tracking
- SPI/CPI monitoring

### 3. AI-Powered Analysis
- Project status summaries
- Risk analysis with mitigation plans
- Portfolio-level insights
- Executive reports
- Natural language Q&A

### 4. Risk Management
- Categorized risk tracking
- Probability and impact scoring
- Mitigation planning
- Status monitoring

### 5. Task Tracking
- Assignment management
- Milestone identification
- Overdue detection
- Progress monitoring

### 6. Resource Management
- Role-based allocation
- Utilization tracking
- Cost management

## 🎨 UI Features

### Responsive Design
- Mobile-friendly interface
- Tailwind CSS styling
- Modern gradient backgrounds
- Smooth transitions and animations

### Interactive Elements
- Clickable project cards
- Modal dialogs for details
- Loading indicators
- Hover effects

### Visual Indicators
- Color-coded status badges
- Progress bars
- Health score displays
- Chart visualizations

## 🔐 Admin Interface

Access at: http://localhost:8000/admin/

Features:
- Full CRUD for all models
- Bulk operations
- Advanced filtering
- Search functionality
- Read-only calculated fields

## 📚 API Documentation

Interactive API docs at: http://localhost:8000/api/docs/

Features:
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication info

## 🧪 Testing the AI

### Demo Mode (No API Key Required)
The AI works in demo mode with intelligent pre-defined responses:
- Portfolio summaries
- Risk analysis
- Project insights
- Recommendations

### Adding Real Claude AI
1. Get API key from: https://console.anthropic.com/
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
3. Restart server

## 💡 Use Cases

### For Project Managers
- Monitor project health
- Track risks and issues
- Manage tasks and milestones
- Get AI-powered insights

### For PMO Directors
- Portfolio overview
- Performance metrics
- Resource allocation
- Executive reporting

### For Executives
- High-level dashboards
- AI-generated summaries
- Strategic recommendations
- Quick decision support

## 🔄 Next Steps

1. Explore the dashboard
2. Click on projects to see details
3. Try the AI assistant
4. Check the API documentation
5. Use the admin panel
6. Customize for your needs

## 📞 Need Help?

- Check README.md for detailed documentation
- Visit /api/docs/ for API reference
- Review Django admin at /admin/
- Check browser console for errors

---

**Enjoy your PMO AI Assistant!** 🎉
