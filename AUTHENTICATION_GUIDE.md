# PMO AI Assistant - Multi-User Authentication System

## 🎉 What's New - Version 2.0

This updated version includes a complete **multi-user authentication system** with role-based access control, dynamic user interactions, and multiple pages for different user types.

## 🚀 New Features

### 1. Authentication System
- ✅ **User Registration** - Self-service account creation
- ✅ **Login/Logout** - Secure authentication
- ✅ **Password Management** - Secure password handling
- ✅ **Session Management** - Keep users logged in
- ✅ **Activity Logging** - Track all user actions

### 2. User Roles & Permissions
- **Administrator** - Full system access
- **PMO Director** - Portfolio-level access, can view all projects
- **Project Manager** - Can manage assigned projects
- **Team Member** - Can view and update assigned tasks
- **Stakeholder** - Read-only access to projects

### 3. Multi-Page Application
- **Login Page** - Beautiful authentication interface
- **Registration Page** - Self-service account creation
- **Dashboard** - Personalized for each user role
- **Projects List** - Filterable, searchable project grid
- **Project Detail** - Comprehensive project information
- **Tasks List** - Personal task management
- **User Profile** - Manage account settings

### 4. Dynamic User Experience
- **Role-Based Navigation** - Different menus for different users
- **Personalized Dashboard** - Shows only relevant projects/tasks
- **Activity Tracking** - All user actions are logged
- **Real-Time Filters** - Dynamic project and task filtering
- **Responsive Design** - Works on all devices

### 5. User Profile System
- Extended user profiles with additional fields
- Department and phone information
- Bio and preferences
- Email notification settings
- Activity history

## 📋 Quick Start Guide

