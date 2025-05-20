#!/usr/bin/env python3
"""
error_handler.py
Advanced error handling and logging for the TradeMasterX system.
"""
import os
import logging
import traceback
import sys
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ErrorHandler:
    """Advanced error handling with logging, notifications, and recovery."""
    
    ERROR_LEVELS = {
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self, config_path=None):
        """Initialize error handler with optional config."""
        self.logger = None
        self.email_config = None
        self.notification_enabled = False
        self.recover_funcs = {}
        
        # Set up logging
        self.setup_logging()
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def setup_logging(self):
        """Set up logging with file and console handlers."""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Create error log file handler
        self.logger = logging.getLogger('TradeMasterXError')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler(os.path.join('logs', 'errors.log'))
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def load_config(self, config_path):
        """Load error handling configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Email notification settings
            if 'email' in config:
                self.email_config = config['email']
                self.notification_enabled = self.email_config.get('enabled', False)
                
            # Set log level from config
            if 'log_level' in config:
                level = self.ERROR_LEVELS.get(config['log_level'].upper(), logging.INFO)
                self.logger.setLevel(level)
                
            self.logger.info(f"Error handler configured from {config_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load error handler config: {e}")
    
    def register_recovery(self, error_type, recovery_func):
        """Register a recovery function for a specific error type."""
        if isinstance(error_type, type) and issubclass(error_type, Exception):
            self.recover_funcs[error_type] = recovery_func
            self.logger.info(f"Registered recovery for {error_type.__name__}")
        else:
            self.logger.warning(f"Invalid error type for recovery registration: {error_type}")
    
    def handle_error(self, error, context=None, level=None):
        """Handle an error with logging, notification, and recovery if possible."""
        # Determine error level
        if level is None:
            if isinstance(error, KeyboardInterrupt):
                level = logging.INFO
            elif isinstance(error, Exception):
                level = logging.ERROR
            else:
                level = logging.WARNING
        
        # Format error message with context
        if context:
            error_msg = f"{error} (Context: {context})"
        else:
            error_msg = str(error)
            
        # Get stack trace
        stack_trace = traceback.format_exc()
        
        # Log the error
        self.logger.log(level, error_msg)
        if stack_trace and stack_trace != "NoneType: None\n":
            self.logger.log(level, f"Stack trace:\n{stack_trace}")
            
        # Send notification for serious errors
        if level >= logging.ERROR and self.notification_enabled:
            self.send_notification(error_msg, stack_trace)
            
        # Attempt recovery if registered
        for error_type, recovery_func in self.recover_funcs.items():
            if isinstance(error, error_type):
                try:
                    self.logger.info(f"Attempting recovery for {error_type.__name__}")
                    return recovery_func(error)
                except Exception as recovery_error:
                    self.logger.error(f"Recovery failed: {recovery_error}")
                    
        return False  # No recovery attempted or recovery failed
    
    def send_notification(self, error_msg, stack_trace):
        """Send email notification about error."""
        if not self.email_config:
            return
            
        try:
            sender = self.email_config.get('sender')
            recipient = self.email_config.get('recipient')
            password = self.email_config.get('password')
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            
            if not all([sender, recipient, password]):
                self.logger.warning("Incomplete email configuration, skipping notification")
                return
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = f"TradeMasterX Error Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Build email body
            body = f"""
            <html>
            <body>
                <h2>TradeMasterX Error Alert</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Error:</strong> {error_msg}</p>
                <h3>Stack Trace:</h3>
                <pre>{stack_trace}</pre>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to server and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Error notification email sent to {recipient}")
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
    
    @staticmethod
    def safe_execute(func, *args, error_handler=None, context=None, **kwargs):
        """
        Execute a function safely with error handling.
        
        Args:
            func: The function to execute
            error_handler: ErrorHandler instance or None to use print
            context: Context information to include in error messages
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            Result of function or None if execution failed
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if error_handler:
                error_handler.handle_error(e, context)
            else:
                print(f"Error executing {func.__name__}: {e}")
                traceback.print_exc()
            return None


# Default error handler instance for global use
default_handler = ErrorHandler()

def handle_error(error, context=None, level=None):
    """Global error handling function using default handler."""
    return default_handler.handle_error(error, context, level)

def safe_execute(func, *args, context=None, **kwargs):
    """Global safe execution function using default handler."""
    return ErrorHandler.safe_execute(func, *args, error_handler=default_handler, context=context, **kwargs)
