# Flask App - Quick Start Guide

## 🚀 How to Launch the App

### Option 1: Desktop Launcher (Recommended!)

**Simply double-click the desktop icon:**

```
Contractor Pay Tracker.command
```

That's it! The app will:
1. ✅ Activate the virtual environment
2. ✅ Install dependencies (first time only)
3. ✅ Find an available port automatically
4. ✅ Start the server

### Option 2: Terminal

```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker
./start_app.sh
```

---

## 📱 What You'll See

When the app starts, you'll see:

```
========================================
  Contractor Pay Tracker
========================================

✅ Virtual environment activated
✅ Dependencies installed

🚀 Starting Flask application...

============================================================
🚀 Contractor Pay Tracker - Flask App
============================================================

✅ Server starting on http://127.0.0.1:5555
✅ Local access: http://localhost:5555

📁 Upload files: http://localhost:5555/upload
📊 View files: http://localhost:5555/files

⚠️  Press CTRL+C to stop the server
============================================================
```

**Open your browser to:** `http://localhost:5555`

---

## 🎯 What Can You Do?

### 1. Upload Files (`/upload`)

- **Drag and drop** Excel files
- **Or click** "Choose File" button
- Supports `.xlsx` files only
- Shows upload progress
- Auto-validates file type

### 2. View Files Dashboard (`/files`)

- See all uploaded files
- **Filter by status:**
  - ✅ Completed
  - ⚠️ Completed with Warnings
  - ❌ Errors
  - 🔄 Processing

- **Filter by umbrella:**
  - NASA
  - PARASOL
  - GIANT
  - PAYSTREAM
  - BROOKSON
  - APSCo

- **Actions:**
  - View details
  - Delete file

### 3. View File Details (`/file/{id}`)

- File metadata
- **Validation Errors** (blocks import)
- **Validation Warnings** (allows import)
- Suggested fixes
- Delete functionality

---

## 🔧 Smart Port Selection

The app automatically handles port conflicts!

**Default behavior:**
- Tries port **5555** first
- If in use, tries **5556**
- If in use, tries **5557**
- Continues up to 100 ports

**Perfect for testing** when you have multiple servers running!

---

## 🛑 How to Stop

Press **CTRL+C** in the terminal window

---

## 🔄 How to Restart

Just run the desktop launcher again or:

```bash
./start_app.sh
```

---

## ⚙️ Configuration

### First Time Setup

1. Navigate to `flask-app/` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp flask-app/.env.example flask-app/.env
   ```

3. Edit `.env` with your AWS details:
   ```env
   AWS_REGION=eu-west-2
   DYNAMODB_TABLE_NAME=contractor-pay-development
   S3_BUCKET_NAME=contractor-pay-files-development-123456789012
   ```

---

## 📁 File Structure

```
flask-app/
├── app.py                 # Main Flask app (with smart port detection!)
├── templates/             # HTML pages
│   ├── upload.html       # Drag-and-drop upload
│   ├── files.html        # Files dashboard
│   ├── file_detail.html  # Validation viewer
│   └── contractors.html  # Contractors (coming soon)
├── requirements.txt       # Dependencies
└── .env                  # Your AWS config
```

---

## 🐛 Troubleshooting

### Desktop launcher doesn't work

Make sure it's executable:
```bash
chmod +x "/Users/gianlucaformica/Desktop/Contractor Pay Tracker.command"
chmod +x /Users/gianlucaformica/Projects/contractor-pay-tracker/start_app.sh
```

### Virtual environment issues

Recreate it:
```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r flask-app/requirements.txt
```

### Port still in use after 100 attempts

Check what's using ports:
```bash
lsof -i :5555
lsof -i :5556
# etc.
```

Kill a specific process:
```bash
kill -9 [PID]
```

### Browser shows "connection refused"

Make sure the app is running:
1. Check terminal for "Server starting on..." message
2. Try `http://127.0.0.1:[PORT]` instead of `localhost`

---

## 🎨 Current Status

### ✅ Working Features

- File upload page with drag-and-drop
- Files dashboard with filters
- File detail page with validation viewer
- DELETE functionality
- Smart port selection
- Desktop launcher

### 🚧 Mock Data (Not Yet Connected to AWS)

The app currently shows **mock data** for demonstration.

To connect to real AWS:
1. Deploy backend: `cd backend && sam deploy`
2. Update `.env` with real AWS resources
3. Implement boto3 calls in `app.py`

---

## 📚 Next Steps

### 1. Deploy AWS Backend

```bash
cd backend
sam build
sam deploy --guided
```

### 2. Update .env

Add your deployed resource names to `flask-app/.env`

### 3. Connect Flask to AWS

Implement real AWS calls in `app.py`:
- Upload to S3 via Lambda
- Query DynamoDB for files
- Display real validation results

---

## 💡 Tips

**During development:**
- The app auto-reloads when you save code changes
- Check terminal for error messages
- Use browser DevTools (F12) to debug JavaScript

**Testing multiple ports:**
- Open multiple terminals
- Run `./start_app.sh` in each
- Each instance gets its own port!

**Viewing logs:**
- All output appears in the terminal
- Structured JSON logs for AWS Lambda
- Flask debug toolbar in development mode

---

## 🎉 Enjoy!

You now have a fully functional Flask web app with smart port detection!

**Common URLs:**
- Upload: `http://localhost:5555/upload`
- Files: `http://localhost:5555/files`
- API: `http://localhost:5555/api/files`

Press CTRL+C to stop, double-click desktop icon to restart!
