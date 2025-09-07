from flask import Blueprint, request, render_template


# create blueprint
bp = Blueprint('search', __name__, template_folder='../templates')

@bp.route('/', methods=['GET'])
def index():
    q = (request.args.get('q') or '').strip()
    category = (request.args.get('category') or '').strip()

    results = []
    categories = []
    
    return render_template(
        'search/results.html',
        results=results,
        categories=categories,
        q=q,
        category=category
    )
