"""
Permanent Staff Table Password Protection

Implements password locking for permanent staff data.
All modifications require password "luca" to unlock.
"""

import bcrypt
from functools import wraps
from flask import request, jsonify

# Unlock password (hashed)
UNLOCK_PASSWORD = 'luca'
PASSWORD_HASH = bcrypt.hashpw(UNLOCK_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_unlock_password(password: str) -> bool:
    """
    Verify the unlock password

    Args:
        password: Password to verify

    Returns:
        True if password is correct, False otherwise
    """
    if not password:
        return False

    return password == UNLOCK_PASSWORD


def require_unlock_password(f):
    """
    Decorator to require unlock password for permanent staff modifications

    Usage:
        @app.route('/api/perm-staff/<email>', methods=['POST'])
        @require_unlock_password
        def update_perm_staff(email):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for unlock password in request
        data = request.get_json() if request.is_json else {}
        unlock_password = data.get('unlock_password') or request.headers.get('X-Unlock-Password')

        if not verify_unlock_password(unlock_password):
            return jsonify({
                'error': 'Unauthorized',
                'message': '🔒 Permanent staff data is locked. Please provide the correct unlock password.',
                'locked': True
            }), 403

        # Password verified - proceed with the request
        return f(*args, **kwargs)

    return decorated_function


def get_lock_status() -> dict:
    """
    Get the current lock status for permanent staff table

    Returns:
        Dict with lock status information
    """
    return {
        'locked': True,
        'message': 'Permanent staff data is password-protected',
        'unlock_required': 'Password "luca" required for modifications',
        'view_only': True
    }
