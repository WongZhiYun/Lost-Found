from flask import Flask, render_template

# Tell Flask where templates are located
app = Flask(__name__, template_folder="CheahMunXi/admin/adminhtml/templates")

@app.route("/admin")
def admin():
    return render_template("admin.html")  # looks inside your template_folder

if __name__ == "__main__":
    app.run(debug=True)
