"""
Structured logging utility for Lambda functions
Provides JSON-formatted logs for CloudWatch Logs Insights
"""

import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class StructuredLogger:
    """Structured JSON logger for Lambda functions"""

    def __init__(self, lambda_name: str, request_id: str = None):
        print(f"[LOGGER_INIT] Starting StructuredLogger initialization with lambda_name={lambda_name}, request_id={request_id}")
        self.lambda_name = lambda_name
        print(f"[LOGGER_INIT] Set self.lambda_name={self.lambda_name}")

        self.request_id = request_id or "no-request-id"
        print(f"[LOGGER_INIT] Set self.request_id={self.request_id}")

        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
        print(f"[LOGGER_INIT] Retrieved LOG_LEVEL from environment: {self.log_level}")

        self.logger = logging.getLogger()
        print(f"[LOGGER_INIT] Created logger instance: {self.logger}")

        log_level_attr = getattr(logging, self.log_level)
        print(f"[LOGGER_INIT] Converting log_level string '{self.log_level}' to logging constant: {log_level_attr}")

        self.logger.setLevel(log_level_attr)
        print(f"[LOGGER_INIT] Set logger level to {log_level_attr}")
        print(f"[LOGGER_INIT] StructuredLogger initialization complete")

    def _format_log(self, level: str, message: str, **context) -> str:
        """Format log entry as JSON"""
        print(f"[FORMAT_LOG] Formatting log entry - level={level}, message={message}, context={context}")

        timestamp = datetime.utcnow().isoformat() + "Z"
        print(f"[FORMAT_LOG] Generated timestamp: {timestamp}")

        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "lambda_name": self.lambda_name,
            "request_id": self.request_id,
            "message": message,
        }
        print(f"[FORMAT_LOG] Created base log_entry dict: {log_entry}")

        if context:
            print(f"[FORMAT_LOG] Context provided, adding to log_entry: {context}")
            log_entry["context"] = context
            print(f"[FORMAT_LOG] Updated log_entry with context: {log_entry}")
        else:
            print(f"[FORMAT_LOG] No context provided, skipping context addition")

        json_output = json.dumps(log_entry, cls=DecimalEncoder)
        print(f"[FORMAT_LOG] Converted log_entry to JSON: {json_output}")
        return json_output

    def debug(self, message: str, **context):
        """Debug level log"""
        print(f"[DEBUG_METHOD] debug() called with message={message}, context={context}")
        formatted_log = self._format_log("DEBUG", message, **context)
        print(f"[DEBUG_METHOD] Formatted log: {formatted_log}")
        self.logger.debug(formatted_log)
        print(f"[DEBUG_METHOD] Passed formatted log to logger.debug()")

    def info(self, message: str, **context):
        """Info level log"""
        print(f"[INFO_METHOD] info() called with message={message}, context={context}")
        formatted_log = self._format_log("INFO", message, **context)
        print(f"[INFO_METHOD] Formatted log: {formatted_log}")
        self.logger.info(formatted_log)
        print(f"[INFO_METHOD] Passed formatted log to logger.info()")

    def warning(self, message: str, **context):
        """Warning level log"""
        print(f"[WARNING_METHOD] warning() called with message={message}, context={context}")
        formatted_log = self._format_log("WARNING", message, **context)
        print(f"[WARNING_METHOD] Formatted log: {formatted_log}")
        self.logger.warning(formatted_log)
        print(f"[WARNING_METHOD] Passed formatted log to logger.warning()")

    def error(self, message: str, **context):
        """Error level log"""
        print(f"[ERROR_METHOD] error() called with message={message}, context={context}")
        formatted_log = self._format_log("ERROR", message, **context)
        print(f"[ERROR_METHOD] Formatted log: {formatted_log}")
        self.logger.error(formatted_log)
        print(f"[ERROR_METHOD] Passed formatted log to logger.error()")

    def critical(self, message: str, **context):
        """Critical level log"""
        print(f"[CRITICAL_METHOD] critical() called with message={message}, context={context}")
        formatted_log = self._format_log("CRITICAL", message, **context)
        print(f"[CRITICAL_METHOD] Formatted log: {formatted_log}")
        self.logger.critical(formatted_log)
        print(f"[CRITICAL_METHOD] Passed formatted log to logger.critical()")
