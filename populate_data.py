import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmo_core.settings')
django.setup()

from projects.models import Project, Risk, Task, Resource, Milestone

def create_sample_data():
    print("Creating sample PMO data...")
    
    # Clear existing data
    Project.objects.all().delete()
    
    # Sample data
    projects_data = [
        {
            'name': 'Alpha CRM Implementation',
            'code': 'CRM-001',
            'status': 'at_risk',
            'priority': 'high',
            'completion': 58,
            'spi': 0.86,
            'cpi': 0.92,
            'budget': 500000,
            'spent': 320000,
            'pm': 'Sarah Johnson',
            'team_size': 12,
        },
        {
            'name': 'Beta Mobile App',
            'code': 'MOB-002',
            'status': 'on_track',
            'priority': 'critical',
            'completion': 75,
            'spi': 1.05,
            'cpi': 1.02,
            'budget': 350000,
            'spent': 250000,
            'pm': 'Michael Chen',
            'team_size': 8,
        },
        {
            'name': 'Gamma Data Warehouse',
            'code': 'DW-003',
            'status': 'delayed',
            'priority': 'high',
            'completion': 42,
            'spi': 0.75,
            'cpi': 0.88,
            'budget': 750000,
            'spent': 480000,
            'pm': 'Ahmed Al-Rashid',
            'team_size': 15,
        },
        {
            'name': 'Delta API Gateway',
            'code': 'API-004',
            'status': 'on_track',
            'priority': 'medium',
            'completion': 85,
            'spi': 1.12,
            'cpi': 1.08,
            'budget': 200000,
            'spent': 155000,
            'pm': 'Lisa Anderson',
            'team_size': 6,
        },
        {
            'name': 'Epsilon Security Upgrade',
            'code': 'SEC-005',
            'status': 'at_risk',
            'priority': 'critical',
            'completion': 35,
            'spi': 0.82,
            'cpi': 0.95,
            'budget': 400000,
            'spent': 180000,
            'pm': 'David Kim',
            'team_size': 10,
        },
        {
            'name': 'Zeta Cloud Migration',
            'code': 'CLD-006',
            'status': 'on_track',
            'priority': 'high',
            'completion': 65,
            'spi': 0.98,
            'cpi': 1.00,
            'budget': 600000,
            'spent': 380000,
            'pm': 'Maria Garcia',
            'team_size': 14,
        },
        {
            'name': 'Eta Analytics Platform',
            'code': 'ANL-007',
            'status': 'on_track',
            'priority': 'medium',
            'completion': 90,
            'spi': 1.15,
            'cpi': 1.10,
            'budget': 300000,
            'spent': 260000,
            'pm': 'James Wilson',
            'team_size': 7,
        },
        {
            'name': 'Theta Customer Portal',
            'code': 'PRT-008',
            'status': 'delayed',
            'priority': 'high',
            'completion': 48,
            'spi': 0.78,
            'cpi': 0.85,
            'budget': 450000,
            'spent': 310000,
            'pm': 'Emma Thompson',
            'team_size': 11,
        },
    ]
    
    # Create projects
    for pd in projects_data:
        start_date = datetime.now().date() - timedelta(days=random.randint(60, 180))
        end_date = start_date + timedelta(days=random.randint(180, 365))
        
        project = Project.objects.create(
            name=pd['name'],
            code=pd['code'],
            description=f"Enterprise project for {pd['name']}",
            status=pd['status'],
            priority=pd['priority'],
            start_date=start_date,
            planned_end_date=end_date,
            budget=Decimal(str(pd['budget'])),
            spent=Decimal(str(pd['spent'])),
            completion_percentage=pd['completion'],
            spi=Decimal(str(pd['spi'])),
            cpi=Decimal(str(pd['cpi'])),
            project_manager=pd['pm'],
            sponsor='Executive Board',
            team_size=pd['team_size']
        )
        
        print(f"Created project: {project.name}")
        
        # Create risks for each project
        risk_categories = ['schedule', 'budget', 'resource', 'technical', 'scope']
        num_risks = random.randint(2, 6)
        
        for i in range(num_risks):
            severity = random.choice(['low', 'medium', 'high', 'critical'])
            Risk.objects.create(
                project=project,
                title=f"Risk {i+1} for {project.code}",
                description=f"Potential {random.choice(risk_categories)} issue that could impact project delivery",
                category=random.choice(risk_categories),
                severity=severity,
                status=random.choice(['open', 'mitigating', 'closed']),
                probability=random.randint(30, 90),
                impact=random.randint(5, 10),
                mitigation_plan="Monitoring and contingency planning in place",
                owner=pd['pm'],
                identified_date=start_date + timedelta(days=random.randint(10, 60))
            )
        
        # Create tasks
        num_tasks = random.randint(5, 12)
        for i in range(num_tasks):
            task_start = start_date + timedelta(days=random.randint(0, 90))
            task_due = task_start + timedelta(days=random.randint(14, 60))
            
            Task.objects.create(
                project=project,
                name=f"Task {i+1}: Implementation Phase",
                description="Key deliverable for project milestone",
                status=random.choice(['not_started', 'in_progress', 'completed', 'blocked']),
                assigned_to=f"Team Member {random.randint(1, pd['team_size'])}",
                start_date=task_start,
                due_date=task_due,
                planned_hours=Decimal(str(random.randint(40, 160))),
                actual_hours=Decimal(str(random.randint(30, 180))),
                completion_percentage=random.randint(0, 100),
                is_milestone=random.choice([True, False]),
                is_critical_path=random.choice([True, False])
            )
        
        # Create resources
        roles = ['developer', 'qa', 'designer', 'analyst', 'architect']
        for i in range(pd['team_size']):
            Resource.objects.create(
                project=project,
                name=f"{random.choice(['John', 'Jane', 'Alice', 'Bob', 'Charlie'])} {random.choice(['Smith', 'Doe', 'Wilson', 'Brown', 'Davis'])}",
                role=random.choice(roles),
                email=f"team{i}@company.com",
                allocation_percentage=random.randint(50, 100),
                hourly_rate=Decimal(str(random.randint(50, 150))),
                start_date=start_date,
                is_active=True
            )
        
        # Create milestones
        num_milestones = random.randint(3, 6)
        for i in range(num_milestones):
            milestone_date = start_date + timedelta(days=(i+1) * 60)
            Milestone.objects.create(
                project=project,
                name=f"Milestone {i+1}: Phase Completion",
                description=f"Key milestone for {project.name}",
                planned_date=milestone_date,
                status=random.choice(['pending', 'achieved', 'at_risk']),
                deliverables="Phase deliverables and documentation"
            )
    
    print("\nSample data created successfully!")
    print(f"Total Projects: {Project.objects.count()}")
    print(f"Total Risks: {Risk.objects.count()}")
    print(f"Total Tasks: {Task.objects.count()}")
    print(f"Total Resources: {Resource.objects.count()}")
    print(f"Total Milestones: {Milestone.objects.count()}")

if __name__ == '__main__':
    create_sample_data()
