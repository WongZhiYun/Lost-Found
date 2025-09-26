"""
Chat area component - UI Layer
This file is responsible for creating and managing the visual components of the chat area.
It holds UI state (like pending image uploads) but does not perform business logic like saving files or database operations.
"""
from nicegui import ui
from ..core.utils import safe_str
import uuid
from pathlib import Path
import base64
from typing import List, Dict, Callable

# UI-level state for images waiting to be sent
# Keeps track of images that the user has uploaded but not yet sent.
uploaded_images: List[Dict] = []

# --- Component Builders ---

def create_chat_area() -> ui.element:
    """Creates the main container for the chat interface."""
    return ui.element('div').classes('custom-chat')

def create_chat_header(partner, on_menu_click: Callable) -> None:
    """Creates the header bar for the chat."""
    with ui.element('div').classes('custom-chat-header'):
                # Mobile sidebar menu button
        ui.icon('menu').classes('mobile-menu-btn').on('click', on_menu_click)

        profile_url = partner.profile_image or "default.png"

        # Display user profile image
        ui.image(f"/static/profile_pics/{profile_url}").classes('w-10 h-10 rounded-full')        
        
        with ui.element('div').classes('ml-3'):
                    # Username label
            ui.label(safe_str(partner.username)).classes('text-lg font-medium text-gray-900')
        ui.space()

def create_messages_container() -> ui.element:
    """Creates the container where message bubbles will be rendered."""
    return ui.element('div').classes('custom-messages')

def create_input_area(on_send: Callable) -> ui.input:
    """
    Creates the message input field, attachment button, and send button.
    The `on_send` callback will be invoked with the message text and a list of pending image data.
    """
    # Container to show preview thumbnails of images before sending
    preview_container = ui.element('div').classes('p-2 hidden')

    # Hidden uploader for selecting images
    uploader = ui.upload(
        on_upload=lambda e: handle_image_upload(e, preview_container),
        on_rejected=lambda: ui.notify('File rejected!', color='negative'),     # Called when file validation fails (size/type issues, etc.)
        max_file_size=5_000_000,
        auto_upload=True,     # Automatically upload as soon as user selects a file (no extra "upload" button needed)
        multiple=True     # Allow selecting multiple files at once
    ).classes('hidden')

    with ui.element('div').classes('custom-input-area'):
        ui.query('.q-btn--fab').classes('!p-2 !min-w-12 !min-h-12')

        with ui.fab('add', direction='up'):      # Main FAB button (a round '+' button that expands upwards)
            # Sub-action: "Picture" button inside the FAB menu
            ui.fab_action('image', label='Picture').classes('!mb-3 !ml-10').on('click', lambda: uploader.run_method('pickFiles'))
        
        # Message text field
        message_input = ui.input(placeholder='Type a message').props('borderless').classes('flex-1 rounded-full')
        
         # Internal handler for sending text + images
        def enhanced_send_handler():
            text_value = message_input.value
            images_to_send = list(uploaded_images)  # Create a copy

            # If nothing is typed and no images, skip
            if not text_value.strip() and not images_to_send:
                return

            if on_send:
                # Pass the raw data to the handler. The handler is responsible for saving.
                on_send(message_input, images_to_send)
                
            # Clear the UI state after passing the data
            clear_all_previews_after_send(preview_container)
        
        # Send button + Enter key support
        ui.button(icon='send', on_click=enhanced_send_handler).classes('p-6 custom-btn')
        message_input.on('keydown.enter', enhanced_send_handler)
        
        return message_input

def create_message_bubble(msg, current_user_id: int, open_viewer_func: Callable) -> None:
    """Creates a single message bubble with text and/or an image grid."""
    is_sent = msg.sender_id == current_user_id    # Check if the message is sent by the current user
    time_str = msg.created_at.strftime('%H:%M')   # Format timestamp as HH:MM (e.g., 14:25)
    message_class = 'custom-message sent' if is_sent else 'custom-message received'
    
    with ui.element('div').classes(message_class):
        with ui.element('div').classes('p-1'):

            if msg.content:   # If the message has text content, render it
                with ui.element('div').classes('px-2 py-1'):
                    ui.html(f'<div>{safe_str(msg.content)}</div>')
            
             # If the message has media (images, files, etc.), create a grid layout
            if msg.media_items:
                _create_image_grid(msg.media_items, open_viewer_func)
                
            # Timestamp below the message bubble
            with ui.element('div').classes('px-2'):
                ui.label(time_str).classes('text-right mt-1 text-gray-500 text-xs')

# --- UI Helper Functions (Internal to this component) ---

