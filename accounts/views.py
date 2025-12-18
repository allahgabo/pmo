from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import UserProfile, ActivityLog
from projects.models import Project, Task


def log_activity(user, action, model_name='', object_id=None, description='', request=None):
    """Helper function to log user activities"""
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=ip
    )


# Template Views
def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_activity(user, 'login', request=request)
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'team_member')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Update profile
            profile = user.profile
            profile.role = role
            profile.save()
            
            log_activity(user, 'create', 'User', user.id, 'User registered', request)
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    
    return render(request, 'accounts/register.html')


@login_required
def logout_view(request):
    """Logout user"""
    log_activity(request.user, 'logout', request=request)
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    profile = user.profile
    
    # Get user's projects
    if profile.is_pmo_director:
        projects = Project.objects.all()
    elif profile.is_project_manager:
        projects = Project.objects.filter(project_manager=user.get_full_name())
    else:
        # Team member - get projects where they have tasks
        projects = Project.objects.filter(
            tasks__assigned_to=user.get_full_name()
        ).distinct()
    
    # Get user's tasks
    tasks = Task.objects.filter(assigned_to=user.get_full_name()).order_by('due_date')[:10]
    
    # Get recent activities
    activities = ActivityLog.objects.filter(user=user)[:10]
    
    context = {
        'projects': projects[:10],
        'tasks': tasks,
        'activities': activities,
        'total_projects': projects.count(),
        'total_tasks': tasks.count(),
    }
    
    log_activity(user, 'view', 'Dashboard', request=request)
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile page"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Update profile
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        profile.department = request.POST.get('department', profile.department)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.save()
        
        log_activity(user, 'update', 'UserProfile', profile.id, 'Profile updated', request)
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    # Get user statistics
    activities = ActivityLog.objects.filter(user=user)[:20]
    
    context = {
        'activities': activities,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def projects_list_view(request):
    """Projects list page"""
    user = request.user
    profile = user.profile
    
    # Filter projects based on role
    if profile.is_pmo_director:
        projects = Project.objects.all()
    elif profile.is_project_manager:
        projects = Project.objects.filter(project_manager=user.get_full_name())
    else:
        projects = Project.objects.filter(
            tasks__assigned_to=user.get_full_name()
        ).distinct()
    
    # Apply filters from query params
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search = request.GET.get('search')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    if search:
        projects = projects.filter(name__icontains=search)
    
    log_activity(user, 'view', 'Project', description='Viewed projects list', request=request)
    
    context = {
        'projects': projects,
        'can_edit': profile.can_edit_projects,
    }
    
    return render(request, 'projects/list.html', context)


@login_required
def project_detail_view(request, pk):
    """Project detail page"""
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found')
        return redirect('projects_list')
    
    user = request.user
    profile = user.profile
    
    # Check permissions
    can_edit = profile.can_edit_projects
    
    # Calculate task statistics
    task_stats = {
        'completed': project.tasks.filter(status='completed').count(),
        'in_progress': project.tasks.filter(status='in_progress').count(),
        'not_started': project.tasks.filter(status='not_started').count(),
    }
    
    log_activity(user, 'view', 'Project', project.id, f'Viewed project: {project.name}', request)
    
    context = {
        'project': project,
        'can_edit': can_edit,
        'task_stats': task_stats,
    }
    
    return render(request, 'projects/detail.html', context)


@login_required
def tasks_list_view(request):
    """Tasks list page"""
    user = request.user
    profile = user.profile
    
    # Filter tasks based on role
    if profile.is_pmo_director:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user.get_full_name())
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    log_activity(user, 'view', 'Task', description='Viewed tasks list', request=request)
    
    context = {
        'tasks': tasks.order_by('due_date'),
    }
    
    return render(request, 'tasks/list.html', context)


# API Views
class LoginAPIView(APIView):
    """API endpoint for login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            log_activity(user, 'login', request=request)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.profile.role,
                'is_admin': user.profile.is_admin,
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterAPIView(APIView):
    """API endpoint for registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        token = Token.objects.create(user=user)
        log_activity(user, 'create', 'User', user.id, 'User registered via API')
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_201_CREATED)


class UserProfileAPIView(APIView):
    """API endpoint for user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile = user.profile
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': profile.role,
            'department': profile.department,
            'phone': profile.phone,
            'bio': profile.bio,
            'email_notifications': profile.email_notifications,
            'projects_assigned': profile.projects_assigned,
            'tasks_completed': profile.tasks_completed,
            'is_admin': profile.is_admin,
            'can_edit_projects': profile.can_edit_projects,
        })
    
    def put(self, request):
        user = request.user
        profile = user.profile
        
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        profile.department = request.data.get('department', profile.department)
        profile.phone = request.data.get('phone', profile.phone)
        profile.bio = request.data.get('bio', profile.bio)
        profile.save()
        
        log_activity(user, 'update', 'UserProfile', profile.id, 'Profile updated via API', request)
        
        return Response({'message': 'Profile updated successfully'})


class ActivityLogAPIView(APIView):
    """API endpoint for activity logs"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        activities = ActivityLog.objects.filter(user=request.user)[:50]
        
        data = [{
            'action': act.action,
            'model_name': act.model_name,
            'description': act.description,
            'timestamp': act.timestamp,
        } for act in activities]
        
        return Response(data)


@login_required
def project_create_view(request):
    """Create new project"""
    from projects.forms import ProjectForm
    
    user = request.user
    profile = user.profile
    
    # Check permissions
    if not profile.can_edit_projects:
        messages.error(request, 'You do not have permission to create projects')
        return redirect('projects_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            log_activity(user, 'create', 'Project', project.id, f'Created project: {project.name}', request)
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('project_detail', pk=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'projects/form.html', context)


@login_required
def project_edit_view(request, pk):
    """Edit existing project"""
    from projects.forms import ProjectForm
    
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found')
        return redirect('projects_list')
    
    user = request.user
    profile = user.profile
    
    # Check permissions
    if not profile.can_edit_projects:
        messages.error(request, 'You do not have permission to edit projects')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            log_activity(user, 'update', 'Project', project.id, f'Updated project: {project.name}', request)
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('project_detail', pk=project.id)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'action': 'Edit',
    }
    
    return render(request, 'projects/form.html', context)


@login_required
def project_delete_view(request, pk):
    """Delete project"""
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found')
        return redirect('projects_list')
    
    user = request.user
    profile = user.profile
    
    # Check permissions
    if not profile.is_pmo_director:
        messages.error(request, 'Only PMO Directors can delete projects')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        project_name = project.name
        log_activity(user, 'delete', 'Project', project.id, f'Deleted project: {project_name}', request)
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('projects_list')
    
    context = {
        'project': project,
    }
    
    return render(request, 'projects/delete_confirm.html', context)