from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('pmo_director', 'PMO Director'),
        ('project_manager', 'Project Manager'),
        ('team_member', 'Team Member'),
        ('stakeholder', 'Stakeholder'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    dashboard_layout = models.CharField(max_length=20, default='default')
    
    # Statistics
    projects_assigned = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser
    
    @property
    def is_pmo_director(self):
        return self.role in ['admin', 'pmo_director'] or self.user.is_superuser
    
    @property
    def is_project_manager(self):
        return self.role in ['admin', 'pmo_director', 'project_manager'] or self.user.is_superuser
    
    @property
    def can_edit_projects(self):
        return self.is_project_manager


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class ActivityLog(models.Model):
    """Track user activities in the system"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
