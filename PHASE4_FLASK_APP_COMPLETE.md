# Phase 4: Flask Web Application ✅

## What Was Built

### 🎯 Complete Flask Web Application

A fully functional web interface for the Contractor Pay Tracker with:

- ✅ **Smart port detection** (starts at 5555, finds next available)
- ✅ **Virtual environment setup**
- ✅ **Desktop launcher** (double-click to start)
- ✅ **Drag-and-drop file upload**
- ✅ **Files management dashboard**
- ✅ **Validation errors viewer**
- ✅ **DELETE functionality**
- ✅ **Clean, modern UI** (no frameworks, pure CSS)

---

## 🚀 How to Use

### Desktop Launcher (Easiest!)

**Double-click this icon on your desktop:**

```
Contractor Pay Tracker.command
```

**What happens automatically:**
1. Activates virtual environment (creates if needed)
2. Installs dependencies (first run only)
3. Finds available port (5555, 5556, 5557, etc.)
4. Starts Flask server
5. Shows URL in terminal

**Terminal output:**
```
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

**Then open:** `http://localhost:5555` in your browser

---

## 📱 Features

### 1. File Upload Page (`/upload`)

**Features:**
- Drag-and-drop interface
- Click to browse files
- File type validation (.xlsx only)
- File size display
- Upload progress bar
- Recent uploads list

**Usage:**
1. Drag an Excel file onto the upload area
2. Or click "Choose File" button
3. Review file details
4. Click "Upload"
5. See progress bar
6. Get confirmation

### 2. Files Dashboard (`/files`)

**Features:**
- Table view of all files
- Filter by status dropdown
- Filter by umbrella company
- Refresh button
- View details button
- Delete button with confirmation

**Filters:**
- **Status:** All, Completed, Completed with Warnings, Error, Processing
- **Umbrella:** All, NASA, PARASOL, GIANT, PAYSTREAM, BROOKSON, APSCo

**Columns:**
- Filename
- Umbrella company
- Period number
- Status badge (colored)
- Record count
- Upload timestamp
- Actions (View, Delete)

### 3. File Detail Page (`/file/{id}`)

**Features:**
- File metadata display
- Status badge
- Validation errors section (CRITICAL)
- Validation warnings section (NON-BLOCKING)
- Suggested fixes
- Delete button

**Error Display:**
- Row number
- Contractor name
- Error message
- Suggested fix (if available)

**Warning Display:**
- Row number
- Warning message
- Resolution notes (e.g., "Fuzzy matched: Jon → Jonathan")

### 4. Contractors Page (`/contractors`)

**Status:** Placeholder for future development

**Planned Features:**
- View all contractors
- See umbrella associations
- Payment history
- Add/edit contractors

---

## 🔧 Smart Port Selection

### How It Works

The app automatically finds an available port:

```python
def find_available_port(start_port=5555, max_attempts=100):
    """
    Find an available port starting from start_port
    Tries ports sequentially until one is available
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result != 0:  # Port is available
                return port
        except socket.error:
            continue

    return start_port + max_attempts  # Fallback
```

### Port Selection Logic

- **Default start:** Port 5555
- **If in use:** Tries 5556
- **If in use:** Tries 5557
- **Continues:** Up to 100 ports (5555-5655)
- **Fallback:** Port 5655 if all fail

### Perfect for Testing

When you have multiple test servers running throughout the day:
- First instance: Port 5555
- Second instance: Port 5556
- Third instance: Port 5557
- Etc.

**No manual port configuration needed!**

---

## 📁 File Structure

```
flask-app/
├── app.py                          # Main Flask app with port detection
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                           # Your AWS config (create from example)
├── README.md                       # Full documentation
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with nav
│   ├── upload.html                # Drag-and-drop upload
│   ├── files.html                 # Files dashboard
│   ├── file_detail.html           # Validation viewer
│   ├── contractors.html           # Contractors (placeholder)
│   ├── 404.html                   # Not found page
│   └── 500.html                   # Error page
└── static/                         # Static assets
    ├── css/                       # CSS files (inline for now)
    └── js/                        # JavaScript (inline for now)

Desktop/
└── Contractor Pay Tracker.command  # Desktop launcher

Project Root/
└── start_app.sh                    # Startup script
```

