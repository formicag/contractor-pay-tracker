"""
Contractor Pay Tracker - Flask Web Application

Main Flask application with smart port selection
"""

import os
import socket
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', '')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', '')


def find_available_port(start_port=5555, max_attempts=100):
    """
    Find an available port starting from start_port

    Args:
        start_port: Starting port number (default: 5555)
        max_attempts: Maximum number of ports to try

    Returns:
        int: Available port number
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result != 0:  # Port is available
                return port
        except socket.error:
            continue

    # Fallback to a random high port if all attempts fail
    return start_port + max_attempts


@app.route('/')
def index():
    """Home page - redirect to upload page"""
    return redirect(url_for('upload'))


@app.route('/upload')
def upload():
    """File upload page"""
    return render_template('upload.html')


@app.route('/files')
def files():
    """Files management dashboard"""
    return render_template('files.html')


@app.route('/file/<file_id>')
def file_detail(file_id):
    """File detail page with validation errors"""
    return render_template('file_detail.html', file_id=file_id)


@app.route('/contractors')
def contractors():
    """Contractors management page"""
    return render_template('contractors.html')


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    API endpoint for file upload

    Expected: multipart/form-data with file
    Returns: JSON with file_id and status
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files are supported'}), 400

    # TODO: Implement S3 upload via Lambda
    # For now, return mock response

    return jsonify({
        'message': 'File upload endpoint ready',
        'filename': file.filename,
        'size': len(file.read()),
        'status': 'pending'
    })


@app.route('/api/files', methods=['GET'])
def api_files():
    """
    API endpoint to list files

    Returns: JSON with files list
    """
    # TODO: Query DynamoDB for files

    # Mock data for now
    mock_files = [
        {
            'file_id': 'f001',
            'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',
            'umbrella': 'NASA',
            'period': 8,
            'status': 'COMPLETED',
            'uploaded_at': '2025-09-01T14:30:00Z',
            'records': 14
        },
        {
            'file_id': 'f002',
            'filename': 'PARASOL_Limited_Contractor_Pay_01092025.xlsx',
            'umbrella': 'PARASOL',
            'period': 8,
            'status': 'COMPLETED_WITH_WARNINGS',
            'uploaded_at': '2025-09-01T15:45:00Z',
            'records': 6,
            'warnings': 1
        }
    ]

    return jsonify({'files': mock_files})


@app.route('/api/file/<file_id>', methods=['GET'])
def api_file_detail(file_id):
    """
    API endpoint to get file details

    Returns: JSON with file metadata and validation results
    """
    # TODO: Query DynamoDB for file details

    # Mock data
    mock_file = {
        'file_id': file_id,
        'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',
        'umbrella': 'NASA',
        'period': 8,
        'status': 'COMPLETED',
        'uploaded_at': '2025-09-01T14:30:00Z',
        'total_records': 14,
        'valid_records': 14,
        'errors': [],
        'warnings': []
    }

    return jsonify(mock_file)


@app.route('/api/file/<file_id>', methods=['DELETE'])
def api_delete_file(file_id):
    """
    API endpoint to delete a file

    Returns: JSON with success status
    """
    # TODO: Implement soft delete in DynamoDB

    return jsonify({
        'message': f'File {file_id} deleted successfully',
        'status': 'deleted'
    })


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'app_name': 'Contractor Pay Tracker',
        'current_year': datetime.now().year
    }


if __name__ == '__main__':
    # Find available port
    port = find_available_port(start_port=5555)

    print("\n" + "="*60)
    print("🚀 Contractor Pay Tracker - Flask App")
    print("="*60)
    print(f"\n✅ Server starting on http://127.0.0.1:{port}")
    print(f"✅ Local access: http://localhost:{port}")
    print(f"\n📁 Upload files: http://localhost:{port}/upload")
    print(f"📊 View files: http://localhost:{port}/files")
    print(f"\n⚠️  Press CTRL+C to stop the server")
    print("="*60 + "\n")

    app.run(
        host='127.0.0.1',
        port=port,
        debug=True,
        use_reloader=True
    )
