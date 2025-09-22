"""
Startup System Checker - Verify database, email, and other configurations
"""
import sys
from file.chat_v2.chat_config import config
from ..services.database import db_service
from ..services.email import email_service


"""Startup Checker - Verify system configurations and dependencies"""
class StartupChecker:
    
    def __init__(self):
        # Store results for checks
        self.checks = [] # Successful checks
        self.warnings = [] # Non-critical issues
        self.errors = [] # Critical issues
    
    """Run all checks, return if the server can start"""
    def run_all_checks(self) -> bool:
        print("Starting system checks...")
        print("=" * 60)
        
        # Basic configuration check
        self._check_basic_config()
        
        # Database check
        self._check_database()
        
        # Email service check
        self._check_email_service()
        
        # Display check results
        self._display_results()
        
        # Check if the server can start
        can_start = len(self.errors) == 0
        
        if can_start:
            print("\nAll checks passed! Server is ready to start.")
        else:
            print(f"\n{len(self.errors)} critical error(s) found. Please fix them before starting.")
            
        print("=" * 60)
        return can_start
    
    def _check_basic_config(self):
        """Check basic configuration"""
        print("\nChecking basic configuration...")
        
        # Check necessary environment variables
        required_configs = [
            ('APP_NAME', config.APP_NAME),
            ('SECRET_KEY', config.SECRET_KEY),
            ('HOST', config.HOST),
            ('PORT', config.PORT),
        ]
        
        for name, value in required_configs:
            if value and str(value).strip():
                self._add_check(f"{name}: {value}") #pass
            else:
                self._add_error(f"{name} is not configured") #fail
        
        # Check debug mode
        if config.DEBUG:
            self._add_warning("DEBUG mode is enabled (not recommended for production)")
        else:
            self._add_check("DEBUG mode is disabled")
    
    def _check_database(self):
        """Check database connection"""
        print("\nChecking database connection...")
        
        try: # Try to create tables to verify DB connection

            db_service.create_all_tables()
            self._add_check("Database tables created successfully")
        except Exception as e:
            self._add_error(f"Database configuration error: {e}")
    
    def _check_email_service(self):
        """Check email service"""
        print("\nChecking email service...")
        
        if not config.EMAIL_NOTIFICATIONS_ENABLED:
            self._add_warning("Email notifications are disabled")
            return
            
        if not email_service:
            self._add_error("Email service failed to initialize")
            return
            
        try:
            # Display email configuration
            mail_info = email_service.get_config_info()
            self._add_check(f"SMTP Host: {mail_info['host']}:{mail_info['port']}")
            self._add_check(f"From: {mail_info['from_name']} <{mail_info['from_address']}>")
            self._add_check(f"Username: {mail_info['username']}")
            
            encryption = "TLS" if mail_info['use_tls'] else "SSL" if mail_info['use_ssl'] else "None"
            self._add_check(f"Encryption: {encryption}")
            
            # Test SMTP connection
            if email_service.test_connection():
                self._add_check("SMTP connection successful")
            else:
                self._add_error("SMTP connection failed - check credentials")
                
        except Exception as e:
            self._add_error(f"Email service error: {e}")
    

    def _add_check(self, message: str):
        """Add success check"""
        self.checks.append(message)
        print(f"  {message}")
    
    def _add_warning(self, message: str):
        """Add warning"""
        self.warnings.append(message)
        print(f"  {message}")
    
    def _add_error(self, message: str):
        """Add error"""
        self.errors.append(message)
        print(f"  {message}")
    
    def _display_results(self):
        """Display check results summary"""
        print(f"\nCheck Results:")
        print(f"   Passed: {len(self.checks)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Errors: {len(self.errors)}")
        
        if self.warnings:
            print(f"\nWarnings:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print(f"\nCritical Errors:")
            for error in self.errors:
                print(f"   {error}")


"""Run startup checks"""
def run_startup_checks() -> bool:
    checker = StartupChecker()
    return checker.run_all_checks()


if __name__ == "__main__":
    # Run checks
    success = run_startup_checks()
    sys.exit(0 if success else 1)
