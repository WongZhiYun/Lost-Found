"""
Empty state component
"""
from nicegui import ui
from file.chat_v2.chat_config import config


"""Show empty chat state"""
def show_empty_state(container):
    container.clear()
    
    with container:
        # Mobile header (for empty state)
        _create_empty_state_header()
        
        # Empty state content
        _create_empty_state_content()


"""Create empty state header"""
def _create_empty_state_header():
    with ui.element('div').classes('custom-chat-header'):
        # Mobile menu button
        ui.icon('menu').classes('mobile-menu-btn').on('click', lambda: _toggle_main_sidebar())
        
        # Application title
        ui.label(config.APP_NAME).classes('text-lg font-medium text-gray-900')
        ui.space()


"""Create empty state content"""
def _create_empty_state_content():
    with ui.element('div').classes('custom-empty-state'):
        ui.icon('chat', size='3rem').classes('text-gray-400 mb-4')
        ui.label(config.APP_NAME).classes('text-3xl font-light text-gray-700 my-4')
        ui.label('Send and receive messages without keeping your phone online.').classes(
            'text-gray-500 text-center max-w-md'
        )


"""Toggle main sidebar"""
def _toggle_main_sidebar():
    ui.run_javascript('''
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
    ''')
