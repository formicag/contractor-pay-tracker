"""
Structured logging utility for Lambda functions
Provides JSON-formatted logs for CloudWatch Logs Insights
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """Structured JSON logger for Lambda functions"""

    def __init__(self, lambda_name: str, request_id: str = None):
        self.lambda_name = lambda_name
        self.request_id = request_id or "no-request-id"
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')

        self.logger = logging.getLogger()
        self.logger.setLevel(getattr(logging, self.log_level))

    def _format_log(self, level: str, message: str, **context) -> str:
        """Format log entry as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "lambda_name": self.lambda_name,
            "request_id": self.request_id,
            "message": message,
        }

        if context:
            log_entry["context"] = context

        return json.dumps(log_entry)

    def debug(self, message: str, **context):
        """Debug level log"""
        self.logger.debug(self._format_log("DEBUG", message, **context))

    def info(self, message: str, **context):
        """Info level log"""
        self.logger.info(self._format_log("INFO", message, **context))

    def warning(self, message: str, **context):
        """Warning level log"""
        self.logger.warning(self._format_log("WARNING", message, **context))

    def error(self, message: str, **context):
        """Error level log"""
        self.logger.error(self._format_log("ERROR", message, **context))

    def critical(self, message: str, **context):
        """Critical level log"""
        self.logger.critical(self._format_log("CRITICAL", message, **context))
