"""
Chat area component
"""
from nicegui import ui
from core.utils import safe_str


"""Create chat area component"""  
def create_chat_area():
    chat_container = ui.element('div').classes('custom-chat')
    return chat_container


"""Create chat header component"""
def create_chat_header(partner, on_menu_click=None):
    with ui.element('div').classes('custom-chat-header'):
        # Mobile menu button
        menu_btn = ui.icon('menu').classes('mobile-menu-btn')
        if on_menu_click:
            menu_btn.on('click', on_menu_click)
        
        # User avatar and information
        ui.image(f'https://robohash.org/{partner.username}.png').classes('h-12 w-12 rounded-full flex-shrink-0 bg-gray-300')
        with ui.element('div').classes('ml-3'):
            ui.label(safe_str(partner.username)).classes('text-lg font-medium text-gray-900')
        
        ui.space()


"""Create input area component"""
def create_input_area(on_send=None, on_enter=None):
    with ui.element('div').classes('custom-input-area'):

        ui.query('.q-btn--fab').classes('!p-2 !min-w-12 !min-h-12')
        
        # FAB button (attachment)
        with ui.fab('add', direction='up'):
            ui.fab_action('image', label='Picture').classes('!mb-3 !ml-10')
        
        # Message input box
        message_input = ui.input(placeholder='Type a message').props('borderless').classes('flex-1 rounded-full')
        
        # Send button
        send_btn = ui.button(icon='send').classes('p-6 custom-btn')
        if on_send:
            send_btn.on('click', lambda: on_send(message_input))
        
        # Enter key send
        if on_enter:
            message_input.on('keydown.enter', lambda: on_enter(message_input))
        
        return message_input


"""Create messages container component"""
def create_messages_container():
    messages_container = ui.element('div').classes('custom-messages')
    return messages_container


"""Create message bubble component"""
def create_message_bubble(msg, current_user_id: int):
    is_sent = msg.sender_id == current_user_id
    time_str = msg.created_at.strftime('%H:%M')
    
    message_class = 'custom-message sent' if is_sent else 'custom-message received'
    
    with ui.element('div').classes(message_class):
        with ui.element('div').classes('px-3 py-2'):
            ui.html(f'<div>{safe_str(msg.content)}</div>')
            ui.label(time_str).classes('text-right mt-2 text-gray-500 text-xs')


"""Toggle sidebar JavaScript code"""
def toggle_sidebar_js(show: bool):
    if show:
        return '''
            if (window.innerWidth <= 768) {
                const sidebar = document.querySelector('.custom-sidebar');
                let overlay = document.querySelector('.sidebar-overlay');
                
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.className = 'sidebar-overlay';
                    overlay.onclick = function() {
                        sidebar.classList.remove('mobile-open');
                        overlay.classList.remove('active');
                        overlay.style.left = '0';
                    };
                    document.body.appendChild(overlay);
                }
                
                sidebar.classList.add('mobile-open');
                overlay.classList.add('active');
                // Don't cover sidebar
                if (window.innerWidth <= 480) {
                    overlay.style.left = '280px';
                } else {
                    overlay.style.left = '340px';
                }
            }
        '''
    else:
        return '''
            const sidebar = document.querySelector('.custom-sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            if (sidebar) sidebar.classList.remove('mobile-open');
            if (overlay) {
                overlay.classList.remove('active');
                overlay.style.left = '0';
            }
        '''