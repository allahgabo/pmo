// API Base URL
const API_BASE = '/api';
const AI_BASE = '/api/ai';

// Global state
let allProjects = [];
let dashboardStats = {};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Section navigation
function showSection(section) {
    document.querySelectorAll('.section').forEach(el => el.classList.add('hidden'));
    document.getElementById(section + '-section').classList.remove('hidden');
    
    if (section === 'projects') {
        loadProjects();
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/projects/dashboard_stats/`);
        dashboardStats = await response.json();
        
        renderStatsCards();
        renderCharts();
        loadAtRiskProjects();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Render stats cards
function renderStatsCards() {
    const stats = dashboardStats;
    const html = `
        <div class="bg-white rounded-lg shadow-md p-6 card-hover transition-all">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-500 text-sm">Total Projects</p>
                    <p class="text-3xl font-bold text-gray-900">${stats.total_projects || 0}</p>
                </div>
                <i class="fas fa-folder-open text-4xl text-purple-500"></i>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 card-hover transition-all">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-500 text-sm">On Track</p>
                    <p class="text-3xl font-bold text-green-600">${stats.by_status?.on_track || 0}</p>
                </div>
                <i class="fas fa-check-circle text-4xl text-green-500"></i>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 card-hover transition-all">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-500 text-sm">At Risk</p>
                    <p class="text-3xl font-bold text-orange-600">${stats.by_status?.at_risk || 0}</p>
                </div>
                <i class="fas fa-exclamation-triangle text-4xl text-orange-500"></i>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 card-hover transition-all">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-500 text-sm">Avg Completion</p>
                    <p class="text-3xl font-bold text-blue-600">${stats.performance?.avg_completion?.toFixed(0) || 0}%</p>
                </div>
                <i class="fas fa-chart-line text-4xl text-blue-500"></i>
            </div>
        </div>
    `;
    document.getElementById('stats-cards').innerHTML = html;
}

// Render charts
function renderCharts() {
    const stats = dashboardStats;
    
    // Status distribution chart
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: ['On Track', 'At Risk', 'Delayed', 'Completed'],
            datasets: [{
                data: [
                    stats.by_status?.on_track || 0,
                    stats.by_status?.at_risk || 0,
                    stats.by_status?.delayed || 0,
                    stats.by_status?.completed || 0
                ],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#3b82f6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
    
    // Performance chart
    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    new Chart(perfCtx, {
        type: 'bar',
        data: {
            labels: ['Avg SPI', 'Avg CPI', 'Completion %'],
            datasets: [{
                label: 'Performance Metrics',
                data: [
                    (stats.performance?.avg_spi || 0) * 100,
                    (stats.performance?.avg_cpi || 0) * 100,
                    stats.performance?.avg_completion || 0
                ],
                backgroundColor: ['#667eea', '#764ba2', '#10b981']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Load at-risk projects
async function loadAtRiskProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects/at_risk_projects/`);
        const projects = await response.json();
        
        if (projects.length === 0) {
            document.getElementById('at-risk-projects').innerHTML = 
                '<p class="text-gray-500 text-center py-8">No projects at risk!</p>';
            return;
        }
        
        const html = projects.map(p => `
            <div class="border-l-4 border-orange-500 bg-orange-50 p-4 mb-3 rounded hover:bg-orange-100 cursor-pointer"
                 onclick="showProjectDetail(${p.id})">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-semibold text-gray-900">${p.name}</h4>
                        <p class="text-sm text-gray-600">${p.code}</p>
                    </div>
                    <div class="text-right">
                        <span class="inline-block px-3 py-1 text-sm rounded-full bg-orange-200 text-orange-800">
                            ${p.status.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                </div>
                <div class="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                        <span class="text-gray-600">SPI:</span>
                        <span class="font-semibold ml-1">${p.spi}</span>
                    </div>
                    <div>
                        <span class="text-gray-600">Complete:</span>
                        <span class="font-semibold ml-1">${p.completion_percentage}%</span>
                    </div>
                    <div>
                        <span class="text-gray-600">High Risks:</span>
                        <span class="font-semibold ml-1 text-red-600">${p.high_risks}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        document.getElementById('at-risk-projects').innerHTML = html;
    } catch (error) {
        console.error('Error loading at-risk projects:', error);
    }
}

// Load all projects
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects/`);
        allProjects = await response.json();
        
        if (allProjects.results) {
            allProjects = allProjects.results;
        }
        
        renderProjects(allProjects);
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Render projects grid
function renderProjects(projects) {
    if (projects.length === 0) {
        document.getElementById('projects-grid').innerHTML = 
            '<p class="col-span-3 text-gray-500 text-center py-8">No projects found</p>';
        return;
    }
    
    const html = projects.map(p => `
        <div class="bg-white rounded-lg shadow-md p-6 card-hover transition-all cursor-pointer"
             onclick="showProjectDetail(${p.id})">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">${p.name}</h3>
                    <p class="text-sm text-gray-600">${p.code}</p>
                </div>
                <span class="px-3 py-1 text-xs rounded-full ${getStatusClass(p.status)}">
                    ${p.status.replace('_', ' ').toUpperCase()}
                </span>
            </div>
            
            <div class="mb-4">
                <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600">Progress</span>
                    <span class="font-semibold">${p.completion_percentage}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-purple-600 h-2 rounded-full" style="width: ${p.completion_percentage}%"></div>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-gray-600">SPI:</span>
                    <span class="font-semibold ml-1">${p.spi}</span>
                </div>
                <div>
                    <span class="text-gray-600">Health:</span>
                    <span class="font-semibold ml-1">${p.health_score || 0}</span>
                </div>
                <div>
                    <span class="text-gray-600">Risks:</span>
                    <span class="font-semibold ml-1">${p.total_risks || 0}</span>
                </div>
                <div>
                    <span class="text-gray-600">PM:</span>
                    <span class="font-semibold ml-1 text-xs">${p.project_manager}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('projects-grid').innerHTML = html;
}

// Get status class
function getStatusClass(status) {
    const classes = {
        'on_track': 'bg-green-100 text-green-800',
        'at_risk': 'bg-orange-100 text-orange-800',
        'delayed': 'bg-red-100 text-red-800',
        'completed': 'bg-blue-100 text-blue-800',
        'cancelled': 'bg-gray-100 text-gray-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
}

// Show project detail
async function showProjectDetail(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}/`);
        const project = await response.json();
        
        document.getElementById('modal-project-name').textContent = project.name;
        document.getElementById('modal-content').innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold mb-2">Project Information</h4>
                        <dl class="text-sm space-y-2">
                            <div class="flex justify-between">
                                <dt class="text-gray-600">Status:</dt>
                                <dd class="font-semibold">${project.status}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-600">Completion:</dt>
                                <dd class="font-semibold">${project.completion_percentage}%</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-600">PM:</dt>
                                <dd class="font-semibold">${project.project_manager}</dd>
                            </div>
                        </dl>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">Performance Metrics</h4>
                        <dl class="text-sm space-y-2">
                            <div class="flex justify-between">
                                <dt class="text-gray-600">SPI:</dt>
                                <dd class="font-semibold">${project.spi}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-600">CPI:</dt>
                                <dd class="font-semibold">${project.cpi}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-600">Health Score:</dt>
                                <dd class="font-semibold">${project.health_score}</dd>
                            </div>
                        </dl>
                    </div>
                </div>
                
                <div>
                    <button onclick="getProjectAISummary(${projectId})" 
                            class="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
                        <i class="fas fa-robot mr-2"></i>Get AI Summary
                    </button>
                </div>
                
                <div id="project-ai-summary"></div>
            </div>
        `;
        
        document.getElementById('project-modal').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading project detail:', error);
    }
}

// Close modal
function closeModal() {
    document.getElementById('project-modal').classList.add('hidden');
}

// Filter projects
function filterProjects() {
    const status = document.getElementById('filter-status').value;
    const priority = document.getElementById('filter-priority').value;
    const search = document.getElementById('search-projects').value.toLowerCase();
    
    let filtered = allProjects.filter(p => {
        const matchStatus = !status || p.status === status;
        const matchPriority = !priority || p.priority === priority;
        const matchSearch = !search || 
            p.name.toLowerCase().includes(search) || 
            p.code.toLowerCase().includes(search);
        return matchStatus && matchPriority && matchSearch;
    });
    
    renderProjects(filtered);
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-priority').value = '';
    document.getElementById('search-projects').value = '';
    renderProjects(allProjects);
}

// AI Functions
async function getPortfolioSummary() {
    showAILoading();
    try {
        const response = await fetch(`${AI_BASE}/portfolio-summary/`);
        const data = await response.json();
        renderAIResponse(data);
    } catch (error) {
        showAIError('Error getting portfolio summary');
    }
}

async function getExecutiveReport() {
    showAILoading();
    try {
        const response = await fetch(`${AI_BASE}/executive-report/`);
        const data = await response.json();
        renderAIResponse(data);
    } catch (error) {
        showAIError('Error getting executive report');
    }
}

async function askAI() {
    const question = document.getElementById('ai-question').value.trim();
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    showAILoading();
    try {
        const response = await fetch(`${AI_BASE}/ask/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        renderAIResponse(data);
    } catch (error) {
        showAIError('Error getting AI response');
    }
}

