"""
Authentication pages
"""
from nicegui import ui
from config import config
from core.utils import validate_email
from handlers.auth import handle_login, handle_register


"""Login/Register page"""
def show_login_page():
    """Set page styles"""
    ui.query('body').style(
        'background: linear-gradient(134deg, #2563eb 0%, #1e40af 100%); '
        'margin: 0; padding: 0;'
    )
    
    with ui.column().classes('w-full h-screen justify-center items-center px-4'):
        with ui.card().classes('w-full max-w-md mx-4 p-4 rounded-2xl bg-white/95 backdrop-blur-lg shadow-2xl'):
            # Application title
            ui.label(config.APP_NAME).classes('w-full text-center text-3xl font-bold mb-6 text-gray-800')
            
            # Tabs
            with ui.tabs().classes('w-full mb-4 px-4') as tabs:
                ui.tab('Login')
                ui.tab('Register')
            
            with ui.tab_panels(tabs, value='Login').classes('w-full bg-transparent'):
                # Login panel
                with ui.tab_panel('Login'):
                    _create_login_form()
                
                # Register panel
                with ui.tab_panel('Register'):
                    _create_register_form()


"""Create login form"""
def _create_login_form():

    ui.query('.q-field--outlined .q-field__control').classes('!rounded-lg')

    username_login = ui.input('Username').classes('w-full mb-4').props('outlined').props('required')
    password_login = ui.input('Password', password=True, password_toggle_button=True).classes('w-full mb-4').props('outlined').props('required')
    
    # Validate input and login
    def validate_and_login():
        # Check empty fields
        if not username_login.value or not username_login.value.strip():
            ui.notify('Please enter username', color='negative')
            username_login.props('error error-message="Username is required"')
            return
        
        if not password_login.value or not password_login.value.strip():
            ui.notify('Please enter password', color='negative') 
            password_login.props('error error-message="Password is required"')
            return
            
        # Clear error status
        username_login.props(remove='error')
        password_login.props(remove='error')
        
        # Execute login
        handle_login(username_login.value.strip(), password_login.value.strip())
    
    ui.button(
        'Login', 
        on_click=validate_and_login
    ).classes('w-full py-3 rounded-lg bg-green-600 text-white font-semibold hover:bg-green-700')


"""Create register form"""
def _create_register_form():

    ui.query('.q-field--outlined .q-field__control').classes('!rounded-lg')

    username_reg = ui.input('Username', validation={'Username must be at least 3 characters': lambda value: len(value) >= 3}).classes('w-full').props('outlined').props('required')
    email_reg = ui.input('Email', validation={'Invalid email format': lambda value: validate_email(value)}).classes('w-full').props('outlined').props('required')
    password_reg = ui.input('Password', password=True, password_toggle_button=True, validation={'Password must be at least 8 characters': lambda value: len(value) >= 8}).classes('w-full mb-4').props('outlined').props('required')
    
    # Validate input and register
    def validate_and_register():
        # Check empty fields
        if not username_reg.value or not username_reg.value.strip():
            ui.notify('Please enter username', color='negative')
            username_reg.props('error error-message="Username is required"')
            return
            
        if not email_reg.value or not email_reg.value.strip():
            ui.notify('Please enter email', color='negative')
            email_reg.props('error error-message="Email is required"')
            return
            
        if not password_reg.value or not password_reg.value.strip():
            ui.notify('Please enter password', color='negative')
            password_reg.props('error error-message="Password is required"')
            return
        
        # Clear error status
        username_reg.props(remove='error')
        email_reg.props(remove='error')
        password_reg.props(remove='error')
        
        # Execute register
        handle_register(username_reg.value.strip(), email_reg.value.strip(), password_reg.value.strip())
    
    ui.button(
        'Register',
        on_click=validate_and_register
    ).classes('w-full py-3 rounded-lg bg-green-600 text-white font-semibold hover:bg-green-700')
