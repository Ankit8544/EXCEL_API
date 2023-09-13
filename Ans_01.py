import os
import pandas as pd
from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('Indexs.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Check if the post request has the file part
    if 'file1' not in request.files or 'file2' not in request.files:
        return 'No file parts'

    file1 = request.files['file1']
    file2 = request.files['file2']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file1.filename == '' or file2.filename == '':
        return 'No selected file'

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        # Save the uploaded files
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

        # First File selection
        df1 = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        Column_name_of_frist_dataset = df1.columns.to_list()
        # Select Column from First Dataset# Get the selected column name from the form
        First_Column_Selection = request.form['selected_column']
        List_of_Column_from_Frist_Dataset = df1[First_Column_Selection].to_list()

        # Second File Selection
        df2 = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        Column_name_of_second_dataset = df2.columns.to_list()
        # Select Column From Second Data Set
        Second_Column_Selection = request.form["second-col"]
        List_of_Column_from_Second_Dataset = df2[Second_Column_Selection].to_list()

        Auto_Approval = []
        for i in List_of_Column_from_Frist_Dataset:
            # Check if the number is in the list
            if i in List_of_Column_from_Second_Dataset:
                Result = "Yes"
                Auto_Approval.append(Result)
            else:
                Result = None
                Auto_Approval.append(Result)

        df1['Auto Approval'] = Auto_Approval

        df3 = df1.dropna()

        URL = []
        for l in (df3['Group ID']):
            link = 'https://www.facebook.com/groups/'+str(l)+'/?ref=share&mibextid=ukryub'  # Use the create_link function here
            URL.append(link)

        df3['Group URL'] = URL

        Auto_Approved_Group = df3

        # Prompt user for the Excel file name and add '.xlsx' extension automatically
        user_filename = request.form.get('excel_filename')
        if not user_filename:
            user_filename = 'Auto_Approved_Group.xlsx'  # Default name if user doesn't provide one
        elif not user_filename.endswith('.xlsx'):
            user_filename += '.xlsx'  # Add '.xlsx' extension if missing

        excel_file_path = os.path.join(app.config['UPLOAD_FOLDER'], user_filename)
        Auto_Approved_Group.to_excel(excel_file_path, index=False)

        # Provide a download link for the generated Excel file
        return redirect(url_for('download_file', filename=excel_file_path))

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run()  # Run the app in debug mode for easier debugging
