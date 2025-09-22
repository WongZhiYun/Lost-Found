"""
Dialog components
"""
from nicegui import app, ui
from sqlalchemy import text
from file.models import User
from ..services.database import SessionLocal


"""Open new chat dialog"""
def open_new_chat_dialog():
    with ui.dialog() as dialog, ui.card().classes('w-96 p-6 !rounded-xl shadow-lg'):
        ui.label('Start a new chat').classes('text-xl font-semibold mb-4 text-gray-800')
        
        # Search input box
        search_input = ui.input(placeholder='Search contacts').props('borderless clearable').classes(
            'w-full mb-4 px-4 bg-gray-100 rounded-full whatsapp-dialog-search'
        ).on_value_change(lambda: ui.timer(0.3, load_dialog_users, once=True))
        
        # Users list container
        users_container = ui.element('div').classes('max-h-64 overflow-y-auto w-full')
        
        def load_dialog_users():
            """Load users list in the dialog"""
            users_container.clear()
            db = SessionLocal()
            current_user_id = app.storage.user['user_id']
            
            # Query users (exclude current user)
            query = db.query(User).filter(User.id != current_user_id)
            
            # Search filter
            search_term = search_input.value.strip() if search_input.value else ""
            if search_term:
                # Use proper SQL LIKE query
                query = query.filter(text(f"lower(username) LIKE lower('%{search_term}%')"))
                users = query.limit(5).all()
            else:
                # Default: show only first 5 users
                users = query.limit(5).all()
            
            # Close database session
            db.close()
            
            # Show users list
            with users_container:
                if not users:
                    if search_term:
                        ui.label(f'No users found for "{search_term}"').classes('text-gray-500 text-center py-8')
                    else:
                        ui.label('No users available').classes('text-gray-500 text-center py-8')
                else:
                    for user in users:
                        _create_user_item(user, dialog)
        
        # Initial load users
        load_dialog_users()
        
        # Close button
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat').classes('text-gray-600')
    
    dialog.open()


"""Create user item"""
def _create_user_item(user, dialog):
    
    """
    Create a clickable user item in the dialog.
    - Shows user avatar and name
    - Clicking starts a new chat with that user
    """

    def create_chat_handler(u_id):
        """Return handler that closes dialog and navigates to chat with selected user"""
        def start_chat():
            # Close the "new chat" dialog
            dialog.close()
            # Navigate to the main page with query param for selected user
            ui.navigate.to(f'/?chat_with={u_id}')
        return start_chat
    
    # Create a clickable user item inside the dialog
    with ui.element('div').classes('custom-dialog-user-item').on('click', create_chat_handler(user.id)): # Attach handler for starting chat
         # User avatar (generated using robohash)
        ui.image(f'https://robohash.org/{user.username}.png').classes('w-10 h-10 rounded-full object-cover mr-2 bg-gray-300')
        # User info (username + subtitle)
        with ui.element('div').classes('flex-1'):
            ui.label(str(user.username)).classes('font-medium text-gray-900')
            ui.label('Click to start chatting').classes('text-sm text-gray-500')
