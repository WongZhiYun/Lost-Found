"""
Chat handlers
"""
from nicegui import app, ui
from sqlalchemy import or_
from models import Message, User
from services.database import SessionLocal
from services.email import email_service
from components.chat_area import (
    create_chat_header, create_input_area, create_messages_container,
    create_message_bubble, toggle_sidebar_js
)
from core.utils import format_timestamp, truncate_message


"""Send new message"""
def send_message(input_field, messages_container, current_user_id: int, partner_id: int):
    text = input_field.value.strip()

    if not text:
        return
    
    db = SessionLocal()

    try:
        current_user = db.query(User).get(current_user_id)
        partner = db.query(User).get(partner_id)
        
        if not current_user or not partner:
            return
        
        # Save message to database
        new_msg = Message(content=text, sender_id=current_user_id, receiver_id=partner_id)
        db.add(new_msg)
        db.commit()
        
        # Immediately clear input field - do not wait for email sending
        input_field.value = ''
        
        # Immediately reload messages - do not wait for email sending
        load_chat_messages(db, current_user_id, partner_id, messages_container)
        
        # Extract data to simple variables, avoid SQLAlchemy session issues
        partner_email = partner.email
        partner_username = partner.username
        sender_username = current_user.username
        
        if partner_email:  # Only send email notification if there is an email
            print(f"Prepare to send email notification to {partner_username} ({partner_email})")
            # Delay email sending to next event loop, pass simple data types
            ui.timer(0.01, lambda: _send_email_notification_async(
                partner_email, partner_username, sender_username
            ), once=True)
        else:
            print(f"{partner_username} has no email, skipping email notification")
        
        # If receive a new message, dynamically update the sidebar (no page refresh)
        _refresh_if_new_conversation(db, current_user_id, partner_id)
        
    except Exception as e:
        db.rollback()
        ui.notify(f'Failed to send message: {str(e)}', color='negative')
        print(f"Error sending message: {e}")
    finally:
        db.close()


def open_chat(partner_id: int, container):
    """Open chat with specific user"""
    # Set global chat partner ID
    global current_chat_partner_id
    current_chat_partner_id = partner_id
    
    # Create chat interface
    create_chat_interface(partner_id, container)


def create_chat_interface(partner_id: int, container):
    """Create chat interface - business logic layer"""
    db = SessionLocal()
    current_user_id = app.storage.user['user_id']
    partner = db.query(User).get(partner_id)
    
    if not partner:
        return
        
    container.clear()
    
    with container:
        # Chat header
        create_chat_header(partner, on_menu_click=lambda: ui.run_javascript(toggle_sidebar_js(True)))
        
        # Messages area
        messages_container = create_messages_container()
        load_chat_messages(db, current_user_id, partner_id, messages_container)
        
        # Input area
        message_input = create_input_area(
            on_send=lambda input_field: send_message(input_field, messages_container, current_user_id, partner_id),
            on_enter=lambda input_field: send_message(input_field, messages_container, current_user_id, partner_id)
        )


def load_chat_messages(db, current_user_id: int, partner_id: int, container):
    """Load chat messages - business logic layer"""
    container.clear()
    
    # Get all messages between two users
    messages = db.query(Message).filter(
        or_(
            (getattr(Message, 'sender_id') == current_user_id) & (getattr(Message, 'receiver_id') == partner_id),
            (getattr(Message, 'sender_id') == partner_id) & (getattr(Message, 'receiver_id') == current_user_id)
        )
    ).order_by(getattr(Message, 'created_at').desc()).all()
    
    # Display messages
    with container:
        for msg in messages:
            create_message_bubble(msg, current_user_id)


def _send_email_notification_async(partner_email: str, partner_username: str, sender_username: str):
    """Asynchronous sending email notification - background task, do not block UI"""
    if email_service and partner_email:
        try:
            print(f"📧 Start sending email notification to {partner_username} ({partner_email})")
            result = email_service.send_new_message_notification(
                recipient_email=partner_email,
                recipient_name=partner_username,
                sender_name=sender_username,
                message_count=1
            )
            if result:
                print(f"✅ Email notification sent successfully: {partner_email}")
            else:
                print(f"⚠️ Email notification sent failed (cooldown or other reasons): {partner_email}")
        except Exception as e:
            print(f"❌ Email notification sent exception: {e}")