---

## 🎨 UI Design

### Design Principles

- **Clean & Simple** - No heavy frameworks
- **Modern** - Professional appearance
- **Responsive** - Works on all screen sizes
- **Accessible** - Clear labels and actions

### Color Scheme

- **Primary:** #3498db (blue)
- **Success:** #27ae60 (green)
- **Warning:** #f39c12 (orange)
- **Error:** #e74c3c (red)
- **Background:** #f5f5f5 (light gray)
- **Header:** #2c3e50 (dark blue)

### Status Badges

- **COMPLETED:** Green badge
- **COMPLETED_WITH_WARNINGS:** Yellow badge
- **ERROR:** Red badge
- **PROCESSING:** Blue badge
- **UPLOADED:** Gray badge

### Components

**Buttons:**
- Primary (blue)
- Success (green)
- Danger (red)

**Tables:**
- Clean borders
- Hover effects
- Responsive columns

**Forms:**
- Drag-and-drop areas
- File validation
- Progress indicators

---

## 🔌 API Endpoints

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

Body: file (Excel .xlsx)

Response: {
    "message": "File uploaded successfully",
    "filename": "NASA_01092025.xlsx",
    "size": 12345,
    "status": "pending"
}
```

### List Files
```http
GET /api/files

Response: {
    "files": [
        {
            "file_id": "f001",
            "filename": "NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx",
            "umbrella": "NASA",
            "period": 8,
            "status": "COMPLETED",
            "uploaded_at": "2025-09-01T14:30:00Z",
            "records": 14
        }
    ]
}
```

### File Details
```http
GET /api/file/{file_id}

Response: {
    "file_id": "f001",
    "filename": "...",
    "umbrella": "NASA",
    "period": 8,
    "status": "COMPLETED_WITH_WARNINGS",
    "total_records": 14,
    "valid_records": 14,
    "errors": [],
    "warnings": [
        {
            "row_number": 5,
            "warning_type": "FUZZY_NAME_MATCH",
            "warning_message": "Name 'Jon Mays' matched to 'Jonathan Mays' with 87% confidence",
            "resolution_notes": "Fuzzy matched: jon mays → Jonathan Mays"
        }
    ]
}
```

### Delete File
```http
DELETE /api/file/{file_id}

Response: {
    "message": "File f001 deleted successfully",
    "status": "deleted"
}
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# AWS Configuration
AWS_REGION=eu-west-2
AWS_PROFILE=default

# DynamoDB
DYNAMODB_TABLE_NAME=contractor-pay-development

# S3
S3_BUCKET_NAME=contractor-pay-files-development-123456789012

# API Gateway (optional)
API_GATEWAY_URL=https://your-api-id.execute-api.eu-west-2.amazonaws.com/prod
```

### First Time Setup

```bash
# Navigate to flask-app
cd flask-app

# Create .env from example
cp .env.example .env

# Edit .env with your AWS details
nano .env
```

---

## 🧪 Testing

### Manual Testing

```bash
# Start the app
./start_app.sh

# In browser, test:
1. Navigate to http://localhost:5555/upload
2. Drag and drop a test Excel file
3. Verify file info displays
4. Click Upload
5. Check progress bar
6. Verify success message

7. Navigate to /files
8. Verify files list displays
9. Test status filter
10. Test umbrella filter
11. Click "View" on a file

12. Verify file details page
13. Check errors/warnings display
14. Test Delete button
```

### Port Conflict Testing

```bash
# Terminal 1
./start_app.sh
# Should start on port 5555

# Terminal 2 (while Terminal 1 is running)
./start_app.sh
# Should auto-detect and start on port 5556

# Terminal 3
./start_app.sh
# Should start on port 5557

