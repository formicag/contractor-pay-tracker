print("[FLASK_APP] Module load started")
"""
print("[FLASK_APP] Contractor Pay Tracker - Flask Web Application")
Contractor Pay Tracker - Flask Web Application

print("[FLASK_APP] Main Flask application with smart port selection")
Main Flask application with smart port selection
"""

print("[FLASK_APP] import os")
import os
print("[FLASK_APP] import socket")
import socket
print("[FLASK_APP] from datetime import datetime")
from datetime import datetime
print("[FLASK_APP] import uuid")
import uuid
print("[FLASK_APP] import json")
import json

print("[FLASK_APP] from flask import Flask, render_template, request, jsonify, redirect, url_for")
from flask import Flask, render_template, request, jsonify, redirect, url_for
print("[FLASK_APP] from dotenv import load_dotenv")
from dotenv import load_dotenv
print("[FLASK_APP] import boto3")
import boto3
print("[FLASK_APP] from botocore.exceptions import ClientError")
from botocore.exceptions import ClientError

# Load environment variables
print("[FLASK_APP] load_dotenv()")
load_dotenv()

print("[FLASK_APP] app = Flask(__name__)")
app = Flask(__name__)
print("[FLASK_APP] app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
print("[FLASK_APP] app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-i")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
print("[FLASK_APP] AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')")
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')
print("[FLASK_APP] AWS_PROFILE = os.environ.get('AWS_PROFILE', 'AdministratorAccess-016164185850')")
AWS_PROFILE = os.environ.get('AWS_PROFILE', 'AdministratorAccess-016164185850')
print("[FLASK_APP] S3_BUCKET = os.environ.get('S3_BUCKET_NAME', '')")
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', '')
print("[FLASK_APP] DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', '')")
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', '')
print("[FLASK_APP] FILE_PROCESSOR_ARN = os.environ.get('FILE_PROCESSOR_ARN', '')")
FILE_PROCESSOR_ARN = os.environ.get('FILE_PROCESSOR_ARN', '')

# Initialize AWS clients
print("[FLASK_APP] session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)")
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
print("[FLASK_APP] s3_client = session.client('s3')")
s3_client = session.client('s3')
print("[FLASK_APP] dynamodb = session.resource('dynamodb')")
dynamodb = session.resource('dynamodb')
print("[FLASK_APP] lambda_client = session.client('lambda')")
lambda_client = session.client('lambda')
print("[FLASK_APP] table = dynamodb.Table(DYNAMODB_TABLE) if DYNAMODB_TABLE else None")
table = dynamodb.Table(DYNAMODB_TABLE) if DYNAMODB_TABLE else None


print("[FLASK_APP] def find_available_port(start_port=5555, max_attempts=100):")
def find_available_port(start_port=5555, max_attempts=100):
    """
print("[FLASK_APP] Find an available port starting from start_port")
    Find an available port starting from start_port

print("[FLASK_APP] Args:")
    Args:
print("[FLASK_APP] start_port: Starting port number (default: 5555)")
        start_port: Starting port number (default: 5555)
print("[FLASK_APP] max_attempts: Maximum number of ports to try")
        max_attempts: Maximum number of ports to try

print("[FLASK_APP] Returns:")
    Returns:
print("[FLASK_APP] int: Available port number")
        int: Available port number
    """
print("[FLASK_APP] for port in range(start_port, start_port + max_attempts):")
    for port in range(start_port, start_port + max_attempts):
print("[FLASK_APP] try:")
        try:
            # Try to bind to the port
print("[FLASK_APP] sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[FLASK_APP] sock.settimeout(1)")
            sock.settimeout(1)
print("[FLASK_APP] result = sock.connect_ex(('127.0.0.1', port))")
            result = sock.connect_ex(('127.0.0.1', port))
print("[FLASK_APP] sock.close()")
            sock.close()

print("[FLASK_APP] if result != 0:  # Port is available")
            if result != 0:  # Port is available
print("[FLASK_APP] return port")
                return port
print("[FLASK_APP] except socket.error:")
        except socket.error:
print("[FLASK_APP] continue")
            continue

    # Fallback to a random high port if all attempts fail
print("[FLASK_APP] return start_port + max_attempts")
    return start_port + max_attempts


print("[FLASK_APP] @app.route('/')")
@app.route('/')
print("[FLASK_APP] def index():")
def index():
    """Home page - redirect to upload page"""
print("[FLASK_APP] return redirect(url_for('upload'))")
    return redirect(url_for('upload'))


print("[FLASK_APP] @app.route('/upload')")
@app.route('/upload')
print("[FLASK_APP] def upload():")
def upload():
    """File upload page"""
print("[FLASK_APP] return render_template('upload.html')")
    return render_template('upload.html')


print("[FLASK_APP] @app.route('/files')")
@app.route('/files')
print("[FLASK_APP] def files():")
def files():
    """Files management dashboard"""
print("[FLASK_APP] return render_template('files.html')")
    return render_template('files.html')


print("[FLASK_APP] @app.route('/file/<file_id>')")
@app.route('/file/<file_id>')
print("[FLASK_APP] def file_detail(file_id):")
def file_detail(file_id):
    """File detail page with validation errors"""
print("[FLASK_APP] return render_template('file_detail.html', file_id=file_id)")
    return render_template('file_detail.html', file_id=file_id)


print("[FLASK_APP] @app.route('/contractors')")
@app.route('/contractors')
print("[FLASK_APP] def contractors():")
def contractors():
    """Contractors management page"""
print("[FLASK_APP] return render_template('contractors.html')")
    return render_template('contractors.html')


print("[FLASK_APP] @app.route('/api/upload', methods=['POST'])")
@app.route('/api/upload', methods=['POST'])
print("[FLASK_APP] def api_upload():")
def api_upload():
    """
print("[FLASK_APP] API endpoint for file upload")
    API endpoint for file upload

print("[FLASK_APP] Expected: multipart/form-data with file")
    Expected: multipart/form-data with file
print("[FLASK_APP] Returns: JSON with file_id and status")
    Returns: JSON with file_id and status
    """
print("[FLASK_APP] if 'file' not in request.files:")
    if 'file' not in request.files:
print("[FLASK_APP] return jsonify({'error': 'No file provided'}), 400")
        return jsonify({'error': 'No file provided'}), 400

print("[FLASK_APP] file = request.files['file']")
    file = request.files['file']

print("[FLASK_APP] if file.filename == '':")
    if file.filename == '':
print("[FLASK_APP] return jsonify({'error': 'No file selected'}), 400")
        return jsonify({'error': 'No file selected'}), 400

print("[FLASK_APP] if not file.filename.endswith('.xlsx'):")
    if not file.filename.endswith('.xlsx'):
print("[FLASK_APP] return jsonify({'error': 'Only .xlsx files are supported'}), 400")
        return jsonify({'error': 'Only .xlsx files are supported'}), 400

    # TODO: Implement S3 upload via Lambda
    # For now, return mock response

print("[FLASK_APP] return jsonify({")
    return jsonify({
print("[FLASK_APP] 'message': 'File upload endpoint ready',")
        'message': 'File upload endpoint ready',
print("[FLASK_APP] 'filename': file.filename,")
        'filename': file.filename,
print("[FLASK_APP] 'size': len(file.read()),")
        'size': len(file.read()),
print("[FLASK_APP] 'status': 'pending'")
        'status': 'pending'
print("[FLASK_APP] })")
    })


print("[FLASK_APP] @app.route('/api/files', methods=['GET'])")
@app.route('/api/files', methods=['GET'])
print("[FLASK_APP] def api_files():")
def api_files():
    """
print("[FLASK_APP] API endpoint to list files")
    API endpoint to list files

print("[FLASK_APP] Returns: JSON with files list")
    Returns: JSON with files list
    """
    # TODO: Query DynamoDB for files

    # Mock data for now
print("[FLASK_APP] mock_files = [")
    mock_files = [
print("[FLASK_APP] {")
        {
print("[FLASK_APP] 'file_id': 'f001',")
            'file_id': 'f001',
print("[FLASK_APP] 'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',")
            'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',
print("[FLASK_APP] 'umbrella': 'NASA',")
            'umbrella': 'NASA',
print("[FLASK_APP] 'period': 8,")
            'period': 8,
print("[FLASK_APP] 'status': 'COMPLETED',")
            'status': 'COMPLETED',
print("[FLASK_APP] 'uploaded_at': '2025-09-01T14:30:00Z',")
            'uploaded_at': '2025-09-01T14:30:00Z',
print("[FLASK_APP] 'records': 14")
            'records': 14
print("[FLASK_APP] },")
        },
print("[FLASK_APP] {")
        {
print("[FLASK_APP] 'file_id': 'f002',")
            'file_id': 'f002',
print("[FLASK_APP] 'filename': 'PARASOL_Limited_Contractor_Pay_01092025.xlsx',")
            'filename': 'PARASOL_Limited_Contractor_Pay_01092025.xlsx',
print("[FLASK_APP] 'umbrella': 'PARASOL',")
            'umbrella': 'PARASOL',
print("[FLASK_APP] 'period': 8,")
            'period': 8,
print("[FLASK_APP] 'status': 'COMPLETED_WITH_WARNINGS',")
            'status': 'COMPLETED_WITH_WARNINGS',
print("[FLASK_APP] 'uploaded_at': '2025-09-01T15:45:00Z',")
            'uploaded_at': '2025-09-01T15:45:00Z',
print("[FLASK_APP] 'records': 6,")
            'records': 6,
print("[FLASK_APP] 'warnings': 1")
            'warnings': 1
print("[FLASK_APP] }")
        }
print("[FLASK_APP] ]")
    ]

print("[FLASK_APP] return jsonify({'files': mock_files})")
    return jsonify({'files': mock_files})


print("[FLASK_APP] @app.route('/api/file/<file_id>', methods=['GET'])")
@app.route('/api/file/<file_id>', methods=['GET'])
print("[FLASK_APP] def api_file_detail(file_id):")
def api_file_detail(file_id):
    """
print("[FLASK_APP] API endpoint to get file details")
    API endpoint to get file details

print("[FLASK_APP] Returns: JSON with file metadata and validation results")
    Returns: JSON with file metadata and validation results
    """
    # TODO: Query DynamoDB for file details

    # Mock data
print("[FLASK_APP] mock_file = {")
    mock_file = {
print("[FLASK_APP] 'file_id': file_id,")
        'file_id': file_id,
print("[FLASK_APP] 'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',")
        'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',
print("[FLASK_APP] 'umbrella': 'NASA',")
        'umbrella': 'NASA',
print("[FLASK_APP] 'period': 8,")
        'period': 8,
print("[FLASK_APP] 'status': 'COMPLETED',")
        'status': 'COMPLETED',
print("[FLASK_APP] 'uploaded_at': '2025-09-01T14:30:00Z',")
        'uploaded_at': '2025-09-01T14:30:00Z',
print("[FLASK_APP] 'total_records': 14,")
        'total_records': 14,
print("[FLASK_APP] 'valid_records': 14,")
        'valid_records': 14,
print("[FLASK_APP] 'errors': [],")
        'errors': [],
print("[FLASK_APP] 'warnings': []")
        'warnings': []
print("[FLASK_APP] }")
    }

print("[FLASK_APP] return jsonify(mock_file)")
    return jsonify(mock_file)


print("[FLASK_APP] @app.route('/api/file/<file_id>', methods=['DELETE'])")
@app.route('/api/file/<file_id>', methods=['DELETE'])
print("[FLASK_APP] def api_delete_file(file_id):")
def api_delete_file(file_id):
    """
print("[FLASK_APP] API endpoint to delete a file")
    API endpoint to delete a file

print("[FLASK_APP] Returns: JSON with success status")
    Returns: JSON with success status
    """
    # TODO: Implement soft delete in DynamoDB

print("[FLASK_APP] return jsonify({")
    return jsonify({
print("[FLASK_APP] 'message': f'File {file_id} deleted successfully',")
        'message': f'File {file_id} deleted successfully',
print("[FLASK_APP] 'status': 'deleted'")
        'status': 'deleted'
print("[FLASK_APP] })")
    })


print("[FLASK_APP] @app.errorhandler(404)")
@app.errorhandler(404)
print("[FLASK_APP] def not_found(error):")
def not_found(error):
    """404 error handler"""
print("[FLASK_APP] return render_template('404.html'), 404")
    return render_template('404.html'), 404


print("[FLASK_APP] @app.errorhandler(500)")
@app.errorhandler(500)
print("[FLASK_APP] def internal_error(error):")
def internal_error(error):
    """500 error handler"""
print("[FLASK_APP] return render_template('500.html'), 500")
    return render_template('500.html'), 500


print("[FLASK_APP] @app.context_processor")
@app.context_processor
print("[FLASK_APP] def inject_globals():")
def inject_globals():
    """Inject global variables into templates"""
print("[FLASK_APP] return {")
    return {
print("[FLASK_APP] 'app_name': 'Contractor Pay Tracker',")
        'app_name': 'Contractor Pay Tracker',
print("[FLASK_APP] 'current_year': datetime.now().year")
        'current_year': datetime.now().year
print("[FLASK_APP] }")
    }


print("[FLASK_APP] if __name__ == '__main__':")
if __name__ == '__main__':
    # Use environment variable for port, or find available port
    # This ensures consistent port across Flask reloader restarts
print("[FLASK_APP] if 'FLASK_RUN_PORT' not in os.environ:")
    if 'FLASK_RUN_PORT' not in os.environ:
print("[FLASK_APP] port = find_available_port(start_port=5555)")
        port = find_available_port(start_port=5555)
print("[FLASK_APP] os.environ['FLASK_RUN_PORT'] = str(port)")
        os.environ['FLASK_RUN_PORT'] = str(port)
print("[FLASK_APP] else:")
    else:
print("[FLASK_APP] port = int(os.environ['FLASK_RUN_PORT'])")
        port = int(os.environ['FLASK_RUN_PORT'])

    # Only print banner once (not on reloader restart)
print("[FLASK_APP] if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':")
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
print("[FLASK_APP] print("\n" + "="*60)")
        print("\n" + "="*60)
print("[FLASK_APP] print("🚀 Contractor Pay Tracker - Flask App")")
        print("🚀 Contractor Pay Tracker - Flask App")
print("[FLASK_APP] print("="*60)")
        print("="*60)
print("[FLASK_APP] print(f"\n✅ Server starting on http://127.0.0.1:{port}")")
        print(f"\n✅ Server starting on http://127.0.0.1:{port}")
print("[FLASK_APP] print(f"✅ Local access: http://localhost:{port}")")
        print(f"✅ Local access: http://localhost:{port}")
print("[FLASK_APP] print(f"\n📁 Upload files: http://localhost:{port}/upload")")
        print(f"\n📁 Upload files: http://localhost:{port}/upload")
print("[FLASK_APP] print(f"📊 View files: http://localhost:{port}/files")")
        print(f"📊 View files: http://localhost:{port}/files")
print("[FLASK_APP] print(f"\n⚠️  Press CTRL+C to stop the server")")
        print(f"\n⚠️  Press CTRL+C to stop the server")
print("[FLASK_APP] print("="*60 + "\n")")
        print("="*60 + "\n")

print("[FLASK_APP] app.run(")
    app.run(
print("[FLASK_APP] host='127.0.0.1',")
        host='127.0.0.1',
print("[FLASK_APP] port=port,")
        port=port,
print("[FLASK_APP] debug=True,")
        debug=True,
print("[FLASK_APP] use_reloader=True")
        use_reloader=True
print("[FLASK_APP] )")
    )
print("[FLASK_APP] Module load complete")