async function getProjectAISummary(projectId) {
    const container = document.getElementById('project-ai-summary');
    container.innerHTML = '<div class="loading mx-auto"></div>';
    
    try {
        const response = await fetch(`${AI_BASE}/project-summary/${projectId}/`);
        const data = await response.json();
        container.innerHTML = `
            <div class="bg-purple-50 rounded-lg p-4">
                <h4 class="font-semibold mb-2">AI Analysis</h4>
                <pre class="text-sm whitespace-pre-wrap">${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<p class="text-red-600">Error loading AI summary</p>';
    }
}

function showAILoading() {
    document.getElementById('ai-response').innerHTML = '<div class="loading mx-auto"></div>';
}

function showAIError(message) {
    document.getElementById('ai-response').innerHTML = 
        `<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">${message}</div>`;
}

function renderAIResponse(data) {
    const html = `
        <div class="bg-purple-50 rounded-lg p-6">
            <pre class="whitespace-pre-wrap text-sm">${JSON.stringify(data, null, 2)}</pre>
        </div>
    `;
    document.getElementById('ai-response').innerHTML = html;
}

function showAddProject() {
    alert('Add project form would open here. For demo, use Django Admin or API to add projects.');
}

function getRiskAnalysis() {
    alert('Select a specific risk from a project to analyze it with AI.');
}
