# Chat App 

A modern chat application built with NiceGUI, featuring WhatsApp-like UI and messaging capabilities.

## 🚀 Quick Start

### 1. Clone and Install Dependencies

**Linux/macOS:**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Windows:**
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Email Settings (Required)
A `.env.example` file is provided in the project root. Simply copy it to `.env` and update the values as needed:

```bash
# Gmail Configuration (Recommended)
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM_ADDRESS=your_email@gmail.com
MAIL_ENCRYPTION=tls

# Application Settings
APP_NAME="First Web App"
SECRET_KEY="your_secret_key"
HOST="localhost"
PORT="8080"
```

#### Gmail Setup Steps:
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Enable 2-factor authentication if not already enabled
3. Generate an app-specific password (16 characters)
4. Use this password as `MAIL_PASSWORD` in your `.env` file

#### Generating a Secure `SECRET_KEY`
The `SECRET_KEY` is crucial for securing user sessions. You should generate a long, random string for this value. You can use the following command to generate a cryptographically secure key:

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Copy the output of this command and paste it as the value for `SECRET_KEY` in your `.env` file.

### 3. Start the Server ( Make sure in virtual environment )
```bash
python app.py
```

The application will be available at `http://localhost:8080`

### 4. Create Test Users (Optional)
```bash
python -m test.seed_user
```

## 📧 Email Providers Configuration

### Outlook/Hotmail
```bash
MAIL_HOST=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_ENCRYPTION=tls
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
```

### QQ Mail
```bash
MAIL_HOST=smtp.qq.com
MAIL_PORT=587
MAIL_ENCRYPTION=tls
MAIL_USERNAME=your_email@qq.com
MAIL_PASSWORD=your_auth_code
```

### 163 Mail
```bash
MAIL_HOST=smtp.163.com
MAIL_PORT=587
MAIL_ENCRYPTION=tls
MAIL_USERNAME=your_email@163.com
MAIL_PASSWORD=your_auth_code
```

## 🏗️ Project Structure

```
chat/
├── app.py                 # Main application entry point
├── config.py              # Application configuration
├── models.py              # Database models
├── requirements.txt       # Python dependencies
│
├── pages/                 # Page components
│   ├── auth.py           # Login/Register pages
│   ├── main.py           # Main chat page
│   └── chat.py           # Chat routing
│
├── components/            # Reusable UI components
│   ├── sidebar.py        # Chat sidebar
│   ├── chat_area.py      # Chat messages area
│   ├── dialogs.py        # Modal dialogs
│   ├── empty_state.py    # Empty State
│
├── handlers/              # Business logic
│   ├── auth.py           # Authentication logic
│   └── chat.py           # Chat message handling
│
├── services/              # External services
│   ├── database.py       # Database service
│   ├── email.py          # Email service
│
├── core/                  # Core utilities
│   ├── startup_checker.py # System health checks
│   └── utils.py          # Utility functions
│   └── middleware.py      # Middleware functions
│
├── static/                # Static files
│   └── styles.css         # styling
│   └── logo.png           # Brand Logo
│   └── favicon.ico        
│
└── test/                  # Development tools
    ├── seed_user.py      # Test user creation
    └── test_email.py     # Email testing
```

## ✨ Features

- **WhatsApp-like UI**: Modern, responsive design
- **Email Notifications**: Get notified of new messages via email
- **User Authentication**: Secure login and registration
- **Mobile Responsive**: Works on desktop and mobile devices
- **SQLite Database**: Lightweight database for development

## 🔧 Configuration Options

All configuration is managed through environment variables in the `.env` file:

- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: 8080)
- `DEBUG`: Debug mode (default: false)
- `DATABASE_URL`: Database connection (default: SQLite)
- `EMAIL_NOTIFICATIONS_COOLDOWN`: Email cooldown in seconds (default: 600)

## 🛡️ Security Notes

- Never commit your `.env` file to version control
- Use app-specific passwords for email providers
- Change the `SECRET_KEY` in production
- Add `.env` to your `.gitignore` file

## 🧪 Testing

```bash
# Test email configuration
python -m test.test_email

# Create test users
python -m test.seed_user
```

## 📱 Usage

1. Register a new account or login
2. Click "New Chat" to start a conversation
3. Select a user to chat with
4. Start sending messages
5. Receive email notifications for new messages

---

Built with ❤️ using [NiceGUI](https://nicegui.io/) and modern web technologies.