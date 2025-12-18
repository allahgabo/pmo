from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Project(models.Model):
    """Main Project model representing a single project in the portfolio"""
    
    STATUS_CHOICES = [
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('delayed', 'Delayed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Project code/identifier")
    description = models.TextField(blank=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_track')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Budget
    budget = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total project budget")
    spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Progress Metrics
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall completion percentage"
    )
    
    # Performance Indices
    spi = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=1.00,
        help_text="Schedule Performance Index"
    )
    cpi = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=1.00,
        help_text="Cost Performance Index"
    )
    
    # Team
    project_manager = models.CharField(max_length=255)
    sponsor = models.CharField(max_length=255, blank=True)
    team_size = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['start_date', 'planned_end_date']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_overbudget(self):
        return self.spent > self.budget
    
    @property
    def is_behind_schedule(self):
        return self.spi < 0.9
    
    @property
    def budget_variance(self):
        return float(self.budget - self.spent)
    
    @property
    def days_remaining(self):
        if self.actual_end_date:
            return 0
        delta = self.planned_end_date - timezone.now().date()
        return delta.days
    
    @property
    def health_score(self):
        score = 100
        
        if self.spi < 0.7:
            score -= 30
        elif self.spi < 0.9:
            score -= 15
        
        if self.cpi < 0.7:
            score -= 20
        elif self.cpi < 0.9:
            score -= 10
        
        high_risks = self.risks.filter(severity='high').count()
        score -= min(high_risks * 10, 30)
        
        overdue_tasks = self.tasks.filter(
            status__in=['not_started', 'in_progress'],
            due_date__lt=timezone.now().date()
        ).count()
        score -= min(overdue_tasks * 5, 20)
        
        return max(0, score)


class Risk(models.Model):
    """Risk model for tracking project risks"""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('mitigating', 'Mitigating'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('schedule', 'Schedule'),
        ('budget', 'Budget'),
        ('resource', 'Resource'),
        ('technical', 'Technical'),
        ('scope', 'Scope'),
        ('external', 'External'),
        ('quality', 'Quality'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risks')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    probability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Probability of occurrence (1-100)"
    )
    impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Impact if occurs (1-10)"
    )
    
    mitigation_plan = models.TextField(blank=True)
    owner = models.CharField(max_length=255)
    
    identified_date = models.DateField(default=timezone.now)
    target_closure_date = models.DateField(null=True, blank=True)
    actual_closure_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-probability']
    
    def __str__(self):
        return f"{self.project.code} - {self.title}"
    
    @property
    def risk_score(self):
        return (self.probability / 100) * self.impact


class Task(models.Model):
    """Task model for tracking project tasks"""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    assigned_to = models.CharField(max_length=255)
    
    start_date = models.DateField()
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    planned_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    is_milestone = models.BooleanField(default=False)
    is_critical_path = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.project.code} - {self.name}"
    
    @property
    def is_overdue(self):
        if self.status in ['completed', 'cancelled']:
            return False
        return self.due_date < timezone.now().date()
    
    @property
    def days_until_due(self):
        if self.status in ['completed', 'cancelled']:
            return 0
        delta = self.due_date - timezone.now().date()
        return delta.days


class Resource(models.Model):
    """Resource model for tracking team members"""
    
    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('qa', 'QA Engineer'),
        ('designer', 'Designer'),
        ('analyst', 'Business Analyst'),
        ('architect', 'Architect'),
        ('manager', 'Project Manager'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='resources')
    
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField()
    
    allocation_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage allocated to this project"
    )
    
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.project.code}"


class Milestone(models.Model):
    """Milestone model for tracking key project milestones"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
        ('at_risk', 'At Risk'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    planned_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    deliverables = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['planned_date']
    
    def __str__(self):
        return f"{self.project.code} - {self.name}"
