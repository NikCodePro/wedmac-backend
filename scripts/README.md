# Auto Expire Plans Setup

This directory contains scripts to automatically check for expired artist subscription plans.

## Files

- `check_expired_plans.sh` - Linux bash script to run the expiration check
- `README.md` - This documentation file

## Setup Instructions

### Linux Server Cron Job Setup

1. **SSH into your server**
   ```bash
   ssh ubuntu@your-server-ip
   ```

2. **Navigate to your project directory**
   ```bash
   cd /var/www/wedmac-backend
   ```

3. **Update the script paths** (if needed)
   - Edit `scripts/check_expired_plans.sh`
   - Update `PROJECT_DIR` to match your actual project path
   - Update the virtual environment path if different

4. **Make the script executable**
   ```bash
   chmod +x scripts/check_expired_plans.sh
   ```

5. **Test the script manually**
   ```bash
   ./scripts/check_expired_plans.sh
   ```

6. **Add to crontab for hourly execution**
   ```bash
   crontab -e
   ```

7. **Add this line to run every hour**
   ```
   0 * * * * /var/www/wedmac-backend/scripts/check_expired_plans.sh
   ```

   **Cron schedule options:**
   - `0 * * * *` - Every hour at minute 0
   - `*/30 * * * *` - Every 30 minutes
   - `0 2 * * *` - Daily at 2:00 AM
   - `0 */6 * * *` - Every 6 hours
   - `0 2 * * 1` - Every Monday at 2:00 AM

8. **Verify cron job is added**
   ```bash
   crontab -l
   ```

9. **Check logs after first run**
   ```bash
   tail -f logs/cron_expired_plans.log
   ```

## Manual Testing

You can also run the script manually:

```cmd
# From the project root directory
scripts\check_expired_plans.sh
```

Or run the Django command directly:

```cmd
python manage.py check_expired_plans
```

## Logs

- Check `logs/cron_expired_plans.log` for execution logs
- Django logs will show detailed information about processed expirations

## Troubleshooting

1. **Cron job doesn't run**: Check `/var/log/syslog` or `/var/log/cron` for errors
2. **Script permission issues**: Ensure the script is executable with `chmod +x`
3. **Virtual environment issues**: Ensure the virtual environment path is correct
4. **Path issues**: Update the `PROJECT_DIR` variable in the script if your path is different
5. **Django settings issues**: Make sure DJANGO_SETTINGS_MODULE is set correctly

## Production Deployment

For production servers:

1. Update the `PROJECT_DIR` path in the script to match your production path
2. Ensure the virtual environment is properly set up
3. Test the script in the production environment
4. Set up appropriate monitoring for the logs
