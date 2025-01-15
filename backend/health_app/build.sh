#!/usr/bin/env bash
# Exit on error
set -o errexit



# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser if not already exists..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email='admin@admin.com', password='admin"123')
    print('Superuser created')
EOF

echo "Setup completed successfully."
