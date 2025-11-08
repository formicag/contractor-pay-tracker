import logging
import sys
from datetime import datetime

def setup_logging(app):
    """Configure comprehensive Flask logging"""
    
    # Set Flask app logger to DEBUG
    app.logger.setLevel(logging.DEBUG)
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Console handler with detailed format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Detailed formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [FLASK_APP] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to app logger
    app.logger.addHandler(console_handler)
    
    # Also configure werkzeug logger (HTTP requests)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.DEBUG)
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [FLASK_APP] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[console_handler]
    )
    
    app.logger.info("="*80)
    app.logger.info("Flask logging configured - ALL requests and responses will be logged")
    app.logger.info("="*80)

def log_request(app):
    """Log every incoming request"""
    @app.before_request
    def before_request_logging():
        from flask import request
        app.logger.info("="*80)
        app.logger.info(f"INCOMING REQUEST: {request.method} {request.path}")
        app.logger.info(f"Remote Address: {request.remote_addr}")
        app.logger.info(f"User Agent: {request.user_agent}")
        app.logger.info(f"Headers: {dict(request.headers)}")
        if request.args:
            app.logger.info(f"Query Parameters: {dict(request.args)}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                app.logger.info(f"JSON Body: {request.get_json()}")
            elif request.form:
                app.logger.info(f"Form Data: {dict(request.form)}")
            if request.files:
                app.logger.info(f"Files: {list(request.files.keys())}")
        app.logger.info("="*80)

def log_response(app):
    """Log every outgoing response"""
    @app.after_request
    def after_request_logging(response):
        from flask import request
        app.logger.info("="*80)
        app.logger.info(f"OUTGOING RESPONSE: {request.method} {request.path}")
        app.logger.info(f"Status Code: {response.status_code}")
        app.logger.info(f"Response Headers: {dict(response.headers)}")
        if response.is_json and response.status_code != 200:
            app.logger.info(f"Response Body: {response.get_json()}")
        app.logger.info("="*80)
        return response

def log_errors(app):
    """Log all errors"""
    @app.errorhandler(Exception)
    def handle_exception(e):
        from flask import request
        app.logger.error("="*80)
        app.logger.error(f"EXCEPTION OCCURRED: {type(e).__name__}")
        app.logger.error(f"Request: {request.method} {request.path}")
        app.logger.error(f"Error Message: {str(e)}")
        app.logger.error(f"Exception Details:", exc_info=True)
        app.logger.error("="*80)
        # Re-raise to let Flask handle it
        raise
