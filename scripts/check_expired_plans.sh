
#!/bin/bash

# Script to check for expired artist subscription plans
# This script should be added to crontab to run daily

# Set the project directory (update this path to match your deployment)
PROJECT_DIR="/var/www/wedmac-backend"  # Update this to your actual path

# Activate virtual environment (update path if different)
source $PROJECT_DIR/venv/bin/activate  # Update if your venv path is different

# Change to project directory
cd $PROJECT_DIR

# Run the Django management command
python manage.py check_expired_plans

# Deactivate virtual environment
deactivate

# Log the completion
echo "Expired plans check completed at $(date)" >> $PROJECT_DIR/logs/cron_expired_plans.log
