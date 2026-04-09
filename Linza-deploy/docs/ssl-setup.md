# HTTPS/TLS Setup

## Option 1: Let's Encrypt (recommended for production)

### Prerequisites
- Domain name pointing to your server
- Port 80 and 443 accessible from internet

### Steps

1. Install certbot:
   ```bash
   apt-get install certbot
   ```

2. Obtain certificate:
   ```bash
   certbot certonly --standalone -d your-domain.com
   ```

3. Copy certificates:
   ```bash
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
   ```

4. Enable HTTPS in docker-compose:
   ```yaml
   nginx:
     volumes:
       - ./nginx/nginx-ssl.conf:/etc/nginx/nginx.conf:ro
       - ./ssl:/etc/nginx/ssl:ro
   ```

5. Restart: `docker compose up -d nginx`

### Auto-renewal
```bash
certbot renew --deploy-hook "docker compose restart nginx"
```
Add to crontab: `0 0 1 * * certbot renew ...`

## Option 2: Self-signed (development/testing)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=localhost"
```

Then follow steps 4-5 from Option 1.