def _create_image_grid(media_items: List, open_viewer_func: Callable) -> None:
    """Helper to create the image grid within a message bubble."""
    total_images = len(media_items)
    images_to_display = media_items[:4] # Only display max 4, rest shown as +N
    
    # Base classes: 2x2 grid, small gaps, rounded edges
    grid_classes = 'grid grid-cols-2 gap-0.5 rounded-lg overflow-hidden mt-1 w-64'

    # If only one image: display bigger
    if total_images == 1:
        grid_classes = 'mt-1 w-64 rounded-lg overflow-hidden'

    with ui.element('div').classes(grid_classes):
        # Single image view
        if total_images == 1:
            item = images_to_display[0]
            with ui.element('div').classes('relative cursor-pointer'):
                # Display full-size image
                ui.image(f"/static/uploads/{item.file_url}").classes('w-full h-full object-cover aspect-[4/3]')
                # Transparent clickable overlay that opens viewer
                ui.element('div').classes('absolute inset-0').on('click', lambda: open_viewer_func(media_items, 0))
        else:
            # Multiple image thumbnails
            for i, item in enumerate(images_to_display):
                with ui.element('div').classes('relative aspect-square cursor-pointer'):

                    # Display thumbnail
                    ui.image(f"/static/uploads/{item.file_url}").classes('w-full h-full object-cover')
                    # If there are more than 4 images, show "+N" overlay on last
                    if i == 3 and total_images > 4:
                        with ui.element('div').classes('absolute inset-0 bg-black/60 flex items-center justify-center'):
                            ui.label(f'+{total_images - 4}').classes('text-white text-2xl font-bold')
                    # Click opens image viewer
                    ui.element('div').classes('absolute inset-0').on(
                        'click', lambda _, items=media_items, idx=i: open_viewer_func(items, idx))

def handle_image_upload(e, preview_container: ui.element) -> None:
    """Handles a new file upload by adding it to the temporary UI state."""
    global uploaded_images
    try:
        file_content = e.content.read() # Read file bytes
        file_extension = Path(e.name).suffix.lower()  # Get extension (.jpg, .png, etc.)
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:  # Validate file type
            ui.notify('Invalid image file type', color='negative')
            return
            
        # Build metadata for uploaded file    
        image_info = {
            'uuid_name': f"{uuid.uuid4()}{file_extension}", # Unique filename
            'content': file_content, # Raw bytes
            'extension': file_extension # File extension
        }
        uploaded_images.append(image_info) # Store in global list (temp state until message sent)
        refresh_image_previews(preview_container)
    except Exception as ex:
        # Show error to user
        ui.notify(f'Failed to process image: {str(ex)}', color='negative')

def refresh_image_previews(preview_container: ui.element) -> None:
    """Re-renders the image preview grid based on the current UI state."""

    if not uploaded_images: # If no images, hide preview area
        preview_container.classes('hidden', remove='p-2')
        preview_container.clear()
        return
    else:
        # Show container if images exist
        preview_container.classes('p-2', remove='hidden')
    # Clear old previews
    preview_container.clear()
    with preview_container:
        with ui.element('div').classes('flex flex-wrap gap-2'):
            for image in uploaded_images: # Container for preview
                with ui.element('div').classes('relative w-20 h-20 rounded-lg overflow-hidden'):
                    # Convert raw bytes → Base64 data URL (so we can preview without saving)
                    mime_type = f"image/{image['extension'][1:]}"
                    base64_data = base64.b64encode(image['content']).decode('utf-8')
                    ui.image(f"data:{mime_type};base64,{base64_data}").classes('w-full h-full object-cover')
                    # Close button overlay to remove preview
                    ui.button(
                        icon='close', 
                        on_click=lambda _, uuid=image['uuid_name']: remove_image_preview(preview_container, uuid)
                    ).props('round dense flat').classes('!absolute top-1 right-1 bg-black/50 text-white !p-0 !min-w-6 !min-h-6')

def remove_image_preview(preview_container: ui.element, image_uuid_to_remove: str) -> None:
    """Removes an image from the temporary UI state and refreshes the preview."""
    global uploaded_images

    # Filter out the image with the matching UUID
    uploaded_images = [img for img in uploaded_images if img['uuid_name'] != image_uuid_to_remove]
    # Re-render the preview area after removal
    refresh_image_previews(preview_container)
    
def clear_all_previews_after_send(preview_container: ui.element) -> None:
    """Clears the pending images list and hides the preview container."""
    global uploaded_images
    # Remove all uploaded images from temporary state
    uploaded_images.clear()
    # Clear preview container UI
    preview_container.clear()
    # Hide the container (remove padding, add hidden class)
    preview_container.classes('hidden', remove='p-2')