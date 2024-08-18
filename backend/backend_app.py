from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__, static_url_path='/custom_static', static_folder='../frontend/static')
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/custom_static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction', 'asc')
    sorted_posts = POSTS[:]
    if sort in ['title', 'content']:
        reverse = direction == 'desc'
        sorted_posts = sorted(sorted_posts, key=lambda x: x[sort].lower(), reverse=reverse)
    return jsonify(sorted_posts)

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    if 'title' not in data or 'content' not in data:
        missing_fields = []
        if 'title' not in data:
            missing_fields.append('title')
        if 'content' not in data:
            missing_fields.append('content')
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1
    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    for post in POSTS:
        if post['id'] == post_id:
            POSTS.remove(post)
            return jsonify({"message": f"Post id {post_id} has been deleted successfully."}), 200
    return jsonify({"error": f"Post id {post_id} does not exist."}), 404

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    updated_post = None
    for post in POSTS:
        if post['id'] == post_id:
            post['title'] = data.get('title', post['title'])
            post['content'] = data.get('content', post['content'])
            updated_post = post
            break
    if updated_post:
        return jsonify(updated_post), 200
    else:
        return jsonify({"Some Error": f"post id {post_id}does not exist"}), 404

@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title = request.args.get('title')
    content = request.args.get('content')
    searched_items = []
    for post in POSTS:
        if (title and title.lower() in post['title'].lower()) or (content and content.lower() in post['content'].lower()):
            searched_items.append(post)
    return jsonify(searched_items), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)