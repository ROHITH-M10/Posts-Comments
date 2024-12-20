from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS  # Import CORS for handling cross-origin requests

app = Flask(__name__)
CORS(app)  # Allow all origins by default, you can customize it if needed

# Database initialization (creates the necessary tables)
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            author TEXT,
            style TEXT,
            post_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    ''')
    conn.commit()
    conn.close()

# Route to get all posts and their comments
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts order by created_at desc')
    posts = cursor.fetchall() # [(1,"Title1","Content1","Author1","2021-09-01 12:00:00"), ...]
    result = []
    for post in posts:
        post_id = post[0]
        cursor.execute('SELECT * FROM comments WHERE post_id = ? order by created_at desc', (post_id,))
        comments = cursor.fetchall()
        
        comment_list = [{'id': comment[0], 'content': comment[1], 'author': comment[2],'style': comment[3] , 'timestamp': comment[5]} for comment in comments]

        result.append({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'author': post[3],
            'timestamp': post[4],
            'comments': comment_list
        })
    
    conn.close()
    return jsonify(result)

# Route to create a new post
@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data['title']
    content = data['content']
    author = data.get('author', 'Anonymous') 

    print(f"Received data: {title}, {content}, {author}")  # Debugging line

    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content, author) VALUES (?, ?, ?)', (title, content, author))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Post created successfully'}), 201
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'message': 'Database error'}), 500

# Route to add a comment to a post
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    content = data['content']
    author = data.get('author', 'Anonymous')
    style = data.get('style', 'text')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (content, author, style, post_id) VALUES (?, ?, ?, ?)', (content, author, style, post_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Comment added successfully'}), 201

if __name__ == '__main__':
    init_db()  # Initialize the database with tables
    app.run(debug=True)
