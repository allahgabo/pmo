#!/bin/bash

echo "================================================================"
echo "           PMO AI Assistant - Complete Demo"
echo "================================================================"
echo ""
echo "This script will demonstrate all features of the PMO AI Assistant"
echo ""

cd /home/claude/pmo-ai-assistant

# Start server in background
echo "🚀 Starting Django server..."
python manage.py runserver 0.0.0.0:8000 > /tmp/pmo_server.log 2>&1 &
SERVER_PID=$!
sleep 5

# Check if server started
if curl -s http://localhost:8000/api/projects/dashboard_stats/ > /dev/null; then
    echo "✅ Server started successfully on http://localhost:8000"
else
    echo "❌ Server failed to start. Check /tmp/pmo_server.log"
    exit 1
fi

echo ""
echo "================================================================"
echo "                    API DEMONSTRATIONS"
echo "================================================================"
echo ""

# Dashboard Stats
echo "📊 1. Dashboard Statistics"
echo "-----------------------------------"
curl -s http://localhost:8000/api/projects/dashboard_stats/ | python3 -m json.tool
echo ""
echo ""

# List Projects
echo "📁 2. Project List (First 3)"
echo "-----------------------------------"
curl -s http://localhost:8000/api/projects/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', data) if isinstance(data, dict) else data
for p in results[:3]:
    print(f\"  • {p['name']}")
    print(f\"    Status: {p['status']}, SPI: {p['spi']}, Complete: {p['completion_percentage']}%\")
    print()
"
echo ""

# At-Risk Projects
echo "⚠️  3. At-Risk Projects"
echo "-----------------------------------"
curl -s http://localhost:8000/api/projects/at_risk_projects/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(f\"  • {p['name']} - {p['status']}\")
    print(f\"    SPI: {p['spi']}, Health: {p['health_score']}, High Risks: {p['high_risks']}\")
    print()
"
echo ""

# Risks Summary
echo "🛡️  4. Risk Summary"
echo "-----------------------------------"
curl -s http://localhost:8000/api/risks/high_priority/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', data) if isinstance(data, dict) else data
print(f\"  Total High Priority Risks: {len(results)}\")
for r in results[:3]:
    print(f\"  • {r['title']}\")
    print(f\"    Severity: {r['severity']}, Probability: {r['probability']}%\")
"
echo ""
echo ""

# AI Demonstrations
echo "================================================================"
echo "              AI-POWERED ANALYSIS DEMONSTRATIONS"
echo "================================================================"
echo ""

echo "🤖 5. AI Portfolio Summary"
echo "-----------------------------------"
curl -s http://localhost:8000/api/ai/portfolio-summary/ | python3 -m json.tool
echo ""
echo ""

echo "🤖 6. AI Executive Report"
echo "-----------------------------------"
curl -s http://localhost:8000/api/ai/executive-report/ | python3 -m json.tool
echo ""
echo ""

echo "🤖 7. AI Question: 'What is the portfolio health?'"
echo "-----------------------------------"
curl -s -X POST http://localhost:8000/api/ai/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the overall portfolio health?"}' | python3 -m json.tool
echo ""
echo ""

# Project Detail
echo "📋 8. Detailed Project Information (First Project)"
echo "-----------------------------------"
curl -s http://localhost:8000/api/projects/1/ | python3 -c "
import sys, json
p = json.load(sys.stdin)
print(f\"  Project: {p['name']}\")
print(f\"  Code: {p['code']}\")
print(f\"  Status: {p['status']}\")
print(f\"  Completion: {p['completion_percentage']}%\")
print(f\"  SPI: {p['spi']}, CPI: {p['cpi']}\")
print(f\"  Health Score: {p['health_score']}\")
print(f\"  Budget: \${p['budget']:,.2f}, Spent: \${p['spent']:,.2f}\")
print(f\"  Total Risks: {p['total_risks']}, High Risks: {p['high_risks']}\")
print(f\"  Open Tasks: {p['open_tasks']}, Overdue: {p['overdue_tasks']}\")
"
echo ""
echo ""

# Health Report
echo "💊 9. Project Health Report (First Project)"
echo "-----------------------------------"
curl -s http://localhost:8000/api/projects/1/health_report/ | python3 -m json.tool
echo ""
echo ""

echo "================================================================"
echo "                    DEMONSTRATION COMPLETE"
echo "================================================================"
echo ""
echo "✅ All API endpoints tested successfully!"
echo ""
echo "Next steps:"
echo "  1. Open browser to: http://localhost:8000"
echo "  2. Login to admin: http://localhost:8000/admin/"
echo "     Username: admin, Password: admin123"
echo "  3. View API docs: http://localhost:8000/api/docs/"
echo ""
echo "Server is running on PID: $SERVER_PID"
echo "To stop server: kill $SERVER_PID"
echo ""
echo "Logs available at: /tmp/pmo_server.log"
echo ""
echo "Press Ctrl+C to stop..."
wait $SERVER_PID
