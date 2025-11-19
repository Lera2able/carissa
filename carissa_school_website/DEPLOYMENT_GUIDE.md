# Carissa School Website - Deployment Guide

## Quick Start (Local Development)

1. **Navigate to the project folder**
```bash
cd carissa_school_website
```

2. **Install dependencies**
```bash
pip install -r requirements.txt --break-system-packages
```

3. **Run the application**
```bash
python app.py
```

4. **Access the website**
   Open your web browser and go to: `http://localhost:5000`

5. **Login as Admin**
   - Username: `admin`
   - Password: `admin123`

## Deployment Options

### Option 1: cPanel Deployment (Recommended for Shared Hosting)

1. **Upload Files**
   - Compress the entire `carissa_school_website` folder as a ZIP file
   - Login to your cPanel
   - Go to File Manager
   - Navigate to your public_html directory (or subdomain folder)
   - Upload and extract the ZIP file

2. **Setup Python Application**
   - In cPanel, find "Setup Python App"
   - Click "Create Application"
   - Select Python version: 3.9 or higher
   - Application root: `/home/yourusername/public_html/carissa_school_website`
   - Application URL: your domain or subdomain
   - Application startup file: `app.py`
   - Application entry point: `app`

3. **Install Dependencies**
   - Click "Enter to the virtual environment"
   - Run: `pip install -r requirements.txt`

4. **Configure Domain**
   - Point your domain or create a subdomain
   - Update DNS if necessary
   - Enable SSL certificate (recommended)

5. **Start Application**
   - Click "Start" in the Python App interface
   - Access your website via the configured domain

### Option 2: VPS/Cloud Server (DigitalOcean, Linode, AWS, etc.)

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install nginx
sudo apt install nginx -y
```

2. **Upload Project**
```bash
# Create directory
sudo mkdir -p /var/www/carissa
cd /var/www/carissa

# Upload your files (use SCP, SFTP, or Git)
# Then set permissions
sudo chown -R www-data:www-data /var/www/carissa
```

3. **Create Virtual Environment**
```bash
cd /var/www/carissa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

4. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/carissa.service
```

Add this content:
```ini
[Unit]
Description=Carissa School Website
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/carissa
Environment="PATH=/var/www/carissa/venv/bin"
ExecStart=/var/www/carissa/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/carissa
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/carissa/static;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/carissa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Start the Application**
```bash
sudo systemctl start carissa
sudo systemctl enable carissa
sudo systemctl status carissa
```

7. **Setup SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Option 3: PythonAnywhere (Free Tier Available)

1. **Create Account**: Sign up at pythonanywhere.com
2. **Upload Files**: Use their file browser or Git
3. **Create Web App**:
   - Go to Web tab
   - Add new web app
   - Choose Flask
   - Point to your app.py file
4. **Install Dependencies**: Use the Bash console
5. **Reload**: Click reload button

## Post-Deployment Steps

1. **Change Default Admin Password**
   - Login with admin/admin123
   - Go to User Management
   - Edit admin user and change password

2. **Update Secret Key**
   - Edit `app.py`
   - Change `app.secret_key` to a random string
   - Restart application

3. **Setup Backups**
   - Regular database backups (database/school.db)
   - Backup uploaded files (static/uploads/)

4. **Configure Email (Optional)**
   - For contact form functionality
   - Add email configuration in app.py

5. **Test All Features**
   - Test user creation
   - Upload test images
   - Add sample news
   - Create test student accounts

## Maintenance

### Regular Tasks
- Backup database weekly
- Monitor disk space (uploaded files)
- Update dependencies monthly
- Review user accounts quarterly

### Updating the Site
```bash
# Pull latest changes
git pull origin main  # if using Git

# Restart application
sudo systemctl restart carissa  # VPS
# OR click Reload in cPanel/PythonAnywhere
```

## Troubleshooting

### Application Won't Start
- Check Python version (3.9+)
- Verify all dependencies installed
- Check error logs
- Ensure database folder is writable

### Upload Errors
- Check folder permissions
- Verify MAX_CONTENT_LENGTH setting
- Ensure enough disk space

### Database Errors
- Check database/school.db permissions
- Re-run init_db() if needed
- Backup before any changes

## Security Checklist

- [ ] Change default admin password
- [ ] Update secret key in production
- [ ] Enable HTTPS/SSL
- [ ] Set proper file permissions
- [ ] Regular backups enabled
- [ ] Keep dependencies updated
- [ ] Monitor access logs

## Support

For deployment assistance:
- Email: carissaschool@telkomsa.net
- Phone: 013 656 1286

## Resources

- Flask Documentation: https://flask.palletsprojects.com/
- cPanel Documentation: https://docs.cpanel.net/
- Let's Encrypt: https://letsencrypt.org/
- PythonAnywhere: https://www.pythonanywhere.com/
