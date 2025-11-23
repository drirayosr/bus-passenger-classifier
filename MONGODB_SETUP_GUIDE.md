le# MongoDB Atlas Setup Guide

Complete guide to set up MongoDB Atlas (free tier) for your bus passenger classifier project.

## Why MongoDB Atlas?

- ✅ **512 MB storage FREE forever**
- ✅ **No credit card required**
- ✅ Fast queries and filtering
- ✅ Cloud-hosted database
- ✅ Better than CSV for structured data
- ✅ Production-ready

---

## Step 1: Create MongoDB Account (5 minutes)

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up with:
   - Email address (or use Google/GitHub)
   - Password
3. **No credit card required!** ✅
4. Verify your email

---

## Step 2: Create Free Cluster (3 minutes)

After logging in:

1. Click **"Build a Database"** or **"Create"**
2. Choose **"M0 FREE"** tier (should be selected by default)
3. Settings:
   - **Provider**: AWS, Google Cloud, or Azure (any works)
   - **Region**: Choose closest to you
   - **Cluster Name**: `BusCluster` (or keep default)
4. Click **"Create"**
5. Wait ~3 minutes for cluster to be created

---

## Step 3: Configure Database Access (2 minutes)

### Create Database User:

1. In MongoDB dashboard, go to **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
3. Settings:
   - **Authentication Method**: Password # mJC3PfbRWi6gMcgZ
   - **Username**: `busadmin` (or choose your own)
   - **Password**: Click "Autogenerate Secure Password" (SAVE THIS!)
   - **Database User Privileges**: "Read and write to any database"
4. Click **"Add User"**

⚠️ **IMPORTANT**: Save your password! You'll need it for the connection string.

---

## Step 4: Configure Network Access (2 minutes)

### Whitelist Your IP:

1. Go to **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. Choose one:
   - **Option A**: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
     - ⚠️ Less secure but easier for testing
   - **Option B**: Click **"Add Current IP Address"**
     - ✅ More secure but need to update when IP changes
4. Click **"Confirm"**

---

## Step 5: Get Connection String (2 minutes)

1. Go back to **"Database"** (left sidebar)
2. Click **"Connect"** button on your cluster
3. Choose **"Drivers"**
4. Select:
   - **Driver**: Python
   - **Version**: 3.12 or later
5. Copy the connection string (looks like):
   ```
   mongodb+srv://busadmin:<password>@buscluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **Replace `<password>`** with your actual password from Step 3

Example final string:
```
mongodb+srv://busadmin:MySecurePass123@buscluster.abc12.mongodb.net/?retryWrites=true&w=majority
```

---

## Step 6: Configure Your Project (3 minutes)

### Option A: Using .env file (Recommended)

1. Copy the example file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` file:
   ```
   MONGODB_URI=mongodb+srv://busadmin:YourPassword@cluster.mongodb.net/
   USE_MONGODB=true
   ```

3. Load environment variables:
   ```powershell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
           [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
       }
   }
   ```

### Option B: Set directly in PowerShell

```powershell
$env:MONGODB_URI = "mongodb+srv://busadmin:YourPassword@cluster.mongodb.net/"
$env:USE_MONGODB = "true"
```

---

## Step 7: Install MongoDB Driver (1 minute)

```powershell
pip install pymongo dnspython
```

---

## Step 8: Upload Data to MongoDB (2 minutes)

```powershell
python upload_data_to_mongodb.py
```

You should see:
```
✅ Connected to MongoDB Atlas
✅ Using database: bus_classifier
✅ Uploaded XXX records to 'passengers' collection
✅ Uploaded XXX records to 'buses' collection
🎉 Upload complete!
```

---

## Step 9: Test the Dashboard

### Option A: Run locally
```powershell
streamlit run dashboard/app.py
```

### Option B: Run with Docker
```powershell
docker-compose up -d dashboard
```

Check the sidebar for:
- **✅ Connected to MongoDB Atlas**
- **✅ Loaded XXX records from MongoDB**

If you see this, MongoDB is working! 🎉

---

## Verify in MongoDB Atlas

1. Go to MongoDB Atlas dashboard
2. Click **"Browse Collections"** on your cluster
3. You should see:
   - Database: `bus_classifier`
   - Collections: `passengers`, `buses`
   - Documents: Your CSV data

---

## Troubleshooting

### ❌ "Connection timeout"
- Check Network Access settings
- Make sure your IP is whitelisted
- Try "Allow Access from Anywhere" for testing

### ❌ "Authentication failed"
- Check username and password in connection string
- Password must be URL-encoded (no special characters or use %XX encoding)
- Make sure you replaced `<password>` with actual password

### ❌ "MONGODB_URI not set"
- Load environment variables (see Step 6)
- Or set them directly in PowerShell

### 📁 Using Local Files Instead
If MongoDB isn't working, the dashboard will automatically fall back to local CSV files. You'll see:
- **📁 MongoDB not configured - using local files**

---

## Connection String Format

```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

- **username**: Database user from Step 3
- **password**: User's password (URL-encoded)
- **cluster**: Your cluster name (auto-generated)

---

## Security Best Practices

- ⚠️ **Never commit `.env` to Git** (already in `.gitignore`)
- ⚠️ **Never share your connection string**
- ✅ Use "Allow Access from Anywhere" only for development
- ✅ Create read-only users for production dashboard
- ✅ Rotate passwords regularly

---

## MongoDB Atlas Dashboard

Access at: https://cloud.mongodb.com/

Features:
- 📊 View collections and documents
- 📈 Monitor database performance
- 🔐 Manage users and access
- 📦 Database size and storage used

---

## Benefits Over CSV Files

| Feature | CSV Files | MongoDB |
|---------|-----------|---------|
| Size | Limited by disk | 512 MB free |
| Queries | Load entire file | Fast indexed queries |
| Updates | Rewrite file | Update single records |
| Filtering | Load then filter | Filter before loading |
| Concurrent Access | ❌ | ✅ |
| Cloud Access | ❌ | ✅ |

---

## Next Steps

1. ✅ Upload your data: `python upload_data_to_mongodb.py`
2. ✅ Test dashboard: `streamlit run dashboard/app.py`
3. ✅ Deploy to cloud (dashboard connects to MongoDB from anywhere)
4. 💡 Add more data - you have 512 MB to use!

---

## Need Help?

- MongoDB Docs: https://www.mongodb.com/docs/atlas/
- Python Driver: https://pymongo.readthedocs.io/
- Dashboard fallback: Works with local CSV if MongoDB not configured
