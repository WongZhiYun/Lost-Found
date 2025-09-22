"""
Chat page component
"""
from nicegui import ui


"""Redirect to chat page with chat parameter"""
def direct_chat_page(partner_id: int):
    # Redirect to main page with chat parameter
    ui.navigate.to(f'/?chat_with={partner_id}')
