"""
notification_system.py
A module for sending notifications about important trading events.
"""
import os
import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationSystem:
    def __init__(self, config_file=None):
        """Initialize the notification system with configuration."""
        self.config_file = config_file or os.path.join('config', 'notifications.json')
        self.config = self._load_config()
        self.notification_log = os.path.join('logs', 'notifications.log')
        
        # Ensure log directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
    
    def _load_config(self):
        """Load notification configuration from JSON file."""
        default_config = {
            "enabled": True,
            "console_output": True,
            "log_file": True,
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_address": ""
            },
            "notification_levels": {
                "INFO": True,
                "TRADE": True,
                "WARNING": True,
                "ERROR": True
            },
            "throttle_minutes": 5  # Minimum minutes between similar notifications
        }
        
        # Create config directory if it doesn't exist
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        
        # Create default config if file doesn't exist
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return default_config
    
    def _log_notification(self, level, message):
        """Log notification to file."""
        if not self.config.get("log_file", True):
            return
            
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} [{level}] {message}\n"
        
        with open(self.notification_log, 'a') as f:
            f.write(log_entry)
    
    def _send_email(self, subject, message):
        """Send email notification."""
        email_config = self.config.get("email", {})
        
        if not email_config.get("enabled", False):
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config.get("from_address")
            msg['To'] = email_config.get("to_address")
            msg['Subject'] = f"TradeMasterX: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port", 587))
            server.starttls()
            server.login(email_config.get("username"), email_config.get("password"))
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email notification error: {str(e)}")
            return False
    
    def _should_throttle(self, level, message):
        """Check if similar notifications have been sent recently."""
        throttle_minutes = self.config.get("throttle_minutes", 5)
        
        if throttle_minutes <= 0:
            return False
            
        # Check notification log for similar messages
        if not os.path.exists(self.notification_log):
            return False
            
        try:
            with open(self.notification_log, 'r') as f:
                lines = f.readlines()
                
            # Check last 50 log entries
            for line in reversed(lines[-50:]):
                try:
                    parts = line.strip().split(' ', 2)
                    if len(parts) >= 3:
                        timestamp_str = parts[0]
                        log_level = parts[1].strip('[]')
                        log_message = parts[2]
                        
                        # If we find a similar message with the same level
                        if level == log_level and message in log_message:
                            timestamp = datetime.datetime.fromisoformat(timestamp_str)
                            now = datetime.datetime.now()
                            
                            # If the message is within throttle window
                            if (now - timestamp).total_seconds() < throttle_minutes * 60:
                                return True
                except Exception:
                    continue
                    
            return False
        except Exception:
            return False
    
    def notify(self, level, message, force=False):
        """
        Send a notification.
        
        Args:
            level: Notification level ('INFO', 'TRADE', 'WARNING', 'ERROR')
            message: Notification message
            force: If True, bypass throttling checks
        """
        if not self.config.get("enabled", True):
            return False
            
        # Check if this level of notification is enabled
        notification_levels = self.config.get("notification_levels", {})
        if not notification_levels.get(level, True):
            return False
            
        # Check throttling
        if not force and self._should_throttle(level, message):
            return False
        
        # Console output
        if self.config.get("console_output", True):
            print(f"[{level}] {message}")
        
        # Log to file
        self._log_notification(level, message)
        
        # Send email for TRADE, WARNING, and ERROR levels
        if level in ['TRADE', 'WARNING', 'ERROR']:
            self._send_email(f"{level}: {message[:30]}...", message)
        
        return True

# Global notification instance for easy access
_notification_system = None

def get_notification_system():
    """Get or create the global notification system instance."""
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
    return _notification_system

def notify(level, message, force=False):
    """Send a notification using the global notification system."""
    system = get_notification_system()
    return system.notify(level, message, force)
