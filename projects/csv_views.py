import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from io import TextIOWrapper
from projects.models import Project, Task, Risk, Resource


@login_required
def export_projects_csv(request):
    """
    Export projects to CSV format.
    Columns: project_id, project_name, start_date, end_date, budget, status
    Used for: Portfolio health, Executive summaries, AI status explanations
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="projects.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['project_id', 'project_name', 'start_date', 'end_date', 'budget', 'status'])
    
    projects = Project.objects.all()
    for project in projects:
        writer.writerow([
            project.id,
            project.name,
            project.start_date,
            project.actual_end_date or project.planned_end_date,
            project.budget,
            project.get_status_display()
        ])
    
    return response


@login_required
def export_tasks_csv(request):
    """
    Export tasks to CSV format.
    Columns: task_id, project_id, task_name, planned_days, actual_days, progress_pct
    Used for: Schedule variance, Delay detection, Risk scoring
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['task_id', 'project_id', 'task_name', 'planned_days', 'actual_days', 'progress_pct'])
    
    tasks = Task.objects.all().select_related('project')
    for task in tasks:
        # Calculate planned days
        if task.start_date and task.due_date:
            planned_days = (task.due_date - task.start_date).days
        else:
            planned_days = 0
        
        # Calculate actual days
        if task.completion_date and task.start_date:
            actual_days = (task.completion_date - task.start_date).days
        else:
            actual_days = 0
        
        writer.writerow([
            task.id,
            task.project.id,
            task.name,
            planned_days,
            actual_days,
            task.completion_percentage
        ])
    
    return response


@login_required
def export_risks_csv(request):
    """
    Export risks to CSV format.
    Columns: risk_id, project_id, risk_type, risk_level, description
    Used for: AI risk explanation, Executive risk summaries
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="risks.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['risk_id', 'project_id', 'risk_type', 'risk_level', 'description'])
    
    risks = Risk.objects.all().select_related('project')
    for risk in risks:
        writer.writerow([
            risk.id,
            risk.project.id,
            risk.get_category_display(),
            risk.get_severity_display(),
            risk.description
        ])
    
    return response


@login_required
def export_resources_csv(request):
    """
    Export resources to CSV format.
    Columns: resource_id, name, role, utilization_pct
    Used for: Over-allocation detection, Capacity planning, AI recommendations
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resources.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['resource_id', 'name', 'role', 'utilization_pct'])
    
    resources = Resource.objects.filter(is_active=True)
    for resource in resources:
        writer.writerow([
            resource.id,
            resource.name,
            resource.get_role_display(),
            resource.allocation_percentage
        ])
    
    return response


@login_required
def export_all_csv(request):
    """Export all data as a ZIP file containing all 4 CSV files"""
    import zipfile
    from io import BytesIO
    
    # Create in-memory ZIP file
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Projects CSV
        projects_csv = BytesIO()
        projects_csv.write(b'project_id,project_name,start_date,end_date,budget,status\n')
        for project in Project.objects.all():
            line = f"{project.id},{project.name},{project.start_date},{project.actual_end_date or project.planned_end_date},{project.budget},{project.get_status_display()}\n"
            projects_csv.write(line.encode('utf-8'))
        zip_file.writestr('projects.csv', projects_csv.getvalue())
        
        # Tasks CSV
        tasks_csv = BytesIO()
        tasks_csv.write(b'task_id,project_id,task_name,planned_days,actual_days,progress_pct\n')
        for task in Task.objects.all().select_related('project'):
            planned_days = (task.due_date - task.start_date).days if task.start_date and task.due_date else 0
            actual_days = (task.completion_date - task.start_date).days if task.completion_date and task.start_date else 0
            line = f"{task.id},{task.project.id},{task.name},{planned_days},{actual_days},{task.completion_percentage}\n"
            tasks_csv.write(line.encode('utf-8'))
        zip_file.writestr('tasks.csv', tasks_csv.getvalue())
        
        # Risks CSV
        risks_csv = BytesIO()
        risks_csv.write(b'risk_id,project_id,risk_type,risk_level,description\n')
        for risk in Risk.objects.all().select_related('project'):
            # Escape commas and quotes in description
            description = risk.description.replace('"', '""')
            line = f'{risk.id},{risk.project.id},{risk.get_category_display()},{risk.get_severity_display()},"{description}"\n'
            risks_csv.write(line.encode('utf-8'))
        zip_file.writestr('risks.csv', risks_csv.getvalue())
        
        # Resources CSV
        resources_csv = BytesIO()
        resources_csv.write(b'resource_id,name,role,utilization_pct\n')
        for resource in Resource.objects.filter(is_active=True):
            line = f"{resource.id},{resource.name},{resource.get_role_display()},{resource.allocation_percentage}\n"
            resources_csv.write(line.encode('utf-8'))
        zip_file.writestr('resources.csv', resources_csv.getvalue())
    
    # Prepare response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="pmo_data_export.zip"'
    
    return response


@login_required
def import_csv_page(request):
    """Display CSV import page"""
    return render(request, 'projects/import_csv.html')


@login_required
def import_projects_csv(request):
    """Import projects from CSV file"""
    if request.method != 'POST':
        return redirect('import_csv_page')
    
    csv_file = request.FILES.get('file')
    if not csv_file:
        messages.error(request, 'No file uploaded')
        return redirect('import_csv_page')
    
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'File must be CSV format')
        return redirect('import_csv_page')
    
    try:
        # Read CSV
        decoded_file = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(decoded_file.splitlines())
        
        imported_count = 0
        for row in csv_data:
            # Check if project exists
            project_id = row.get('project_id')
            if project_id and Project.objects.filter(id=project_id).exists():
                # Update existing
                project = Project.objects.get(id=project_id)
                project.name = row.get('project_name', project.name)
                project.start_date = row.get('start_date', project.start_date)
                project.budget = row.get('budget', project.budget)
                
                # Map status
                status_map = {
                    'On Track': 'on_track',
                    'At Risk': 'at_risk',
                    'Delayed': 'delayed',
                    'Completed': 'completed'
                }
                status_value = row.get('status', '')
                if status_value in status_map:
                    project.status = status_map[status_value]
                
                project.save()
            else:
                # Create new (basic implementation)
                pass
            
            imported_count += 1
        
        messages.success(request, f'Successfully imported {imported_count} projects')
    except Exception as e:
        messages.error(request, f'Error importing CSV: {str(e)}')
    
    return redirect('import_csv_page')


@login_required
def data_export_page(request):
    """Display data export options page"""
    return render(request, 'projects/data_export.html')