# etc.
```

---

## 🚧 Current Status

### ✅ Completed Features

- Flask app with auto-reload
- Smart port detection (5555+)
- Virtual environment setup
- Desktop launcher script
- Drag-and-drop file upload
- Files dashboard with filters
- File detail page with validation viewer
- DELETE functionality with confirmation
- Clean, modern UI
- Responsive design
- Error handling (404, 500)
- API endpoints structure

### 🚧 Mock Data

**Currently using mock data for:**
- File list (`/api/files`)
- File details (`/api/file/{id}`)
- Upload response

**To connect to real AWS:**
1. Deploy backend infrastructure
2. Update `.env` with resource names
3. Implement boto3 calls in `app.py`:
   - Upload files to S3
   - Query DynamoDB
   - Invoke Lambda functions

### 🔜 Future Enhancements

- [ ] Real AWS integration (boto3)
- [ ] Authentication/login
- [ ] User management
- [ ] Contractor management UI
- [ ] Reporting/analytics dashboard
- [ ] Export functionality (CSV, PDF)
- [ ] Real-time processing status updates
- [ ] Email notifications
- [ ] Audit log viewer

---

## 📦 Dependencies

### Python Packages

```
Flask==3.0.0          # Web framework
boto3==1.34.17        # AWS SDK
python-dotenv==1.0.0  # Environment variables
Werkzeug==3.0.1       # WSGI utilities
```

### Installation

```bash
# Automatic (via launcher)
# Just double-click the desktop icon!

# Manual
pip install -r flask-app/requirements.txt
```

---

## 🐛 Troubleshooting

### Desktop Launcher Doesn't Work

**Make executable:**
```bash
chmod +x "/Users/gianlucaformica/Desktop/Contractor Pay Tracker.command"
chmod +x /Users/gianlucaformica/Projects/contractor-pay-tracker/start_app.sh
```

### Virtual Environment Issues

**Recreate:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r flask-app/requirements.txt
```

### Port Already in Use (All 100 Ports!)

**Check what's using ports:**
```bash
lsof -i :5555
lsof -i :5556
# etc.
```

**Kill processes:**
```bash
kill -9 [PID]
```

### Browser Shows "Connection Refused"

**Check:**
1. Is the app running? (Check terminal)
2. Is the port correct? (Check terminal output)
3. Try `http://127.0.0.1:5555` instead of `localhost`

### Dependencies Won't Install

**Upgrade pip:**
```bash
pip install --upgrade pip
pip install -r flask-app/requirements.txt
```

---

## 💡 Development Tips

### Auto-Reload

The app automatically reloads when you save code changes:
- Edit `app.py`, save
- Edit templates, save
- Changes appear immediately (refresh browser)

### Debug Mode

Debug mode is enabled by default in development:
- Detailed error pages
- Stack traces
- Auto-reload on code changes

### View Logs

All output appears in the terminal:
```
✅ Server starting on http://127.0.0.1:5555
127.0.0.1 - - [01/Sep/2025 14:30:00] "GET /upload HTTP/1.1" 200 -
127.0.0.1 - - [01/Sep/2025 14:30:05] "POST /api/upload HTTP/1.1" 200 -
```

### Browser DevTools

Press **F12** to open:
- Console for JavaScript errors
- Network tab for API calls
- Elements tab for CSS debugging

---

## 🎉 Success!

You now have a fully functional Flask web application with:

✅ Smart port detection (handles conflicts automatically)
✅ Desktop launcher (double-click to start)
✅ Modern, clean UI (drag-and-drop uploads)
✅ Files management (dashboard with filters)
✅ Validation viewer (errors & warnings)
✅ DELETE functionality (with confirmation)

**Next Steps:**
1. Deploy AWS backend
2. Update `.env` with real resources
3. Connect Flask to AWS (implement boto3 calls)
4. Test with real Period 8 files

---

## 📚 Documentation

- `flask-app/README.md` - Full technical documentation
- `FLASK_APP_GUIDE.md` - Quick start guide
- `TESTING.md` - Testing procedures
- `.env.example` - Configuration template

---

**Ready to use! Double-click the desktop icon to start.**

Press **CTRL+C** to stop the server.
