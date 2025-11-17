from flask import Flask, render_template, request, redirect, jsonify
import time
import os

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
NOTES_FILE = 'notes.txt'

def init_notes():
    if not os.path.exists(NOTES_FILE) or os.stat(NOTES_FILE).st_size == 0:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            for _ in range(3):
                f.write("::unlocked\n")

def read_notes():
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    notes = []
    for i, line in enumerate(lines):
        parts = line.strip().split("::")
        content = parts[0] if len(parts) > 0 else ""
        status = parts[1] if len(parts) > 1 else "unlocked"
        notes.append({"id": i, "content": content, "locked": status == "locked"})
    return notes

def write_notes(notes):
    # sallitaan vain 3 ensimmäistä, ettei vanhaa roskaa kerry
    notes = notes[:3]
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        for note in notes:
            content = note.get("content", "").replace("\n", " ")
            status = "locked" if note.get("locked") else "unlocked"
            f.write(f"{content}::{status}\n")


@app.route('/', methods=['GET', 'POST'])
def index():
    init_notes()
    notes = read_notes()
    return render_template('index.html', notes=notes, cache_bust=int(time.time()))

@app.route('/update/<int:note_id>', methods=['POST'])
def update_note(note_id):
    notes = read_notes()
    if not notes[note_id]["locked"]:
        notes[note_id]["content"] = request.form.get("content", "")
        write_notes(notes)
        return jsonify({"ok": True})
    return jsonify({"ok": False, "locked": True})


@app.route('/lock/<int:note_id>', methods=['POST'])
def toggle_lock(note_id):
    notes = read_notes()
    notes[note_id]["locked"] = not notes[note_id]["locked"]
    write_notes(notes)
    return jsonify({"ok": True, "locked": notes[note_id]["locked"]})


@app.route('/clear/<int:note_id>', methods=['POST'])
def clear_note(note_id):
    notes = read_notes()
    if not notes[note_id]["locked"]:
        notes[note_id]["content"] = ""
        notes[note_id]["locked"] = False
        write_notes(notes)
        return jsonify({"ok": True})
    return jsonify({"ok": False, "locked": True})


@app.route('/api/clear/<int:note_id>', methods=['POST'])
def api_clear_note(note_id):
    notes = read_notes()
    locked = notes[note_id]["locked"]
    if not locked:
        notes[note_id]["content"] = ""
        notes[note_id]["locked"] = False
        write_notes(notes)
        return jsonify({
            "ok": True,
            "id": note_id,
            "content": notes[note_id]["content"],
            "locked": notes[note_id]["locked"]
        })
    else:
        return jsonify({"ok": False, "locked": True}), 400

@app.route('/api/lock/<int:note_id>', methods=['POST'])
def api_toggle_lock(note_id):
    notes = read_notes()
    notes[note_id]["locked"] = not notes[note_id]["locked"]
    write_notes(notes)
    return jsonify({
        "ok": True,
        "id": note_id,
        "locked": notes[note_id]["locked"]
    })


@app.after_request
def add_no_cache_headers(resp):
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



@app.after_request
def add_no_cache_headers(resp):
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
