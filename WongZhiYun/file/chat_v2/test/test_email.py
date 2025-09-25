"""
Email service test script

Usage:
1. Configure .env file or environment variables
2. Run: python -m test.test_email
"""

from services.email import email_service

def test_email_service():
    """Test email service"""
    print("Start testing email service...")
    
    try:

        # Check if email service is properly configured
        if not email_service:
            print("Email service not configured or configured incorrectly")
            print("Please check your SMTP configuration, refer to email_setup_guide.txt")
            return False
        
        # Test SMTP connection
        print("Test SMTP connection...")
        if email_service.test_connection():
            print("SMTP connection test successful!")
        else:
            print("SMTP connection test failed")
            return False
        
        # Ask user if they want to send a test email

        test_send = input("\nWhether to send test email? (enter email address, or press Enter to skip): ").strip()
        if test_send and '@' in test_send:
            print(f"Send test email to {test_send}...")
            success = email_service.send_new_message_notification(
                recipient_email=test_send,
                recipient_name="Test user",
                sender_name="System test",
                message_count=1
            )
            if success:
                print("Test email sent successfully!")
            else:
                print("Test email sending failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"Error occurred during test: {e}")
        return False

def show_config_status():
    """Show configuration status"""
    print("Current configuration status:")
    
    try:
        from chat_config import config
        if config:
            print(f"SMTP host: {config.MAIL_HOST}")
            print(f"SMTP port: {config.MAIL_PORT}")
            print(f"Use TLS: {config.MAIL_ENCRYPTION}")
            print(f"Sender: {config.MAIL_FROM_ADDRESS}")
            print(f"Application name: {config.APP_NAME}")
        else:
            print("Email configuration not found")
    except Exception as e:
        print(f"Configuration loading error: {e}")

def show_smtp_guide():
    """Show SMTP setup guide"""
    provider = input("Select email provider (gmail/outlook/163/qq): ").strip().lower()
    if provider in ['gmail', 'outlook', '163', 'qq']:
        print(get_smtp_setup_guide(provider))
    else:
        print(get_smtp_setup_guide('gmail'))  # Default display Gmail guide


def get_smtp_setup_guide(provider: str = 'gmail') -> str:
    """Get SMTP setup guide"""
    preset = SMTP_PRESETS.get(provider.lower())
    if not preset:
        return f"Unknown email provider: {provider}"
    
    return f"""
    {provider.upper()} SMTP Setup Guide:

    Server Settings:
    - MAIL_HOST={preset['MAIL_HOST']}
    - MAIL_PORT={preset['MAIL_PORT']}
    - MAIL_ENCRYPTION={preset['MAIL_ENCRYPTION']}

    Note:
    {preset['note']}

    Environment Variables Example:
    MAIL_HOST={preset['MAIL_HOST']}
    MAIL_PORT={preset['MAIL_PORT']}
    MAIL_ENCRYPTION={preset['MAIL_ENCRYPTION']}
    MAIL_USERNAME=your_email@{provider.lower()}.com
    MAIL_PASSWORD=your_app_password
    MAIL_FROM_ADDRESS=your_email@{provider.lower()}.com
    MAIL_FROM_NAME="Chat App"
    """

# SMTP Config Presets 
SMTP_PRESETS = {
    'gmail': {
        'MAIL_HOST': 'smtp.gmail.com',
        'MAIL_PORT': 587,
        'MAIL_ENCRYPTION': 'tls',
        'note': 'Need App Password, not regular password'
    },
    'outlook': {
        'MAIL_HOST': 'smtp-mail.outlook.com',
        'MAIL_PORT': 587,
        'MAIL_ENCRYPTION': 'tls',
        'note': 'Supports Outlook, Hotmail accounts'
    },
    'yahoo': {
        'MAIL_HOST': 'smtp.mail.yahoo.com',
        'MAIL_PORT': 587,
        'MAIL_ENCRYPTION': 'tls',
        'note': 'Need to enable Less Secure Apps or use App Password'
    },
    '163': {
        'MAIL_HOST': 'smtp.163.com',
        'MAIL_PORT': 587,
        'MAIL_ENCRYPTION': 'tls',
        'note': 'Need to enable SMTP service and use auth password'
    },
    'qq': {
        'MAIL_HOST': 'smtp.qq.com',
        'MAIL_PORT': 587,
        'MAIL_ENCRYPTION': 'tls',
        'note': 'Need to enable SMTP service and use auth code'
    }
}

if __name__ == "__main__":
    # CLI menu loop

    print("Chat App email service test tool")
    print("=" * 50)
    
    while True:
        print("\nSelect operation:")
        print("1. View configuration status")
        print("2. Test email service")
        print("3. View SMTP setup guide")
        print("0. Exit")
        
        choice = input("\nSelect (0-3): ").strip()
        
        if choice == "1":
            show_config_status()
        elif choice == "2":
            test_email_service()
        elif choice == "3":
            show_smtp_guide()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again")
