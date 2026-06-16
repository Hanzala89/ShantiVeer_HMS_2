# SantiVeer HMS — Hospital Management System

A Django-based Hospital Management System with OPD, IPD, Lab, Pharmacy, Prescriptions, Bed Management, and Automatic Backup.

---

## Quick Start (Development)

```bash
# 1. Clone and enter project
cd "SantiVeer HMS"

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit environment file
cp .env.example .env
# Edit .env — set DJANGO_DEBUG=True for dev
# Default uses SQLite (no extra setup needed, DB name: ShantiVeer_db)
# To use MySQL instead, set USE_MYSQL=True and fill in DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 5. Run migrations
python manage.py migrate



# 6. Seed demo data (optional)
python manage.py seed_database

# 7. Create superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Production Deployment

### Environment Variables

Set all variables from `.env.example` in your environment:

```bash
export DJANGO_SECRET_KEY="your-long-random-key"
export DJANGO_DEBUG=False
export ALLOWED_HOSTS="yourdomain.com"
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Run with Gunicorn

```bash
gunicorn SantiVeer_hms.wsgi:application \
  --workers 3 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## Automatic Backup (No Physical Media Required)

The backup system creates a ZIP of the database (and media folder if present) stored in the `backups/` directory. No cloud or physical media needed.

### Setup Automatic Backup (Linux Cron)

```bash
# Edit crontab
crontab -e

# Add this line to run at 2 AM every day:
0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py run_scheduled_backup >> logs/backup.log 2>&1
```

### Setup via Admin Panel

1. Log in as admin → navigate to **Dashboard → Backup**
2. Select a schedule: Daily / Weekly / Monthly / Yearly
3. Click **Save Schedule**
4. The cron job above will pick it up automatically

### Manual Backup

Go to **Dashboard → Backup → Backup Now**

---

## Security Features

- 🔐 Two-Factor Authentication (Email OTP) on every login
- 🛡️ Brute-force login protection (rate limiting by IP)
- 🔒 CSRF protection on all forms
- 🔑 Cryptographically secure OTP generation
- 🚫 Path traversal protection on backup downloads
- 📋 Security headers (HSTS, X-Frame-Options, etc.) in production
- ⏰ Session expiry after 8 hours

---

## Module Overview

| Module | URL Prefix | Description |
|--------|-----------|-------------|
| OPD | `/opd/` | Outpatient registrations & visits |
| IPD | `/ipd/` | Inpatient admissions & management |
| Lab | `/lab/` | Lab tests & investigation reports |
| Pharmacy | `/pharmacy/` | Stock, purchases & sales |
| Prescription | `/prescription/` | Doctor prescriptions |
| UHID | `/uhid/` | Patient master records |
| Income | `/income/` | Daybook & billing |
| Masterdata | `/master/` | Doctor list & lab interpretations |
| Backup | `/backup/` | DB backup & schedule |

---

## Cron Job Reference

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && python manage.py run_scheduled_backup >> logs/backup.log 2>&1
```
