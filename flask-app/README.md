# Contractor Pay Tracker - Flask Web Application

Simple, clean web interface for managing contractor pay files.

## Features

✅ **File Upload** - Drag and drop Excel file uploads
✅ **Files Dashboard** - View and manage all uploaded files
✅ **Validation Viewer** - See errors and warnings for each file
✅ **Smart Port Selection** - Automatically finds available port (starting at 5555)
✅ **DELETE Functionality** - Soft delete files and records

## Quick Start

### Desktop Launcher (Easiest!)

**Double-click the desktop icon:**
```
Contractor Pay Tracker.command
```

The app will:
1. Activate the virtual environment (creates if needed)
2. Install dependencies (first run only)
3. Find an available port (5555, 5556, 5557, etc.)
4. Open at: `http://localhost:[PORT]`

### Manual Start

```bash
# From project root
cd /Users/gianlucaformica/Projects/contractor-pay-tracker

# Run the start script
./start_app.sh
```

### Command Line

```bash
# Activate virtual environment
source venv/bin/activate

# Change to flask-app directory
cd flask-app

# Run the app
python app.py
```

## Port Selection

The app automatically finds an available port:

- **Default start port:** 5555
- **If port is in use:** Tries 5556, 5557, 5558, etc.
- **Max attempts:** 100 ports

This handles the scenario where you have multiple test servers running!

## Directory Structure

```
flask-app/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your environment variables (create from .env.example)
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── upload.html         # File upload page
│   ├── files.html          # Files dashboard
│   ├── file_detail.html    # Validation errors viewer
│   ├── contractors.html    # Contractors page (placeholder)
│   ├── 404.html            # Not found page
│   └── 500.html            # Error page
└── static/                  # Static assets
    ├── css/                # CSS files
    └── js/                 # JavaScript files
```

## Configuration

### Create .env file

```bash
cp .env.example .env
```

### Edit .env with your AWS details

```env
# AWS Configuration
AWS_REGION=eu-west-2
AWS_PROFILE=default

# DynamoDB Table
DYNAMODB_TABLE_NAME=contractor-pay-development

# S3 Bucket
S3_BUCKET_NAME=contractor-pay-files-development-123456789012
```

## API Endpoints

### File Upload
```
POST /api/upload
Content-Type: multipart/form-data

Body: file (Excel .xlsx file)

Returns: {
    "message": "File uploaded successfully",
    "file_id": "uuid",
    "status": "UPLOADED"
}
```

### List Files
```
GET /api/files

Returns: {
    "files": [
        {
            "file_id": "uuid",
            "filename": "NASA_01092025.xlsx",
            "umbrella": "NASA",
            "period": 8,
            "status": "COMPLETED",
            "records": 14
        }
    ]
}
```

### File Details
```
GET /api/file/{file_id}

Returns: {
    "file_id": "uuid",
    "filename": "...",
    "status": "COMPLETED_WITH_WARNINGS",
    "errors": [],
    "warnings": [...]
}
```

### Delete File
```
DELETE /api/file/{file_id}

Returns: {
    "message": "File deleted successfully",
    "status": "deleted"
}
```

## Pages

### 1. Upload Page (`/upload`)

- Drag and drop file upload
- File type validation (.xlsx only)
- Progress bar
- Recent uploads list

### 2. Files Dashboard (`/files`)

- List all uploaded files
- Filter by status (COMPLETED, ERROR, etc.)
- Filter by umbrella company
- View details button
- Delete button

### 3. File Detail Page (`/file/{file_id}`)

- File metadata
- Validation errors (CRITICAL)
- Validation warnings (NON-BLOCKING)
- Suggested fixes
- Delete functionality

### 4. Contractors Page (`/contractors`)

- Placeholder for future contractor management

## Development

### Install Dependencies

```bash
# Activate virtual environment
source ../venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Run in Debug Mode

```bash
python app.py
```

Debug mode features:
- Auto-reload on code changes
- Detailed error pages
- Debug toolbar

### Add New Routes

```python
@app.route('/your-route')
def your_view():
    return render_template('your_template.html')
```

### Add New API Endpoints

```python
@app.route('/api/your-endpoint', methods=['GET', 'POST'])
def your_api():
    return jsonify({'data': 'value'})
```

## Troubleshooting

### Port Already in Use

The app automatically finds the next available port. Check the terminal output:

```
✅ Server starting on http://127.0.0.1:5557
```

### Virtual Environment Not Activating

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r flask-app/requirements.txt
```

### Dependencies Not Installing

```bash
# Upgrade pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### Desktop Launcher Not Working

```bash
# Make scripts executable
chmod +x /Users/gianlucaformica/Projects/contractor-pay-tracker/start_app.sh
chmod +x "/Users/gianlucaformica/Desktop/Contractor Pay Tracker.command"
```

## Next Steps

### Connect to AWS Backend

1. Deploy AWS infrastructure:
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

2. Update `.env` with deployed resources

3. Implement AWS integration in `app.py`:
   - Upload files to S3
   - Query DynamoDB for files
   - Display real validation results

### Add Features

- [ ] Implement actual AWS integration
- [ ] Add authentication
- [ ] Add contractor management
- [ ] Add reporting/analytics
- [ ] Export functionality

## Tech Stack

- **Backend:** Flask 3.0
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **AWS SDK:** boto3
- **File Handling:** Werkzeug

## License

Internal use only.
