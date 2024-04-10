from flask import Flask, request, render_template, send_from_directory , redirect , url_for
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random string
socketio = SocketIO(app)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Dictionary to store active users and their corresponding client connections
active_users = {}

@app.route('/')
def index():
    return render_template('error.html')

@app.route('/instruction')
def instruction():
    return render_template('instruction.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        # Handle the POST request here
        username = request.form.get('username')
        # Do something with the username here, like storing it in the session
        return render_template('chat.html', username=username)
    else:
        # Handle the GET request here
        return render_template('chat.html')

@app.route('/set-username', methods=['GET', 'POST'])
def set_username():
    if request.method == 'POST':
        username = request.form['username']
        if username:
            return redirect(url_for('chat'))
        else:
            return render_template('error.html', message="Username not provided")
    else:
        return render_template('set-username.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return 'File uploaded successfully'
    return render_template('index.html')

@app.route('/files')
def list_files():
    files = os.listdir(app.config['DOWNLOAD_FOLDER'])
    return render_template('files.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@socketio.on('connect')
def handle_connect():
    username = request.args.get('username')
    if username:
        active_users[username] = request.sid
        print(f"{username} connected")

@socketio.on('disconnect')
def handle_disconnect():
    username = get_user_from_sid(request.sid)
    if username:
        del active_users[username]
        print(f"{username} disconnected")

@socketio.on('message')
def handle_message(data):
    sender = data['sender']
    message = data['message']
    for username, sid in active_users.items():
        if username != sender:  # Avoid sending the message back to the sender
            socketio.emit('message', {'sender': sender, 'message': message}, room=sid)

def get_user_from_sid(sid):
    for username, user_sid in active_users.items():
        if user_sid == sid:
            return username
    return None

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
