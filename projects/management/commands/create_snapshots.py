from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project, ProjectSnapshot


class Command(BaseCommand):
    help = 'Create daily snapshots of all projects for historical tracking'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        projects = Project.objects.all()
        
        created_count = 0
        updated_count = 0
        
        for project in projects:
            # Check if snapshot already exists for today
            snapshot, created = ProjectSnapshot.objects.get_or_create(
                project=project,
                snapshot_date=today,
                defaults={
                    'status': project.status,
                    'completion_percentage': project.completion_percentage,
                    'budget': project.budget,
                    'spent': project.spent,
                    'spi': project.spi,
                    'cpi': project.cpi,
                    'health_score': project.health_score,
                    'total_tasks': project.tasks.count(),
                    'completed_tasks': project.tasks.filter(status='completed').count(),
                    'total_risks': project.risks.count(),
                    'high_risks': project.risks.filter(severity__in=['high', 'critical']).count(),
                    'total_issues': project.issues.count() if hasattr(project, 'issues') else 0,
                    'open_issues': project.issues.filter(status='open').count() if hasattr(project, 'issues') else 0,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created snapshot for {project.code}'
                ))
            else:
                # Update if already exists
                snapshot.status = project.status
                snapshot.completion_percentage = project.completion_percentage
                snapshot.budget = project.budget
                snapshot.spent = project.spent
                snapshot.spi = project.spi
                snapshot.cpi = project.cpi
                snapshot.health_score = project.health_score
                snapshot.total_tasks = project.tasks.count()
                snapshot.completed_tasks = project.tasks.filter(status='completed').count()
                snapshot.total_risks = project.risks.count()
                snapshot.high_risks = project.risks.filter(severity__in=['high', 'critical']).count()
                snapshot.total_issues = project.issues.count() if hasattr(project, 'issues') else 0
                snapshot.open_issues = project.issues.filter(status='open').count() if hasattr(project, 'issues') else 0
                snapshot.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(
                    f'Updated snapshot for {project.code}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSnapshot complete: {created_count} created, {updated_count} updated'
        ))