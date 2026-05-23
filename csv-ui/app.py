import os
import uuid
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
# Secure session key for tracking file state
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-1234")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def step1_upload():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".csv"):
            # Use unique names to prevent users overriding each other's files
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            
            # Save filename in session and move to column selection
            session['filename'] = unique_filename
            return redirect(url_for('step2_select_columns'))
            
    return render_template("templates.html", step=1)

@app.route("/select-columns", methods=["GET", "POST"])
def step2_select_columns():
    filename = session.get('filename')
    if not filename:
        return redirect(url_for('step1_upload'))
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Read only the first row to extract column names quickly
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
    except Exception:
        return "Invalid or corrupted CSV file.", 400

    if request.method == "POST":
        selected_columns = request.form.getlist('columns')
        if not selected_columns:
            return render_template("templates.html", step=2, columns=columns, error="Please select at least one column.")
        
        # Save chosen columns to session and move to display step
        session['selected_columns'] = selected_columns
        return redirect(url_for('step3_display_and_download'))

    return render_template("templates.html", step=2, columns=columns)

@app.route("/display", methods=["GET"])
def step3_display_and_download():
    filename = session.get('filename')
    selected_columns = session.get('selected_columns')
    
    if not filename or not selected_columns:
        return redirect(url_for('step1_upload'))
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Read file with only selected columns, limiting preview to 10 rows
        df = pd.read_csv(file_path, usecols=selected_columns)
        preview_html = df.head(10).to_html(classes="table", index=False)
    except Exception as e:
        return f"Error filtering file: {str(e)}", 400

    return render_template("templates.html", step=3, preview_table=preview_html)

@app.route("/download", methods=["GET"])
def download_custom_csv():
    filename = session.get('filename')
    selected_columns = session.get('selected_columns')
    
    if not filename or not selected_columns:
        return redirect(url_for('step1_upload'))
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    custom_filename = f"custom_{filename.split('_', 1)[-1]}"
    custom_file_path = os.path.join(app.config['UPLOAD_FOLDER'], custom_filename)
    
    try:
        # Generate the filtered CSV for download
        df = pd.read_csv(file_path, usecols=selected_columns)
        df.to_csv(custom_file_path, index=False)
        return send_from_directory(app.config['UPLOAD_FOLDER'], custom_filename, as_attachment=True)
    except Exception as e:
        return f"Download failed: {str(e)}", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

