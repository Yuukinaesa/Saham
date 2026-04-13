"""Structured Logging Module for Saham IDX.

Provides enterprise-grade structured logging for audit trails,
incident response, and production diagnostics.

Compliance: NIST SP 800-92, ISO 27001 A.12.4
"""
import logging
import json
import os
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for machine-parseable audit trail."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        # Add extra context if provided
        if hasattr(record, 'user_action'):
            log_entry['user_action'] = record.user_action
        if hasattr(record, 'symbol'):
            log_entry['symbol'] = record.symbol
        if hasattr(record, 'security_event'):
            log_entry['security_event'] = record.security_event

        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(name: str = "saham_idx") -> logging.Logger:
    """Get a configured structured logger.
    
    Args:
        name: Logger name (module identifier).
    
    Returns:
        Configured logger instance with structured JSON output.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers on repeated calls
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Console handler with structured JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # File handler for persistent audit trail (if writable)
    try:
        from logging.handlers import RotatingFileHandler
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'audit.log'),
            encoding='utf-8',
            maxBytes=5_242_880,  # 5MB
            backupCount=3,
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    except (OSError, PermissionError, ImportError):
        # Streamlit Cloud may not allow file writes — gracefully degrade
        pass
    
    return logger


def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """Log a security-relevant event for audit trail.
    
    Args:
        event_type: Category of security event (e.g., 'input_sanitized', 'injection_blocked').
        details: Human-readable description of what happened.
        severity: Log level (INFO, WARNING, ERROR, CRITICAL).
    """
    logger = get_logger("saham_idx.security")
    level = getattr(logging, severity.upper(), logging.WARNING)
    logger.log(level, details, extra={
        'security_event': event_type,
    })


def log_user_action(action: str, details: str = ""):
    """Log a user action for analytics and audit trail.
    
    Args:
        action: Type of action (e.g., 'stock_search', 'calculate', 'export').
        details: Additional context about the action.
    """
    logger = get_logger("saham_idx.user")
    logger.info(f"{action}: {details}", extra={
        'user_action': action,
    })
