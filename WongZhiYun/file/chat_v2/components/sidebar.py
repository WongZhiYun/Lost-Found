"""
Sidebar component
"""
from nicegui import ui
from sqlalchemy import or_
from ..core.utils import format_timestamp, truncate_message
from file.models import Message, User
from ..components.dialogs import open_new_chat_dialog
from ..handlers.auth import handle_logout


"""Create sidebar component"""
def create_sidebar(db, current_user_id: int):
    with ui.element('div').classes('custom-sidebar'):
        # Sidebar header
        _create_sidebar_header(db, current_user_id)
        
        # Search bar
        search_input = _create_search_bar()
        
        # Conversations list
        conversations_container = ui.element('div').classes('custom-conversations flex-1 overflow-y-auto')
        
        # Load conversations list function
        def load_conversations_with_search():
            search_term = search_input.value.strip() if search_input.value else ""
            load_conversations(db, current_user_id, conversations_container, search_term)
        
        # Initial load
        load_conversations_with_search()
        
        # Bind search functionality with debounce
        def search_conversations():
            """Search conversations with a small delay to avoid too many requests"""
            load_conversations_with_search()
        
        search_input.on_value_change(lambda: ui.timer(0.3, search_conversations, once=True))
        
        return conversations_container


"""Create sidebar header"""
def _create_sidebar_header(db, current_user_id: int):
    with ui.element('div').classes('custom-sidebar-header'):
        with ui.row().classes('w-full items-center'):
            # Current user avatar
            current_user = db.query(User).get(current_user_id)
            if current_user:
                ui.image(f'https://robohash.org/{current_user.username}.png').classes('w-12 h-12 rounded-full flex-shrink-0 bg-gray-300')
                
            
            ui.space()
            
            # New chat button
            ui.button(icon='add').props('flat round dense').classes('text-gray-600').on(
                'click', lambda: open_new_chat_dialog()
            )
            
            # More menu
            with ui.button(icon='more_vert').props('flat round dense').classes('text-gray-600'):
                with ui.menu():
                    ui.menu_item('Logout', handle_logout)


"""Create search bar"""
def _create_search_bar(): # Input for searching by username
    search_input = ui.input(placeholder='Search or start new chat').props(' clearable').classes('w-full bg-gray-100 px-4 py-2 ')
    return search_input

"""Load conversations list"""
def load_conversations(db, current_user_id: int, container, search_term: str = ""):
    container.clear()
    
    # Get all related messages
    messages = db.query(Message).filter(
        or_(getattr(Message, 'sender_id') == current_user_id, getattr(Message, 'receiver_id') == current_user_id)
    ).order_by(getattr(Message, 'created_at').desc()).all()

    # Get the last message for each conversation partner
    partners_with_last_message = {}
    for msg in messages:
        # Identify partner (the other user in the conversation)
        partner_id = msg.receiver_id if msg.sender_id == current_user_id else msg.sender_id
        
        # If we don't already have this partner, save their latest message
        if partner_id not in partners_with_last_message:
            partner_user = db.query(User).get(partner_id)
            if partner_user:
                # Apply search filter
                if search_term:
                    if search_term.lower() not in partner_user.username.lower():
                        continue
                
                partners_with_last_message[partner_id] = {
                    'user': partner_user,
                    'last_message': str(msg.content) if msg.content else "Image",
                    'created_at': msg.created_at
                }

    # If there are no conversations, show empty state
    if not partners_with_last_message:
        if search_term:
            _show_conversations_search_empty_state(container, search_term)
        else:
            _show_conversations_empty_state(container)
        return

    # Show conversations list
    with container:
        for partner_id, data in partners_with_last_message.items():
            _create_conversation_item(partner_id, data)


"""Show conversations list empty state"""
def _show_conversations_empty_state(container):
    # Shown when user has no chats at all
    with container:
        with ui.column().classes('flex-grow items-center justify-center p-8'):
            ui.icon('chat', size='3rem').classes('text-gray-400 mb-4')
            ui.label('No conversations yet').classes('text-gray-500 text-center')
            ui.label('Start a new chat to see your conversations here').classes('text-gray-400 text-sm text-center')


"""Show search empty state"""
def _show_conversations_search_empty_state(container, search_term: str):
    with container:
        # Shown when search yields no results
        with ui.column().classes('flex-grow items-center justify-center p-8'):
            ui.icon('search_off', size='3rem').classes('text-gray-400 mb-4')
            ui.label(f'No results for "{search_term}"').classes('text-gray-500 text-center')
            ui.label('Try searching for a different name').classes('text-gray-400 text-sm text-center')


"""Create single conversation item"""
def _create_conversation_item(partner_id: int, data: dict):
    partner = data['user']
    last_message = data['last_message']
    timestamp = data['created_at']
    
    # Format time
    time_str = format_timestamp(timestamp)
    
    # Create click handler
    def create_click_handler(p_id):
        return lambda: ui.navigate.to(f'/?chat_with={p_id}')
    
    # Conversation item container
    with ui.element('div').classes('custom-conversation-item').on('click', create_click_handler(partner_id)):
        ui.image(f'https://robohash.org/{partner.username}.png').classes('w-12 h-12 rounded-full flex-shrink-0 bg-gray-300')

        # Conversation details (name + last message)
        with ui.element('div').classes('flex-1 min-w-0'):
            ui.label(partner.username).classes('custom-conversation-name text-sm font-normal text-gray-900 mb-0.5 truncate')
            display_message = truncate_message(last_message)
            ui.label(display_message).classes('custom-conversation-last-message text-sm font-normal text-gray-500 truncate')
        # Timestamp of last message
        ui.label(time_str).classes('custom-conversation-time text-sm text-gray-500 whitespace-nowrap')
