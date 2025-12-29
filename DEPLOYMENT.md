# Deployment Guide - ABKBet

This guide covers deploying ABKBet to production environments.

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database backed up
- [ ] SSL/TLS certificates obtained
- [ ] Bitcoin network tested (testnet vs mainnet)
- [ ] Admin accounts created
- [ ] Rate limiting configured
- [ ] Logging setup
- [ ] Monitoring alerts configured
- [ ] Payment processing verified

## Environment Setup

### Production Environment Variables

Create a `.env` file with production values:

```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/abkbet_prod
JWT_SECRET_KEY=generate-a-long-random-key-here
BITCOIN_NETWORK=mainnet
BITCOIN_PRIVATE_KEY=your-bitcoin-private-key
WEBHOOK_SECRET=generate-a-long-random-key-here
```

### Generate Secure Keys

```python
import secrets
import string

# JWT Secret Key
jwt_key = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={jwt_key}")

# Webhook Secret
webhook_secret = secrets.token_urlsafe(32)
print(f"WEBHOOK_SECRET={webhook_secret}")
```

## Database Setup

### PostgreSQL

```bash
# Create database
createdb abkbet_prod

# Set proper permissions
psql -d abkbet_prod -c "CREATE USER abkbet WITH PASSWORD 'strong_password';"
psql -d abkbet_prod -c "ALTER ROLE abkbet SET client_encoding TO 'utf8';"
psql -d abkbet_prod -c "ALTER ROLE abkbet SET default_transaction_isolation TO 'read committed';"
psql -d abkbet_prod -c "ALTER ROLE abkbet SET default_transaction_deferrable TO on;"
psql -d abkbet_prod -c "ALTER ROLE abkbet SET default_timezone TO 'UTC';"
psql -d abkbet_prod -c "ALTER DATABASE abkbet_prod OWNER TO abkbet;"
```

### Initialize Database

```bash
python manage_db.py init
```

## Application Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Run with more workers for production
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 60 run:app
```

### Using Systemd Service

Create `/etc/systemd/system/abkbet.service`:

```ini
[Unit]
Description=ABKBet Bitcoin Betting Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/abkbet
Environment="PATH=/var/www/abkbet/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/abkbet/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable abkbet
sudo systemctl start abkbet
sudo systemctl status abkbet
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/abkbet
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - BITCOIN_NETWORK=mainnet
    depends_on:
      - db
    volumes:
      - ./:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=abkbet
      - POSTGRES_USER=abkbet
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:

```bash
docker-compose up -d
```

## Nginx Configuration

Create `/etc/nginx/sites-available/abkbet`:

```nginx
upstream abkbet {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 20M;

    location / {
        proxy_pass http://abkbet;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/abkbet/static/;
        expires 30d;
    }

    location /api/ {
        proxy_pass http://abkbet;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api_limit burst=100 nodelay;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/abkbet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS Certificate

Using Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly -a nginx -d your-domain.com
sudo certbot renew --dry-run
```

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/abkbet"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -U abkbet abkbet_prod | gzip > $BACKUP_DIR/abkbet_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "abkbet_*.sql.gz" -mtime +7 -delete
```

Schedule with cron:

```
0 2 * * * /usr/local/bin/backup_db.sh
```

### Application Backup

```bash
tar -czf abkbet_backup_$(date +%Y%m%d).tar.gz /var/www/abkbet
```

## Monitoring & Logging

### Application Logging

Update `run.py` for production logging:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/abkbet.log', 
                                   maxBytes=10240000, 
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
```

### System Monitoring

```bash
# Monitor CPU and Memory
top

# Monitor Network
netstat -tulpn | grep 5000

# Check service status
sudo systemctl status abkbet

# View logs
sudo journalctl -u abkbet -f
```

### Automated Monitoring

Use tools like:
- **Prometheus** for metrics
- **Grafana** for dashboards
- **ELK Stack** for logs
- **Sentry** for error tracking

## Security Hardening

### File Permissions

```bash
# Restrict access to .env
chmod 600 /var/www/abkbet/.env

# Restrict directory access
chmod 755 /var/www/abkbet
chmod 755 /var/www/abkbet/app
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Database Security

```bash
# Only allow local connections
# In postgresql.conf:
listen_addresses = 'localhost'

# Use strong passwords
ALTER USER abkbet WITH PASSWORD 'very_strong_password_here';
```

### Bitcoin Security

- Store private keys in encrypted format
- Use hardware wallet for cold storage
- Implement multi-sig wallets
- Regular security audits

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_bet_user_id ON bets(user_id);
CREATE INDEX idx_transaction_user_id ON transactions(user_id);
CREATE INDEX idx_bet_status ON bets(status);
```

### Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/payment/fee-estimate')
@cache.cached(timeout=300)
def get_fee_estimate():
    # Fee estimates cached for 5 minutes
    pass
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

## Troubleshooting

### 502 Bad Gateway

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check Nginx logs
tail -f /var/log/nginx/error.log

# Restart Gunicorn
sudo systemctl restart abkbet
```

### Database Connection Issues

```bash
# Check PostgreSQL
sudo -u postgres psql -l

# Check connection
psql -U abkbet -d abkbet_prod -h localhost
```

### High Memory Usage

```bash
# Monitor process
watch -n 1 'ps aux | grep gunicorn'

# Reduce worker count
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

## Maintenance

### Regular Updates

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Database Maintenance

```sql
-- Regular vacuum
VACUUM ANALYZE;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Rollback Procedure

In case of issues:

```bash
# Restore from backup
sudo systemctl stop abkbet
gunzip -c /backups/abkbet/abkbet_20240115.sql.gz | psql -U abkbet abkbet_prod
sudo systemctl start abkbet
```

## Scaling Strategies

### Horizontal Scaling

- Use load balancer (HAProxy, AWS ALB)
- Deploy multiple Gunicorn instances
- Use PostgreSQL replication for read scaling

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching

## Success Checklist

- [ ] Application running on production server
- [ ] Database backed up and verified
- [ ] SSL/TLS enabled and working
- [ ] Monitoring and alerts configured
- [ ] Logging enabled and reviewed
- [ ] Bitcoin network tested
- [ ] Admin accounts secured
- [ ] Rate limiting active
- [ ] Firewall configured
- [ ] Backups automated and tested
