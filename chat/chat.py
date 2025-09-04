import sqlite3
from nicegui import ui

# --- Load users from database ---
def load_users(db_path='users.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users_list = cursor.fetchall()  # [('zhiyun0506',), ('munxi',)]
    conn.close()
    # convert to dict: username -> avatar
    return {u[0]: f'https://robohash.org/{u[0]}?bgset=bg2' for u in users_list}

users = load_users()

# --- Store messages per chat (chat_id -> messages list) ---
chats = {}

# --- Helper to generate unique chat id per user pair ---
def get_chat_id(user1, user2):
    return '_'.join(sorted([user1, user2]))

# --- Chat page for two users ---
def chat_page(user1, user2):
    chat_id = get_chat_id(user1, user2)
    if chat_id not in chats:
        chats[chat_id] = []

    @ui.refreshable
    def chat_messages():
        for sender, avatar, text in chats[chat_id]:
            ui.chat_message(avatar=avatar, text=text, sent=sender==user1)

    input_text = ui.input(placeholder='Type a message').props('rounded outlined').classes('flex-grow')

    def send():
        if input_text.value.strip():
            chats[chat_id].append((user1, users[user1], input_text.value))
            chat_messages.refresh()
            input_text.value = ''

    with ui.column().classes('w-full items-stretch'):
        chat_messages()

    with ui.footer().classes('bg-white'):
        with ui.row().classes('w-full items-center'):
            with ui.avatar():
                ui.image(users[user1])
            input_text.on('keydown.enter', send)
            ui.button('Send', on_click=send)

# --- User profile page with chat buttons ---
@ui.page('/')
def index():
    ui.label('Users:')
    for username, avatar in users.items():
        with ui.row().classes('items-center gap-4'):
            ui.image(avatar).classes('w-12 h-12 rounded-full')
            ui.label(username)
            # Open chat page with this user
            ui.button('Chat', on_click=lambda u=username: ui.open(f'/chat/{u}'))

# --- Chat route ---
@ui.page('/chat/<username>')
def chat(username: str):
    current_user = 'zhiyun0506'  # example logged-in user
    if current_user not in users:
        users[current_user] = f'https://robohash.org/{current_user}?bgset=bg2'
    chat_page(current_user, username)

ui.run(host='0.0.0.0', port=8080)

