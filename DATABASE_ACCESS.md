# Database Access Guide - pgAdmin 4

This guide explains how to connect to the LexiGo PostgreSQL database on AWS EC2 from your local pgAdmin 4 client.

## Prerequisites

- pgAdmin 4 installed on your local machine
- SSH access to EC2 instance (LexiGo-KEY.pem file)
- PostgreSQL running on EC2 (port 5432)

## Connection Methods

### Method 1: SSH Tunnel (Recommended)

SSH tunneling is the most secure method as it doesn't require opening PostgreSQL port to the internet.

#### Step 1: Create SSH Tunnel

**On Windows (PowerShell or Command Prompt):**
```powershell
ssh -i "LexiGo-KEY.pem" -L 5433:localhost:5432 ubuntu@63.178.22.25 -N
```

**On Linux/Mac:**
```bash
ssh -i "LexiGo-KEY.pem" -L 5433:localhost:5432 ubuntu@63.178.22.25 -N
```

**What this does:**
- `-L 5433:localhost:5432` - Forwards local port 5433 to remote PostgreSQL port 5432
- `-N` - Doesn't execute remote commands (just tunnel)
- Keep this terminal window open while using pgAdmin

#### Step 2: Configure pgAdmin 4

1. **Open pgAdmin 4**
2. **Right-click "Servers"** → **Create** → **Server**
3. **General Tab:**
   - Name: `LexiGo EC2 Database`

4. **Connection Tab:**
   - Host: `localhost` (or `127.0.0.1`)
   - Port: `5433` (local tunnel port)
   - Maintenance database: `lexigo`
   - Username: `myuser`
   - Password: `lexigo2024`
   - Save password: ✓ (optional)

5. **Click "Save"**

#### Step 3: Connect
- Click on "LexiGo EC2 Database" in the server tree
- You should see the `lexigo` database with `words` and `user_notes` tables

---

### Method 2: Direct Connection (Requires Firewall Configuration)

⚠️ **Not recommended for production** - Opens database to internet

#### Step 1: Configure PostgreSQL to Accept Remote Connections

SSH into EC2:
```bash
ssh -i "LexiGo-KEY.pem" ubuntu@63.178.22.25
```

Edit PostgreSQL config:
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Find and change:
```
listen_addresses = 'localhost'
```
To:
```
listen_addresses = '*'
```

Edit pg_hba.conf:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add this line (replace YOUR_IP with your actual IP):
```
host    lexigo    myuser    YOUR_IP/32    scram-sha-256
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

#### Step 2: Configure AWS Security Group

1. Go to AWS Console → EC2 → Security Groups
2. Select your EC2 instance's security group
3. **Add Inbound Rule:**
   - Type: PostgreSQL (5432)
   - Source: My IP (or your specific IP)
   - Description: pgAdmin access

#### Step 3: Configure pgAdmin 4

1. **Open pgAdmin 4**
2. **Right-click "Servers"** → **Create** → **Server**
3. **General Tab:**
   - Name: `LexiGo EC2 Database (Direct)`

4. **Connection Tab:**
   - Host: `63.178.22.25` (EC2 public IP)
   - Port: `5432`
   - Maintenance database: `lexigo`
   - Username: `myuser`
   - Password: `lexigo2024`

5. **Click "Save"**

---

## Database Schema

### Tables

#### 1. words
```sql
id                  SERIAL PRIMARY KEY
word                VARCHAR(100) NOT NULL
polish_translation  VARCHAR(100) NOT NULL
example_sentence_1  TEXT NOT NULL
example_sentence_2  TEXT NOT NULL
example_sentence_3  TEXT NOT NULL
created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### 2. user_notes
```sql
id          SERIAL PRIMARY KEY
user_email  VARCHAR(255) NOT NULL
word_id     INTEGER NOT NULL (FOREIGN KEY → words.id)
notes       TEXT NOT NULL
created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
UNIQUE(user_email, word_id)
```

---

## Useful Queries

### View all words
```sql
SELECT * FROM words ORDER BY id;
```

### View all user notes with word details
```sql
SELECT 
    un.user_email,
    w.word,
    w.polish_translation,
    un.notes,
    un.updated_at
FROM user_notes un
JOIN words w ON un.word_id = w.id
ORDER BY un.updated_at DESC;
```

### Count notes per user
```sql
SELECT 
    user_email,
    COUNT(*) as notes_count
FROM user_notes
GROUP BY user_email
ORDER BY notes_count DESC;
```

### Add new word
```sql
INSERT INTO words (word, polish_translation, example_sentence_1, example_sentence_2, example_sentence_3)
VALUES (
    'your_word',
    'polish_translation',
    'Example sentence 1.',
    'Example sentence 2.',
    'Example sentence 3.'
);
```

---

## Troubleshooting

### SSH Tunnel Issues

**Problem:** "Connection refused" or "Unable to connect"
- **Solution:** Check if SSH tunnel is still running
- Restart the SSH tunnel command

**Problem:** "Port 5433 already in use"
- **Solution:** Use a different local port (e.g., 5434)
```bash
ssh -i "LexiGo-KEY.pem" -L 5434:localhost:5432 ubuntu@63.178.22.25 -N
```

### pgAdmin Connection Issues

**Problem:** "Could not connect to server"
- Check SSH tunnel is active (for Method 1)
- Verify credentials (username: myuser, password: lexigo2024)
- Check EC2 instance is running

**Problem:** "Password authentication failed"
- Verify password is correct: `lexigo2024`
- Check PostgreSQL user exists:
```bash
sudo -u postgres psql -c "\du"
```

### AWS Security Group

**Problem:** Can't connect with Method 2
- Verify security group allows PostgreSQL (5432) from your IP
- Check your current IP hasn't changed
- Wait 1-2 minutes after security group changes

---

## Security Best Practices

1. ✅ **Use SSH Tunnel (Method 1)** - Most secure, no internet exposure
2. ✅ **Restrict IP access** - Only allow your IP in security groups
3. ✅ **Use strong passwords** - Change default password `lexigo2024`
4. ✅ **Regular backups** - Backup database regularly
5. ❌ **Don't open 5432 to 0.0.0.0/0** - Never allow all IPs
6. ❌ **Don't commit passwords** - Keep .env file out of git

---

## Database Backup

### Create backup
```bash
ssh -i "LexiGo-KEY.pem" ubuntu@63.178.22.25
pg_dump -U myuser -d lexigo > lexigo_backup_$(date +%Y%m%d).sql
```

### Restore backup
```bash
psql -U myuser -d lexigo < lexigo_backup_20251113.sql
```

### Download backup to local machine
```bash
scp -i "LexiGo-KEY.pem" ubuntu@63.178.22.25:~/lexigo_backup_*.sql ./
```

---

## Quick Reference

**SSH Tunnel Command:**
```bash
ssh -i "LexiGo-KEY.pem" -L 5433:localhost:5432 ubuntu@63.178.22.25 -N
```

**pgAdmin Connection (via tunnel):**
- Host: `localhost`
- Port: `5433`
- Database: `lexigo`
- User: `myuser`
- Password: `lexigo2024`

**Direct Connection:**
- Host: `63.178.22.25`
- Port: `5432`
- Database: `lexigo`
- User: `myuser`
- Password: `lexigo2024`
