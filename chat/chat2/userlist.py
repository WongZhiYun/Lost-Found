@views.route('/users')
@login_required
def users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template("users.html", users=users)
