from flask import Flask, render_template , request , jsonify
from flask_cors import CORS
from PIL import Image
import random
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static") 

app=Flask(__name__,template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

#load doodles/affirmations
with open("data.json","r",encoding="utf-8") as f:
    mood_data= json.load(f)


@app.route('/')
def index():
    return render_template("basic.html")

ASCII_CHARS=["@","#","S","%","?","*","+",";",":",",","."]
def resize_image(image, new_width=80):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)
    # cap max height/width to save memory
    if new_height > 600:
        new_height = 600
    if new_width > 800:
        new_width = 800
    return image.resize((new_width, new_height))
      

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return ascii_str

def image_to_ascii(image_path):
    try:
        image = Image.open(image_path)
    except:
        return "Unable to open image."
    
    image = resize_image(image)
    image = grayify(image)

    ascii_str = pixels_to_ascii(image)
    width = image.width
    ascii_img = "\n".join(
        [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
    )
    return ascii_img

from werkzeug.utils import secure_filename
from PIL import UnidentifiedImageError
# add ALLOWED_EXT at top of file
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT




@app.route('/convert', methods=['POST'])
def convert():
    try:
        file = request.files.get('image')
        user_mood = request.form.get('mood', '').lower()

        if (not file or file.filename == '') and user_mood:
            if user_mood in mood_data:
                mood = user_mood
            else:
                mood = random.choice(list(mood_data.keys()))

            entry = random.choice(mood_data[mood])
            
            return jsonify({
                "ascii_art": entry.get("ascii", random.choice(["(｡◕‿◕｡)", "(❁´◡`❁)", "ʕ•ᴥ•ʔ", "(づ｡◕‿‿◕｡)づ"])),
                "mood": mood,
                "doodle": entry.get("ascii", ""),
                "affirmation": entry["affirmation"]
            }), 200
        
        if not file or file.filename == '':
            return jsonify({"error": "No file uploaded or mood provided"}), 400


        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return jsonify({"error": "Unsupported file type"}), 400

        os.makedirs("uploads", exist_ok=True)
        filepath = os.path.join("uploads", filename)
        file.save(filepath)

        # convert image to ascii (wrap in try/except to catch PIL errors)
        try:
            ascii_art = image_to_ascii(filepath)
            del ascii_art
            import gc
            gc.collect()

        except UnidentifiedImageError:
            return jsonify({"error": "Pillow cannot identify this image (corrupt/unsupported). Try a different file."}), 400
        except Exception as e:
            # print full traceback to terminal for debugging
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Image processing error: {e}"}), 500

        # pick a mood/doodle if you want to return it
        # Determine mood (user input or random)
        user_mood = request.form.get("mood", "").lower()
        if user_mood in mood_data:
            mood = user_mood
        else:
            mood = random.choice(list(mood_data.keys()))

        # Now safely pick the entry for that mood
        entry = random.choice(mood_data[mood])



        return jsonify({
            "ascii_art": ascii_art,
            "mood": mood,
            "doodle": entry.get("ascii", random.choice(["(｡◕‿◕｡)", "(❁´◡`❁)", "ʕ•ᴥ•ʔ", "(⁄⁄>⁄ ▽ ⁄<⁄⁄)", "(づ｡◕‿‿◕｡)づ"])),
            "affirmation": entry["affirmation"]
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()   # full stack trace to terminal
        return jsonify({"error": f"Server error: {e}"}), 500
 
@app.route('/mood', methods=['POST'])
def mood_entry():
    user_mood = request.form.get('mood', '').lower().strip()

    if user_mood and user_mood in mood_data:
        mood = user_mood
        entry = random.choice(mood_data[mood])
        return jsonify({
            "mood": mood,
            "doodle": entry.get("ascii", ""),
            "affirmation": entry.get("affirmation", "")
        }), 200

    # invalid or empty mood → return empty JSON
    return jsonify({}), 200
    
@app.route('/check-static-images')
def check_static_images():
    images_folder = os.path.join(app.static_folder, 'images')
    if not os.path.exists(images_folder):
        return "Folder not found: " + images_folder

    files = os.listdir(images_folder)
    files_list = "<br>".join(files)
    return f"Files in static/images/:<br>{files_list}"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=False)
