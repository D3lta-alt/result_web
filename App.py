from flask import Flask, request, jsonify, render_template, send_from_directory, abort
import os, uuid, json, base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 31  # 31 x 5MB headroom
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
DATA_FOLDER   = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER,   exist_ok=True)

ALLOWED = {'png','jpg','jpeg','gif','webp'}
MAX_FILE_MB = 5

def allowed(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED

# ── Creator page ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Upload + save session ─────────────────────────────────────────────────────
@app.route('/create', methods=['POST'])
def create():
    files   = request.files.getlist('photos')
    message = request.form.get('message', '').strip()
    name    = request.form.get('recipient_name', '').strip()

    if not files or len(files) > 30:
        return jsonify({'error': 'Upload 1–30 photos.'}), 400

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_dir)

    saved = []
    errors = []
    for f in files:
        if not allowed(f.filename):
            errors.append(f.filename)
            continue
        f.seek(0, 2)
        size = f.tell()
        f.seek(0)
        if size > MAX_FILE_MB * 1024 * 1024:
            errors.append(f.filename)
            continue
        fname = secure_filename(f.filename)
        fpath = os.path.join(session_dir, fname)
        # avoid name collision
        base, ext = os.path.splitext(fname)
        counter = 1
        while os.path.exists(fpath):
            fname = f"{base}_{counter}{ext}"
            fpath = os.path.join(session_dir, fname)
            counter += 1
        f.save(fpath)
        saved.append(fname)

    if not saved:
        return jsonify({'error': 'No valid photos saved.', 'bad_files': errors}), 400

    meta = {'recipient': name, 'message': message, 'photos': saved}
    with open(os.path.join(DATA_FOLDER, f'{session_id}.json'), 'w') as fp:
        json.dump(meta, fp)

    link = request.host_url + f'wish/{session_id}'
    return jsonify({'link': link, 'bad_files': errors})

# ── Recipient wish page ───────────────────────────────────────────────────────
@app.route('/wish/<session_id>')
def wish(session_id):
    meta_path = os.path.join(DATA_FOLDER, f'{session_id}.json')
    if not os.path.exists(meta_path):
        abort(404)
    with open(meta_path) as fp:
        meta = json.load(fp)
    # Convert photos to base64 and shuffle server-side so count isn't exposed
    import random
    photos = list(meta['photos'])
    random.shuffle(photos)
    photos_b64 = []
    for fname in photos:
        fpath = os.path.join(UPLOAD_FOLDER, session_id, fname)
        ext = fname.rsplit('.',1)[-1].lower()
        mime = 'image/jpeg' if ext in ('jpg','jpeg') else f'image/{ext}'
        with open(fpath,'rb') as img:
            b64 = base64.b64encode(img.read()).decode()
        photos_b64.append(f'data:{mime};base64,{b64}')

    return render_template('wish.html',
        recipient=meta.get('recipient',''),
        message=meta.get('message',''),
        photos_json=json.dumps(photos_b64))

if __name__ == '__main__':
    import os
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Check if it exists locally
