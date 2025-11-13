# Google OAuth Setup Instructions

## Important: Domain Requirement

Google OAuth does NOT accept raw IP addresses. You must use a domain name.

### Quick Solution: Use nip.io (Free DNS Service)

Instead of http://63.178.22.25:5000, use:
**http://63.178.22.25.nip.io:5000**

This automatically resolves to your IP address and works with Google OAuth!

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it "LexiGo"

## Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Fill in:
   - App name: **LexiGo**
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue** through all screens

## Step 3: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Application type: **Web application**
4. Name: **LexiGo Web Client**
5. Under **Authorized redirect URIs**, add:
   ```
   http://63.178.22.25.nip.io:5000/login/callback
   ```
6. Click **Create**
7. **Copy the Client ID and Client Secret** (you'll need these next)

## Step 4: Update Environment Variables on Server

1. SSH into your server:
   ```bash
   ssh -i "LexiGo-KEY.pem" ubuntu@63.178.22.25
   ```

2. Edit the .env file:
   ```bash
   nano ~/lexigo-app/.env
   ```

3. Replace PLACEHOLDER values with your actual credentials:
   ```
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   SECRET_KEY=any-random-long-string-here
   APP_URL=http://63.178.22.25.nip.io:5000
   ```

4. Save: Press `Ctrl+O`, `Enter`, then `Ctrl+X`

## Step 5: Restart the Application

```bash
sudo systemctl restart lexigo.service
sudo systemctl status lexigo.service
```

Check it's running (should show "active (running)")

## Step 6: Test the Login!

1. Open browser and go to: **http://63.178.22.25.nip.io:5000**
2. You should see the login page
3. Click **"Sign in with Google"**
4. Authorize the app
5. Success! You should see the word learning interface

---

## Alternative: Get a Real Domain (Recommended for Production)

For a production app, consider:

1. **Buy a domain** (from Namecheap, GoDaddy, etc.) - costs ~$10/year
2. **Point domain to EC2**: Create an A record pointing to 63.178.22.25
3. **Use in OAuth**: http://yourdomain.com:5000/login/callback
4. **Add HTTPS**: Use Let's Encrypt (free SSL certificate)

---

## Troubleshooting

**"redirect_uri_mismatch" error:**
- Make sure the URI in Google Console EXACTLY matches: `http://63.178.22.25.nip.io:5000/login/callback`
- No trailing slash, correct port number

**Login doesn't work:**
```bash
sudo journalctl -u lexigo.service -f
```
Check logs for errors

**Port not accessible:**
- Verify AWS Security Group allows port 5000 inbound traffic

**nip.io not resolving:**
- Try: `ping 63.178.22.25.nip.io` (should return 63.178.22.25)
- Alternative: Use sslip.io instead: `63.178.22.25.sslip.io`
