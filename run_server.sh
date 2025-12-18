#!/bin/bash

echo "=========================================="
echo "PMO AI Assistant - Starting Server"
echo "=========================================="
echo ""
echo "🚀 Server will start on: http://localhost:8000"
echo "📊 Admin Interface: http://localhost:8000/admin/"
echo "📖 API Documentation: http://localhost:8000/api/docs/"
echo ""
echo "Admin Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "=========================================="
echo ""

cd /home/claude/pmo-ai-assistant
python manage.py runserver 0.0.0.0:8000
