# AWS EC2 Deployment Guide - RecruitPro 2

## 📋 Prerequisites Completed ✅
- AWS EC2 instance created and running
- Connected to instance via SSH
- System updated: `sudo apt update && sudo apt upgrade -y`
- Python 3.11+ installed
- Nginx installed
- Git installed

---

## 🔧 Step-by-Step Deployment

### Step 1: Install Additional Required Software

```bash
# Install Python virtual environment and pip
sudo apt install python3-venv python3-pip -y

# Install system dependencies for python-magic and pdf2image
sudo apt install libmagic1 poppler-utils -y

# Install Node.js and npm (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3 --version
node --version
npm --version
nginx -v
```

---

### Step 2: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/Nihith132/RecruitPro-2.git

# Navigate into project
cd RecruitPro-2

# Verify files
ls -la
```

---

### Step 3: Setup Backend

```bash
# Navigate to backend
cd ~/RecruitPro-2/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn
```

---

### Step 4: Configure Backend Environment Variables

```bash
# Create .env file from example
cd ~/RecruitPro-2/backend
cp .env.example .env

# Edit .env file with nano (or vim)
nano .env
```

**Update the following in `.env`:**

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/recruitpro?retryWrites=true&w=majority
DATABASE_NAME=recruitpro

# Groq AI (Llama Models)
GROQ_API_KEY=your_actual_groq_api_key

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=/home/ubuntu/RecruitPro-2/backend/firebase-credentials.json

# CORS Origins (UPDATE WITH YOUR EC2 PUBLIC IP OR DOMAIN)
CORS_ORIGINS=http://your-ec2-public-ip,http://localhost:5173
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter`

---

### Step 5: Upload Firebase Credentials

**On your local machine (new terminal):**

```bash
# Upload Firebase JSON to EC2
scp -i /path/to/your-key.pem \
  /Users/nihithreddy/Downloads/recruit-pro2-firebase-adminsdk-*.json \
  ubuntu@your-ec2-public-ip:~/RecruitPro-2/backend/firebase-credentials.json
```

**Back on EC2, verify:**

```bash
ls -la ~/RecruitPro-2/backend/firebase-credentials.json
```

---

### Step 6: Test Backend Manually

```bash
cd ~/RecruitPro-2/backend
source venv/bin/activate

# Test if backend starts
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Open another terminal and test:**
```bash
curl http://localhost:8000
```

**If it works, press `Ctrl + C` to stop.**

---

### Step 7: Create Systemd Service for Backend

```bash
# Create service file
sudo nano /etc/systemd/system/recruitpro-backend.service
```

**Paste this content:**

```ini
[Unit]
Description=RecruitPro Backend - FastAPI Application
After=network.target

[Service]
Type=notify
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/RecruitPro-2/backend
Environment="PATH=/home/ubuntu/RecruitPro-2/backend/venv/bin"
ExecStart=/home/ubuntu/RecruitPro-2/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/log/recruitpro-backend-access.log \
    --error-logfile /var/log/recruitpro-backend-error.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit** (`Ctrl + X`, `Y`, `Enter`)

**Enable and start the service:**

```bash
# Create log files
sudo touch /var/log/recruitpro-backend-access.log
sudo touch /var/log/recruitpro-backend-error.log
sudo chown ubuntu:www-data /var/log/recruitpro-backend-*.log

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable recruitpro-backend

# Start the service
sudo systemctl start recruitpro-backend

# Check status
sudo systemctl status recruitpro-backend

# View logs if there are issues
sudo journalctl -u recruitpro-backend -f
```

---

### Step 8: Setup Frontend

```bash
# Navigate to frontend
cd ~/RecruitPro-2/frontend

# Install dependencies
npm install

# Create production .env file
nano .env.production
```

**Add this content:**

```bash
VITE_API_URL=http://your-ec2-public-ip/api
```

**Save and exit** (`Ctrl + X`, `Y`, `Enter`)

**Build frontend:**

```bash
npm run build
```

This creates a `dist/` folder with production-ready files.

---

### Step 9: Configure Nginx

```bash
# Remove default Nginx config
sudo rm /etc/nginx/sites-enabled/default

# Create RecruitPro Nginx config
sudo nano /etc/nginx/sites-available/recruitpro
```

**Paste this configuration:**

```nginx
# Backend API Server
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-ec2-public-ip;  # Replace with your IP or domain
    
    client_max_body_size 50M;  # Allow larger file uploads
    
    # Frontend - React App
    location / {
        root /home/ubuntu/RecruitPro-2/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running AI requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
    }
}
```

**Save and exit** (`Ctrl + X`, `Y`, `Enter`)

**Enable the site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/recruitpro /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

### Step 10: Configure AWS Security Group

**In AWS Console:**

