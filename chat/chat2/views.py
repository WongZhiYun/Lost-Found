from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Message
from . import db

views = Blueprint('views', __name__)

@views.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            new_message = Message(sender_id=current_user.id, receiver_id=other_user.id, text=text)
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('views.chat', user_id=user_id))

    # Fetch conversation between current user and other_user
    messages = Message.query.filter(
        ((Message.sender_id==current_user.id) & (Message.receiver_id==other_user.id)) |
        ((Message.sender_id==other_user.id) & (Message.receiver_id==current_user.id))
    ).order_by(Message.timestamp).all()

    return render_template("chat.html", other_user=other_user, messages=messages)
