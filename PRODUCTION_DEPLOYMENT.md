# Production Deployment Guide

## Prerequisites

### 1. Install Redis
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

### 2. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE abkbet;
CREATE USER abkbet_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE abkbet TO abkbet_user;
\q

# macOS
brew install postgresql
brew services start postgresql
createdb abkbet
```

### 3. Get API Keys
- Sign up for API-Football: https://www.api-football.com/
- Get your API key from RapidAPI dashboard

## Installation Steps

### 1. Clone and Setup
```bash
cd /var/www/  # or your preferred directory
git clone <your-repo-url> abkbet
cd abkbet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production.example .env

# Edit .env with your actual values
nano .env
```

Update these critical values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `FOOTBALL_API_KEY`: Your API-Football key
- `FOOTBALL_API_ENABLED=true`
- `REDIS_URL`: Redis connection (usually redis://localhost:6379/0)
- `JWT_SECRET_KEY`: Generate a strong random key
- `SECRET_KEY`: Generate a strong random key

### 3. Database Migration
```bash
# Run database migrations
flask db upgrade

# Optionally migrate existing SQLite data
python scripts/migrate_to_postgres.py
```

### 4. Install Gunicorn and Supervisor
```bash
pip install gunicorn supervisor

# Create Gunicorn config
sudo nano /etc/supervisor/conf.d/abkbet.conf
```

Add this configuration:
```ini
[program:abkbet]
command=/var/www/abkbet/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app
directory=/var/www/abkbet
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/abkbet/app.err.log
stdout_logfile=/var/log/abkbet/app.out.log
environment=FLASK_ENV="production"
```

### 5. Setup Celery Workers
```bash
# Create Celery worker config
sudo nano /etc/supervisor/conf.d/abkbet-celery.conf
```

Add this configuration:
```ini
[program:abkbet-celery-worker]
command=/var/www/abkbet/venv/bin/celery -A celery_app worker --loglevel=info
directory=/var/www/abkbet
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/abkbet/celery-worker.err.log
stdout_logfile=/var/log/abkbet/celery-worker.out.log

[program:abkbet-celery-beat]
command=/var/www/abkbet/venv/bin/celery -A celery_app beat --loglevel=info
directory=/var/www/abkbet
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/abkbet/celery-beat.err.log
stdout_logfile=/var/log/abkbet/celery-beat.out.log
```

### 6. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/abkbet
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /static {
        alias /var/www/abkbet/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/abkbet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 8. Create Log Directory
```bash
sudo mkdir -p /var/log/abkbet
sudo chown www-data:www-data /var/log/abkbet
```

### 9. Start Services
```bash
# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Check status
sudo supervisorctl status
```

## Verify Deployment

### 1. Check Application
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"healthy"}
```

### 2. Check Celery Tasks
```bash
# View logs
sudo tail -f /var/log/abkbet/celery-worker.out.log

# Should see tasks executing:
# - fetch_live_matches (every 30 seconds)
# - update_match_odds (every 5 minutes)
# - fetch_upcoming_matches (every hour)
```

### 3. Check Redis
```bash
redis-cli ping
# Should return: PONG
```

### 4. Check PostgreSQL
```bash
psql -U abkbet_user -d abkbet -c "SELECT COUNT(*) FROM users;"
```

## Monitoring & Maintenance

### View Logs
```bash
# Application logs
sudo tail -f /var/log/abkbet/app.out.log

# Celery worker logs
sudo tail -f /var/log/abkbet/celery-worker.out.log

# Celery beat (scheduler) logs
sudo tail -f /var/log/abkbet/celery-beat.out.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart application
sudo supervisorctl restart abkbet

# Restart Celery workers
sudo supervisorctl restart abkbet-celery-worker
sudo supervisorctl restart abkbet-celery-beat

# Restart Nginx
sudo systemctl restart nginx
```

### Database Backup
```bash
# Create backup script
nano /home/backups/backup-abkbet.sh
```

Add:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U abkbet_user abkbet > /home/backups/abkbet_$TIMESTAMP.sql
# Keep only last 7 days
find /home/backups -name "abkbet_*.sql" -mtime +7 -delete
```

Make executable and add to crontab:
```bash
chmod +x /home/backups/backup-abkbet.sh
crontab -e
# Add: 0 2 * * * /home/backups/backup-abkbet.sh
```

## Security Checklist

- [ ] Changed all default passwords and secret keys
- [ ] Enabled firewall (ufw) and only opened ports 80, 443, 22
- [ ] Configured SSL/HTTPS with Let's Encrypt
- [ ] Set up database backups
- [ ] Restricted database access to localhost only
- [ ] Configured Redis password (if exposed)
- [ ] Set up fail2ban for SSH protection
- [ ] Configured proper file permissions (www-data user)
- [ ] Enabled application logging and monitoring
- [ ] Set up rate limiting in Nginx

## Scaling Tips

### Horizontal Scaling
```bash
# Add more Gunicorn workers
# In supervisor config: -w 8 (or more)

# Add more Celery workers
sudo nano /etc/supervisor/conf.d/abkbet-celery.conf
# Add multiple worker processes with different names
```

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_bets_user_id ON bets(user_id);
CREATE INDEX idx_bets_status ON bets(status);
CREATE INDEX idx_game_picks_status ON game_picks(status);
CREATE INDEX idx_game_picks_api_id ON game_picks(api_fixture_id);
```

### Redis Optimization
```bash
# Edit redis.conf
sudo nano /etc/redis/redis.conf

# Increase memory
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo supervisorctl tail -f abkbet stderr

# Check if port 5000 is available
sudo netstat -tlnp | grep 5000

# Test manually
cd /var/www/abkbet
source venv/bin/activate
python run.py
```

### Celery tasks not running
```bash
# Check Redis connection
redis-cli ping

# Check Celery logs
sudo supervisorctl tail -f abkbet-celery-worker

# Restart Celery
sudo supervisorctl restart abkbet-celery-worker abkbet-celery-beat
```

### Database connection issues
```bash
# Test connection
psql -U abkbet_user -d abkbet

# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection string in .env
```

## Performance Monitoring

Install monitoring tools:
```bash
# Install Prometheus node exporter
# Install Grafana for visualization
# Set up alerts for downtime
```

## Support

For issues, check:
1. Application logs: `/var/log/abkbet/`
2. Supervisor logs: `sudo supervisorctl tail -f <service-name>`
3. System logs: `journalctl -u nginx -f`
