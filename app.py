from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter

app = Flask(__name__)

# Define the folder where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the folder where processed images will be stored
PROCESSED_FOLDER = 'processed'
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Define the allowed extensions for uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process the uploaded image
def process_image(file_path, processed_path):
    # Open the image using Pillow
    image = Image.open(file_path)

    # Example image enhancement: Increase sharpness
    enhancer = ImageEnhance.Sharpness(image)
    sharpened_image = enhancer.enhance(1.5)  # Adjust the enhancement factor

    # Example image enhancement: Increase brightness
    enhancer = ImageEnhance.Brightness(sharpened_image)
    brightened_image = enhancer.enhance(1.2)  # Adjust the enhancement factor

    # Example image enhancement: Increase contrast
    enhancer = ImageEnhance.Contrast(brightened_image)
    contrasted_image = enhancer.enhance(1.2)  # Adjust the enhancement factor

    # Example image enhancement: Increase saturation
    enhancer = ImageEnhance.Color(contrasted_image)
    saturated_image = enhancer.enhance(1.2)  # Adjust the enhancement factor

    # Example image enhancement: Adjust color balance
    r, g, b = saturated_image.split()
    balanced_image = Image.merge("RGB", (r, g, b))

    # Example image enhancement: Reduce noise
    denoised_image = saturated_image.filter(ImageFilter.SMOOTH)

    # Example image enhancement: Upscale resolution
    new_width = image.width * 2  # Adjust the desired new width
    new_height = image.height * 2  # Adjust the desired new height
    upscaled_image = denoised_image.resize((new_width, new_height), Image.LANCZOS)

    # Save the processed image
    upscaled_image.save(processed_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return redirect(request.url)

    file = request.files['photo']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Securely save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Create a processed folder if it doesn't exist
        if not os.path.exists(app.config['PROCESSED_FOLDER']):
            os.makedirs(app.config['PROCESSED_FOLDER'])

        # Process the uploaded image
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        process_image(file_path, processed_path)

        # Provide links to the original and processed images
        original_url = url_for('uploaded_file', filename=filename)
        processed_url = url_for('processed_file', filename=processed_filename)

        return render_template('result.html', original_url=original_url, processed_url=processed_url)

    else:
        return 'Invalid file format. Please upload a valid image.'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
