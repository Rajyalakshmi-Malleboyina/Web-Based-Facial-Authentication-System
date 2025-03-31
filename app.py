from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import face_recognition
import json

app = Flask(__name__)

# Set the directory to store uploaded files
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Function to check if the file is an allowed image type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Root route to redirect to registration page
@app.route('/')
def index():
    return redirect(url_for('register'))  # Redirect to the register page

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Process the image (e.g., encoding face data)
            uploaded_image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(uploaded_image)

            if len(face_encoding) > 0:
                # Store the encoding in a file or a database (for simplicity, we use a dictionary here)
                user_data = {'name': name, 'encoding': face_encoding[0].tolist()}
                with open(f'{UPLOAD_FOLDER}/{name}_data.json', 'w') as json_file:
                    json.dump(user_data, json_file)

                return redirect(url_for('login'))  # After successful registration, redirect to login page
            else:
                return render_template('register.html', message='No face detected in the image')

        return render_template('register.html', message='Invalid image file')

    return render_template('register.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Load the user's saved data
            try:
                with open(f'{UPLOAD_FOLDER}/{name}_data.json', 'r') as json_file:
                    user_data = json.load(json_file)

                # Process the uploaded image
                uploaded_image = face_recognition.load_image_file(image_path)
                uploaded_face_encoding = face_recognition.face_encodings(uploaded_image)

                if len(uploaded_face_encoding) > 0:
                    # Compare the uploaded face encoding with the saved one
                    match = face_recognition.compare_faces([user_data['encoding']], uploaded_face_encoding[0])

                    if match[0]:
                        return redirect(url_for('home', name=name))  # Redirect to home page after successful login
                    else:
                        return render_template('login.html', message='Face does not match')
                return render_template('login.html', message='No face detected in the image')
            except FileNotFoundError:
                return render_template('login.html', message='You are not a registered user')

        return render_template('login.html', message='Invalid image file')

    return render_template('login.html')

# Route for the home page
@app.route('/home/<name>')
def home(name):
    return render_template('home.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