"""If receive a new message, dynamically update the sidebar (no page refresh)"""
def _refresh_if_new_conversation(db, current_user_id: int, partner_id: int):
    # Use JavaScript to dynamically update the sidebar, not refresh the entire page
    ui.timer(0.1, lambda: _update_sidebar_dynamically(db, current_user_id, partner_id), once=True)


"""Dynamically update the sidebar, add new conversation items"""
def _update_sidebar_dynamically(db, current_user_id: int, partner_id: int):
    try:
        partner = db.query(User).get(partner_id)
        if not partner:
            return
            
        # Get latest message
        latest_message = db.query(Message).filter(
            or_(
                (getattr(Message, 'sender_id') == current_user_id) & (getattr(Message, 'receiver_id') == partner_id),
                (getattr(Message, 'sender_id') == partner_id) & (getattr(Message, 'receiver_id') == current_user_id)
            )
        ).order_by(getattr(Message, 'created_at').desc()).first()
        
        if not latest_message:
            return
            
        time_str = format_timestamp(latest_message.created_at)
        
        # Truncate message
        message_preview = truncate_message(latest_message.content)
        
        # Use JavaScript to dynamically add conversation items to the top of the sidebar
        js_code = f"""
        (function() {{
            const conversationsContainer = document.querySelector('.custom-conversations');
            if (!conversationsContainer) return;
            
            // First, remove any empty state messages
            const emptyStates = conversationsContainer.querySelectorAll('.flex-grow.items-center.justify-center');
            emptyStates.forEach(emptyState => {{
                emptyState.remove();
                // console.log('🗑️ Removed empty state message');
            }});
            
            // Also remove any standalone icons and labels (backup cleanup)
            const chatIcons = conversationsContainer.querySelectorAll('i');
            const labels = conversationsContainer.querySelectorAll('div');
            labels.forEach(label => {{
                if (label.textContent && (
                    label.textContent.includes('No conversations yet') || 
                    label.textContent.includes('Start a new chat to see')
                )) {{
                    label.parentElement && label.parentElement.remove();
                    // console.log('🗑️ Removed empty state label');
                }}
            }});
            
            // Check if the conversation item already exists - use data attribute for more reliable identification
            const existingItems = conversationsContainer.querySelectorAll('.custom-conversation-item');
            let existingItem = null;
            for (let item of existingItems) {{
                const partnerName = item.querySelector('.custom-conversation-name');
                if (partnerName && partnerName.textContent.trim() === '{partner.username}') {{
                    existingItem = item;
                    break;
                }}
            }}
            
            if (existingItem) {{
                // Update existing item and move to top
                const messagePreview = existingItem.querySelector('.custom-conversation-last-message');
                const timeDisplay = existingItem.querySelector('.custom-conversation-time');
                if (messagePreview) messagePreview.textContent = '{message_preview}';
                if (timeDisplay) timeDisplay.textContent = '{time_str}';
                
                // Move to top
                conversationsContainer.insertBefore(existingItem, conversationsContainer.firstChild);
                console.log('⬆️ Updated and moved existing conversation to top');
                return;
            }}
            
            // Not exists, create new conversation item
            const newItem = document.createElement('div');
            newItem.className = 'custom-conversation-item';
            newItem.setAttribute('data-partner-id', '{partner_id}');
            newItem.onclick = function() {{ 
                window.location.href = '/?chat_with={partner_id}'; 
            }};
            
            newItem.innerHTML = `
                <img src="https://robohash.org/{partner.username}.png" class="w-12 h-12 rounded-full flex-shrink-0 bg-gray-300">
                <div class="flex-1 min-w-0">
                    <div class="custom-conversation-name text-sm font-normal text-gray-900 mb-0.5 truncate">{partner.username}</div>
                    <div class="custom-conversation-last-message text-sm font-normal text-gray-500 truncate">{message_preview}</div>
                </div>
                <div class="custom-conversation-time text-sm text-gray-500 whitespace-nowrap">{time_str}</div>
            `;
            
            // Add to the top
            conversationsContainer.insertBefore(newItem, conversationsContainer.firstChild);
            
            // console.log('✅ New conversation item added to the sidebar');
        }})();
        """
        
        ui.run_javascript(js_code)
        print(f"✅ Sidebar dynamically updated, added conversation with {partner.username}")
        
    except Exception as e:
        print(f"❌ Dynamically update sidebar failed: {e}")


# Global variable: current chat partner ID
current_chat_partner_id = None
