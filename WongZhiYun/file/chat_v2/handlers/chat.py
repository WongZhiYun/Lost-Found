"""
Chat handlers - Business Logic Layer
Handles message sending, database interactions, and triggers email notifications.
"""
from nicegui import app, ui
from sqlalchemy import or_
from file.models import Media, Message, User
from ..services.database import SessionLocal
from ..services.email import email_service  # ✅ Import global email service
from ..components.chat_area import (
    create_chat_header, create_input_area, create_messages_container,
    create_message_bubble
)
from pathlib import Path
from typing import List, Dict


def create_chat_interface(partner_id: int, container: ui.element) -> None:
    """Builds the complete chat interface for a given partner."""
    db = SessionLocal()
    try:
        current_user_id = app.storage.user['user_id']
        partner = db.query(User).get(partner_id)
        if not partner:
            # Show error if user not found
            ui.label("User not found.").classes('m-4')
            return
            
        # Reset container and build UI    
        container.clear()
        with container:
            # Chat header (partner name, back/menu buttons)
            create_chat_header(partner, on_menu_click=lambda: ui.run_javascript(_toggle_sidebar_js(True)))
            # Messages container
            messages_container = create_messages_container()

            # Image viewer dialog
            with ui.dialog().props('maximized') as image_dialog, ui.card().classes('!p-0 !max-w-full !max-h-full'):
                ui.button(icon='close', on_click=image_dialog.close).props(
                    'flat round dense'
                ).classes('absolute top-2 right-2 z-10 bg-black/20 text-white')
                image_carousel = ui.carousel(animated=True, arrows=True, navigation=True).classes(
                    'w-full h-full bg-black'
                ).props('swipeable draggable transition-prev="slide-right" transition-next="slide-left"')
            
            # Function to open image viewer
            def open_image_viewer(media_items, start_index):
                image_carousel.clear()
                with image_carousel:
                    for i, item in enumerate(media_items):
                        with ui.carousel_slide(name=f'slide_{i}'):
                            ui.image(f"/static/uploads/{item.file_url}").props(
                                'fit=contain'
                            ).classes('w-full h-screen')
                target_slide_name = f'slide_{start_index}'
                # Delay slide change to ensure rendering
                ui.timer(0.1, lambda: image_carousel.set_value(target_slide_name), once=True)
                image_dialog.open()

            # Load messages
            _reload_and_display_messages(db, current_user_id, partner_id, messages_container, open_image_viewer)
            
            # Input area
            create_input_area(
                on_send=lambda input_field, images: send_message(
                    input_field, images, messages_container, current_user_id, partner_id, open_image_viewer
                )
            )
    finally:
        db.close()


def send_message(input_field, images_to_upload: List[Dict], messages_container,
                 current_user_id: int, partner_id: int, open_viewer_func):
    """Handles sending a message: save to DB, update UI, and send email notification."""
    text = input_field.value.strip()
    saved_filenames = []
    db = SessionLocal()

    try:
        # Save uploaded files
        if images_to_upload:
            saved_filenames = _save_uploaded_images(images_to_upload)
            if not saved_filenames:
                raise Exception("File saving failed")

        # Save message
        new_msg = Message(sender_id=current_user_id, receiver_id=partner_id, content=text or None)
        for filename in saved_filenames:
            media = Media(file_url=filename, message_id=new_msg.id)
            new_msg.media_items.append(media)

        db.add(new_msg)
        db.commit()

        print(f"Message saved to DB - ID: {new_msg.id}")
        # Clear input field after sending
        input_field.set_value('')

        # Update UI
        _reload_and_display_messages(db, current_user_id, partner_id, messages_container, open_viewer_func)

        # Send email notification
        partner = db.query(User).get(partner_id)
        sender = db.query(User).get(current_user_id)
        if email_service and partner and partner.email:
            email_service.send_new_message_notification(
                recipient_email=partner.email,
                recipient_name=partner.username,
                sender_name=sender.username if sender else "Someone"
            )

    except Exception as e:
        db.rollback()
        ui.notify(f'Failed to send message: {str(e)}', color='negative')
        print(f"Transaction failed: {e}")
        # Cleanup uploaded files on failure
        _cleanup_failed_upload(saved_filenames)
    finally:
        db.close()


# --- Helpers ---
def _reload_and_display_messages(db, current_user_id, partner_id, container, open_viewer_func):
    container.clear()
    messages = db.query(Message).filter(
        or_(
            (Message.sender_id == current_user_id) & (Message.receiver_id == partner_id),
            (Message.sender_id == partner_id) & (Message.receiver_id == current_user_id)
        )
    ).order_by(Message.created_at.desc()).all()
    
    with container:
        for msg in messages:
            create_message_bubble(msg, current_user_id, open_viewer_func)


def _save_uploaded_images(images_to_upload: List[Dict]) -> List[str]:
    saved_filenames = []
    uploads_dir = Path('static/uploads')
    uploads_dir.mkdir(parents=True, exist_ok=True)
    for image_data in images_to_upload:
        file_path = uploads_dir / image_data['uuid_name']
        try:
            with open(file_path, 'wb') as f:
                f.write(image_data['content'])
            saved_filenames.append(image_data['uuid_name'])
            print(f"Image saved: {file_path}")
        except Exception as e:
            print(f"Failed to save image {image_data['uuid_name']}: {e}")
            _cleanup_failed_upload(saved_filenames)
            return []
    return saved_filenames


def _cleanup_failed_upload(filenames: List[str]):
    if not filenames:
        return
    print(f"Rolling back uploads: {filenames}")
    for filename in filenames:
        try:
            (Path('static/uploads') / filename).unlink(missing_ok=True)
        except Exception as e:
            print(f"Failed to delete file during cleanup: {e}")


def _toggle_sidebar_js(show: bool):
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
                overlay.style.left = (window.innerWidth <= 480 ? '280px' : '340px');
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