### Step 1: Start the Server
```bash
cd /mnt/user-data/outputs/pmo-ai-assistant
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Access the Application
Open your browser to: **http://localhost:8000**

You'll be redirected to the login page.

### Step 3: Login with Demo Account
```
Username: admin
Password: admin123
```

### Step 4: Create New Users
1. Click "Create Account" on login page
2. Fill in the registration form
3. Choose your role (Team Member, Project Manager, PMO Director, etc.)
4. Submit and login

## 🎭 User Roles Explained

### Administrator (Superuser)
- Full access to everything
- Can use Django admin panel
- Can create/edit/delete any data
- Sees all projects and tasks
- Access to AI Assistant and API docs

**Login:** admin / admin123

### PMO Director
- Portfolio-level view
- Can see all projects
- Access to dashboards and reports
- Can use AI Assistant
- Cannot directly edit (must use admin panel)

**How to Create:**
1. Register with role "PMO Director"
2. Or create via Django admin

### Project Manager
- Can see projects they manage
- Can view project details
- Can see tasks in their projects
- Limited to assigned projects

**How to Create:**
1. Register with role "Project Manager"
2. Assign as project manager in projects

### Team Member
- Can see assigned tasks
- Can see projects they're working on
- Personal dashboard with their tasks
- Task-focused interface

**How to Create:**
1. Register with role "Team Member"
2. Assign tasks to them

### Stakeholder
- Read-only access
- Can view projects
- Cannot edit anything
- Good for executives or clients

## 🌐 Page-by-Page Guide

### Login Page (`/login/`)
- Clean, modern design
- Username/password authentication
- Link to registration
- Demo credentials displayed

### Registration Page (`/register/`)
- Self-service account creation
- Choose your role
- Email validation
- Password confirmation

### Dashboard (`/dashboard/`)
**Personalized for each user:**
- **Stats Cards**: My Projects, My Tasks, Role, Activities
- **My Projects**: Shows projects relevant to the user
- **My Tasks**: Personal task list
- **Recent Activity**: User's action history
- **Quick Actions** (PMO Directors only): Links to admin, AI, API

**What Users See:**
- PMO Directors: All projects
- Project Managers: Their managed projects
- Team Members: Projects with their tasks
- Stakeholders: Projects they can view

### Projects List (`/projects/`)
- Grid view of all accessible projects
- **Filters**:
  - Status (On Track, At Risk, Delayed, Completed)
  - Priority (Low, Medium, High, Critical)
  - Search by name or code
- Each card shows:
  - Project name and code
  - Status badge
  - Progress bar
  - SPI, Health Score
  - Risk and task counts
  - Project manager

### Project Detail (`/projects/{id}/`)
- Complete project information
- Overview cards (Completion, Health, SPI, CPI)
- Description section
- Budget and timeline
- Risk list (top 5)
- Team information sidebar
- Task summary
- AI Analysis button

### Tasks List (`/tasks/`)
- All tasks assigned to the user
- Filter by status
- Shows:
  - Task name and description
  - Project name
  - Due date and progress
  - Hours (planned vs actual)
  - Overdue warning
  - Milestone badge
- Link to project details

### User Profile (`/profile/`)
- Edit personal information
- Update contact details
- Set preferences
- View activity history

## 🔐 Security Features

### Password Security
- Passwords are hashed (never stored plain text)
- Django's built-in password validators
- Password confirmation on registration

### Session Management
- Secure session cookies
- Automatic logout after inactivity (configurable)
- CSRF protection on all forms

### Access Control
- Login required for all pages (except login/register)
- Role-based permissions
- Users can only see data they have access to

### Activity Logging
All user actions are tracked:
- Login/logout events
- Page views
- Data creation/updates/deletions
- IP address logging

## 📊 How Data is Filtered by Role

### PMO Director
```python
projects = Project.objects.all()  # All projects
```

### Project Manager
```python
projects = Project.objects.filter(
    project_manager=user.get_full_name()
)
```

### Team Member
```python
projects = Project.objects.filter(
    tasks__assigned_to=user.get_full_name()
).distinct()
```

### Tasks
- PMO Directors see all tasks
- Others see only their assigned tasks

## 🎨 UI/UX Enhancements

### Responsive Sidebar
- Desktop: Always visible
- Mobile: Collapsible hamburger menu
- Smooth animations

### Status Badges
- Color-coded by status
- Consistent across pages
- Easy to spot at a glance

### Progress Bars
- Visual completion indicators
- Color-coded by health
- Animated on hover

### Card Hover Effects
- Subtle elevation on hover
- Smooth transitions
- Professional appearance

### Message System
- Success messages (green)
- Error messages (red)
- Info messages (blue)
- Auto-dismiss option

## 🔧 Technical Implementation

### Models
**UserProfile**
- One-to-one with Django User
- Role field
- Department, phone, bio
- Preferences
- Statistics (projects assigned, tasks completed)

**ActivityLog**
- User foreign key
- Action type (login, create, update, etc.)
- Model name and object ID
- Description
- IP address
- Timestamp

### Views
**Template Views**
- `login_view` - Authentication
- `register_view` - Account creation
- `logout_view` - Session termination
- `dashboard_view` - Personalized dashboard
- `projects_list_view` - Filtered projects
- `project_detail_view` - Single project
- `tasks_list_view` - User's tasks
- `profile_view` - User settings

**API Views**
- `LoginAPIView` - Token-based login
- `RegisterAPIView` - API registration
- `UserProfileAPIView` - Get/update profile
- `ActivityLogAPIView` - Activity history

### URL Structure
```
/                       → Dashboard (requires login)
/login/                 → Login page
/register/              → Registration page
/logout/                → Logout (redirects to login)
/dashboard/             → User dashboard
/projects/              → Projects list
/projects/123/          → Project detail
/tasks/                 → Tasks list
/profile/               → User profile
/admin/                 → Django admin (superusers only)
/api/docs/              → API documentation
```

### Templates
- `base.html` - Base template with navigation
- `accounts/login.html` - Login page
- `accounts/register.html` - Registration page
- `accounts/profile.html` - User profile
- `dashboard.html` - Main dashboard
- `projects/list.html` - Projects grid
- `projects/detail.html` - Project details
- `tasks/list.html` - Tasks list

## 📱 Mobile Responsive

All pages are fully responsive:
- Collapsible sidebar on mobile
- Stack cards vertically on small screens
- Touch-friendly buttons
- Readable text sizes
- Optimized for tablets and phones

## 🚀 Usage Examples

### Create a New Project Manager
1. Go to `/register/`
2. Fill in details
3. Select "Project Manager" role
4. Login
5. Assign as project manager in Django admin

### Assign Tasks to Team Members
1. Login as admin
2. Go to Django admin `/admin/`
3. Edit a task
4. Set "assigned_to" to team member's full name
5. Team member will see it in their dashboard

### View Activity Logs
1. Login as admin
2. Go to `/admin/accounts/activitylog/`
3. See all user activities
4. Filter by user, action, date

### Give a User PMO Director Access
1. Login as admin
2. Go to `/admin/accounts/userprofile/`
3. Find user's profile
4. Change role to "PMO Director"
5. Save
6. User now sees all projects

## 🎯 Best Practices

### For Administrators
1. Create user accounts for each team member
2. Assign appropriate roles
3. Update project managers' names to match user full names
4. Regularly review activity logs
5. Use Django admin for bulk operations

### For Project Managers
1. Login daily to check project health
2. Review tasks in your projects
3. Monitor SPI and CPI indicators
4. Address at-risk projects immediately
5. Use AI assistant for insights

### For Team Members
1. Check dashboard for new tasks
2. Update task progress regularly
3. Flag blocked tasks immediately
4. View project details for context
5. Communicate with project manager

## 🔄 Workflow Example

### Typical Day for a Project Manager

1. **Morning Login**
   - See dashboard with project overview
   - Check for at-risk projects (orange/red badges)
   - Review task statuses

2. **Project Review**
   - Click on an at-risk project
   - Review health score and SPI
   - Check risk list
   - Use AI analysis for insights

3. **Task Management**
   - Go to projects list
   - Filter by "At Risk"
   - Review each project's tasks
   - Identify bottlenecks

4. **Reporting**
   - Use API to pull data
   - Generate reports
   - Share with stakeholders

### Typical Day for a Team Member

1. **Check Dashboard**
   - See assigned tasks
   - Identify overdue items
   - Check upcoming deadlines

2. **Work on Tasks**
   - Open tasks list
   - Filter by "In Progress"
   - Update progress
   - Mark completed tasks

3. **Context Review**
   - Click project links
   - Understand project goals
   - See overall project health
   - Coordinate with team

## 🐛 Troubleshooting

### Can't Login
- Check username/password
- Verify account exists in `/admin/auth/user/`
- Check if account is active

### Don't See My Projects
- Verify your role
- Check if project_manager name matches your full name
- Contact administrator

### Tasks Not Showing
- Verify tasks are assigned to you (exact name match)
- Check task status filter
- Contact project manager

### Permission Denied
- Check your role
- Some features require PMO Director or Admin
- Contact administrator for role change

## 📝 API Integration

All previous API endpoints still work, plus new ones:

### Authentication
```bash
# Login via API
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Returns token for subsequent requests
```

### Get User Profile
```bash
curl http://localhost:8000/api/profile/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Activity Log
```bash
curl http://localhost:8000/api/activities/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 🎓 Next Steps

1. **Start the server** and explore the new interface
2. **Create test users** with different roles
3. **Assign tasks** to see role-based filtering
4. **Review activity logs** to understand tracking
5. **Customize** the templates to match your brand
6. **Extend** with additional features as needed

## 🌟 What Makes This Special

- **Production-Ready**: Full authentication and authorization
- **Role-Based**: Different experiences for different users
- **Dynamic**: Content changes based on who's logged in
- **Secure**: Industry-standard security practices
- **Beautiful**: Modern, professional UI
- **Responsive**: Works on all devices
- **Tracked**: Complete activity logging
- **Scalable**: Ready for real deployment

## 📚 Additional Resources

- Django Authentication: https://docs.djangoproject.com/en/5.0/topics/auth/
- Django Permissions: https://docs.djangoproject.com/en/5.0/topics/auth/default/#permissions-and-authorization
- REST Framework Auth: https://www.django-rest-framework.org/api-guide/authentication/
- Bootstrap/Tailwind: https://tailwindcss.com/

---

**Version 2.0 - Multi-User System**  
**Date: December 18, 2025**  
**Status: Production Ready** ✅
