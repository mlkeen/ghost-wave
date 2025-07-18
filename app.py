import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from pydub import AudioSegment

# Base directory of this script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Absolute paths to folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MERGED_FOLDER = os.path.join(BASE_DIR, 'merged')
CLIPS_FOLDER = os.path.join(BASE_DIR, 'static', 'audio')

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)
os.makedirs(CLIPS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MERGED_FOLDER'] = MERGED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Audience interface
@app.route('/')
def audience():
    return render_template('audience.html')

# Magician interface
@app.route('/magician')
def magician():
    clips = os.listdir(CLIPS_FOLDER)
    return render_template('magician.html', clips=clips)

# Upload audience recording
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('audio')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return {'status': 'ok', 'filename': filename}
    return {'status': 'error'}, 400

# Insert prerecorded audio clip by layering it over the audience audio
@app.route('/insert', methods=['POST'])
def insert():
    filename = request.form.get('filename')
    clipname = request.form.get('clip')

    original_path = os.path.join(UPLOAD_FOLDER, filename)
    clip_path = os.path.join(CLIPS_FOLDER, clipname)

    if not os.path.exists(original_path) or not os.path.exists(clip_path):
        return {'status': 'error'}, 404

    base = AudioSegment.from_file(original_path)
    clip = AudioSegment.from_file(clip_path)

    # Ensure both clips are the same sample rate and channel count
    if clip.frame_rate != base.frame_rate:
        clip = clip.set_frame_rate(base.frame_rate)
    if clip.channels != base.channels:
        clip = clip.set_channels(base.channels)

    # Overlay clip at 2 seconds into the base audio
    insert_time_ms = 2000
    merged = base.overlay(clip, position=insert_time_ms)

    merged_filename = f'merged_{filename}'
    merged_path = os.path.join(MERGED_FOLDER, merged_filename)
    merged.export(merged_path, format="wav")

    return {'status': 'ok', 'merged': merged_filename}

# Serve merged audio for playback
@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory(app.config['MERGED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
