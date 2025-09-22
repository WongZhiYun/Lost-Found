"""
Main page component
"""
from typing import Optional
from nicegui import app, ui # type: ignore
from file.chat_v2.chat_config import config
from ..services.database import SessionLocal
from ..components.sidebar import create_sidebar
from ..components.chat_area import create_chat_area
from ..components.empty_state import show_empty_state
from ..handlers.chat import create_chat_interface
from file.models import User


"""Main chat page"""
def main_page(chat_with: Optional[int] = None):
    # Add CSS styles and meta tags
    _add_page_styles()
    
    current_user_id = app.storage.user['user_id']
    db = SessionLocal()
    
    # Check if there is a success message to display
    if 'show_success_message' in app.storage.user:
        success_message = app.storage.user.pop('show_success_message')  # Get and delete message
        ui.timer(0.3, lambda: ui.notify(success_message, color='positive'), once=True)
    
    # Set page background
    ui.query('body').style('background-color: #f0f2f5; margin: 0; padding: 0;')
    
    # Add mobile overlay logic
    _add_mobile_overlay_script()
    
    # Create main layout
    with ui.element('div').classes('custom-container'):
        # Left sidebar
        conversations_container = create_sidebar(db, current_user_id)
        
        # Right chat area
        chat_container = create_chat_area()
    
    # Check if we should open a specific chat
    if chat_with:
        # Validate chat_with ID
        if _validate_chat_partner(db, chat_with, current_user_id):
            ui.timer(0.2, lambda: create_chat_interface(chat_with, chat_container), once=True)
        else:
            # Invalid chat partner, redirect to main page
            ui.navigate.to('/')
            return
    else:
        # Show empty state
        show_empty_state(chat_container)


"""Add page styles"""
def _add_page_styles():
    ui.add_head_html(f'''
    <link rel="stylesheet" href="{config.STYLES_PATH}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no">
    <style>
        /* Fallback for browsers that don't support dvh */
        @supports not (height: 100dvh) {{
            html, body, .custom-container, .custom-chat {{
                height: calc(100vh - env(safe-area-inset-bottom, 0px)) !important;
            }}
        }}
        /* Prevent address bar affecting layout on mobile */
        @media screen and (max-width: 768px) {{
            html, body {{
                height: -webkit-fill-available !important;
            }}
            .custom-container, .custom-chat {{
                height: -webkit-fill-available !important;
            }}
        }}
    </style>
    ''')


"""Add mobile overlay JavaScript"""
def _add_mobile_overlay_script():
    ui.add_head_html('''
    <script>
        function createMobileOverlay() {
            if (window.innerWidth <= 768 && !document.querySelector('.sidebar-overlay')) {
                const overlay = document.createElement('div');
                overlay.className = 'sidebar-overlay';
                overlay.onclick = function() {
                    document.querySelector('.custom-sidebar').classList.remove('mobile-open');
                    overlay.classList.remove('active');
                };
                document.body.appendChild(overlay);
            }
        }
        
        // Create overlay only if on mobile
        if (window.innerWidth <= 768) {
            document.addEventListener('DOMContentLoaded', createMobileOverlay);
        }
        
        // Handle window resize
        window.addEventListener('resize', function() {
            const overlay = document.querySelector('.sidebar-overlay');
            if (window.innerWidth > 768 && overlay) {
                overlay.remove(); // Remove overlay on desktop
            } else if (window.innerWidth <= 768 && !overlay) {
                createMobileOverlay(); // Create overlay on mobile
            }
        });
    </script>
    ''')


"""Validate chat partner ID"""
def _validate_chat_partner(db, partner_id: int, current_user_id: int) -> bool:
    """
    Validate if the chat partner ID is valid:
    1. Check if partner exists in database
    2. Check if partner is not the current user
    """
    try:
        # Convert to int if it's a string
        partner_id = int(partner_id)
        
        # Check if partner is not the current user (can't chat with self)
        if partner_id == current_user_id:
            print(f"Cannot chat with self: {partner_id}")
            return False
        
        # Check if partner exists in database
        partner = db.query(User).get(partner_id)
        if not partner:
            print(f"User not found: {partner_id}")
            return False
        
        return True
        
    except (ValueError, TypeError):
        print(f"Invalid partner ID format: {partner_id}")
        return False
    except Exception as e:
        print(f"Error validating partner: {e}")
        return False