1. Go to **EC2 Dashboard** → **Security Groups**
2. Select your instance's security group
3. **Edit Inbound Rules** → **Add Rule**:
   - **Type**: HTTP
   - **Port**: 80
   - **Source**: Anywhere (0.0.0.0/0)
4. **Add another rule**:
   - **Type**: HTTPS
   - **Port**: 443
   - **Source**: Anywhere (0.0.0.0/0)
5. **Save rules**

---

### Step 11: Update CORS in Backend

```bash
nano ~/RecruitPro-2/backend/.env
```

**Update CORS_ORIGINS:**

```bash
CORS_ORIGINS=http://your-ec2-public-ip,https://your-ec2-public-ip
```

**Restart backend:**

```bash
sudo systemctl restart recruitpro-backend
```

---

### Step 12: Test Your Deployment

**Get your EC2 public IP:**
```bash
curl http://checkip.amazonaws.com
```

**Open in browser:**
```
http://your-ec2-public-ip
```

You should see the RecruitPro 2 login page!

---

## 🔍 Troubleshooting Commands

### Check Backend Service Status
```bash
sudo systemctl status recruitpro-backend
sudo journalctl -u recruitpro-backend -f  # Live logs
sudo journalctl -u recruitpro-backend --since "10 minutes ago"
```

### Check Backend Logs
```bash
sudo tail -f /var/log/recruitpro-backend-access.log
sudo tail -f /var/log/recruitpro-backend-error.log
```

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Test Backend Directly
```bash
curl http://localhost:8000
curl http://localhost:8000/api/analytics/dashboard
```

### Restart Services
```bash
sudo systemctl restart recruitpro-backend
sudo systemctl restart nginx
```

### Check Ports
```bash
sudo netstat -tulpn | grep :8000  # Backend
sudo netstat -tulpn | grep :80    # Nginx
```

---

## 🔒 Optional: Setup HTTPS with Let's Encrypt (SSL)

**After your app is working on HTTP:**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure Nginx for HTTPS
# Certificate auto-renews every 90 days
```

---

## 🔄 Updating Your Application

**When you push changes to GitHub:**

```bash
# SSH into EC2
cd ~/RecruitPro-2

# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt  # If new dependencies
sudo systemctl restart recruitpro-backend

# Update frontend
cd ../frontend
npm install  # If new dependencies
npm run build
sudo systemctl reload nginx
```

---

## 📊 Monitoring

### Set up a simple monitoring script
```bash
nano ~/monitor.sh
```

**Add:**
```bash
#!/bin/bash
echo "=== System Status ==="
free -h
df -h /
echo ""
echo "=== Backend Status ==="
sudo systemctl status recruitpro-backend --no-pager
echo ""
echo "=== Nginx Status ==="
sudo systemctl status nginx --no-pager
```

**Make executable:**
```bash
chmod +x ~/monitor.sh
./monitor.sh
```

---

## 🎯 Your Deployment is Complete!

**Access your application:**
- **Frontend**: `http://your-ec2-public-ip`
- **Backend API**: `http://your-ec2-public-ip/api`
- **Health Check**: `http://your-ec2-public-ip/health`

**Services:**
- Backend runs as systemd service (auto-starts on boot)
- Nginx serves frontend and proxies API requests
- All logs available in `/var/log/`

---

## ⚠️ Important Notes

1. **Backup your Firebase credentials** - Keep them secure
2. **MongoDB Atlas** - Whitelist your EC2 IP in MongoDB Network Access
3. **Environment variables** - Never commit `.env` to git
4. **Groq API limits** - Monitor usage at console.groq.com
5. **EC2 instance** - Don't stop the instance or you'll lose the public IP (unless using Elastic IP)

---

## 🆘 Common Issues & Solutions

### Issue: Backend won't start
**Solution:**
```bash
cd ~/RecruitPro-2/backend
source venv/bin/activate
python main.py  # Check for errors
```

### Issue: Frontend shows blank page
**Solution:**
```bash
# Check browser console for errors
# Update VITE_API_URL in frontend/.env.production
# Rebuild: npm run build
```

### Issue: 502 Bad Gateway
**Solution:**
```bash
# Backend is down
sudo systemctl restart recruitpro-backend
sudo systemctl status recruitpro-backend
```

### Issue: CORS errors
**Solution:**
```bash
# Add your domain/IP to backend/.env CORS_ORIGINS
nano ~/RecruitPro-2/backend/.env
sudo systemctl restart recruitpro-backend
```

### Issue: MongoDB connection timeout
**Solution:**
- Add EC2 public IP to MongoDB Atlas Network Access (whitelist)
- Or use 0.0.0.0/0 for testing (not recommended for production)

---

**Need help? Check logs first:**
```bash
sudo journalctl -u recruitpro-backend -f
sudo tail -f /var/log/nginx/error.log
```

Good luck with your deployment! 🚀
