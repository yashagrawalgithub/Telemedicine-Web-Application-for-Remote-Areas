from flask import render_template, request, redirect, url_for, session ,flash
from app import app, mysql, mongo
from flask import Flask, render_template, request
from pymongo import MongoClient
import base64
# import io

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        password = request.form['password']
        
        # Placeholder for authentication logic
        if password == "password":  # Replace with real password verification
            session['role'] = role
            session['logged_in'] = True
            if role == 'Junior':
                return redirect(url_for('junior_dashboard'))
            elif role == 'Senior':
                return redirect(url_for('senior_dashboard'))
        else:
            return "Invalid login, please try again."
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('role', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/junior_dashboard')
def junior_dashboard():
    if session.get('logged_in') and session.get('role') == 'Junior':
        return render_template('junior_dashboard.html')
    return redirect(url_for('login'))

@app.route('/senior_dashboard')
def senior_dashboard():
    if session.get('logged_in') and session.get('role') == 'Senior':
        return render_template('senior_dashboard.html')
    return redirect(url_for('login'))

# Route to display patient details
@app.route('/patient_detail', methods=['POST', 'GET'])
def patient_detail():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        print(patient_id)

        # Fetch patient details from MySQL
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM patient WHERE Patient_ID = %s", (patient_id,))
        patient_data = cur.fetchone()  # Assuming you're using a single patient_id query
        cur.close()

        client = MongoClient('mongodb://localhost:27017/')
        mongo_db = client['Project']  # Your MongoDB database
        mongo_patient_images = mongo_db['patients']  # The collection storing patient_id and filenames
        
        # Ensure data is correctly structured as a dictionary if needed
        # print(patient_data)
        if patient_data:
            # If `patient_data` is a tuple, convert it to a dictionary
            patient_data = {
            "Patient_ID": patient_data[0],
            "Age": patient_data[1],
            "Gender": patient_data[2],
            "Employer_Category": patient_data[3],
            "Diabetic": patient_data[4],
            "Over_Weight": patient_data[5],
            "Blood_Pressure": patient_data[6],
            "Smoker": patient_data[7],
        }
        
        # Step 1: Retrieve the document with patient metadata based on patient_id
        image_data_document = mongo_patient_images.find_one({"patient_id": int(patient_id)})
        # print(image_metadata_document)  # Print to debug and verify the document structure

        # Step 2: Check if the document and the 'img' field exist
        if image_data_document and "img" in image_data_document:
            # Convert the image data to a Base64 string for HTML rendering
            profile_pic_data = base64.b64encode(image_data_document["img"]).decode('utf-8')
        else:
            # If no image data found, set profile_pic_data to None
            profile_pic_data = None

        #prescription
        # print(profile_pic_data)
        # Get the patient_id from the URL query parameter
        patient_id = request.args.get('patient_id')

        # Fetch patient details from MongoDB by patient_id
        # patient_data = mongo_db['patients'].find_one({"patient_id": int(patient_id)})

        # Check if patient data exists
        if image_data_document:
            # Convert image data to Base64 if it exists

            # Get prescription if available, or show default message
            prescription = image_data_document.get("prescription", "No prescription available.")

            # Determine user role from session (assuming `user_role` is stored in the session on login)
            user_role = session.get('user_role', 'junior')  # default to 'junior' if not set

            return render_template(
                'patient_detail.html', 
                profile_pic=profile_pic_data, 
                data=patient_data, 
                prescription=prescription, 
                user_role=user_role
            )
        else:
            flash("Patient not found.")
            # return redirect(url_for('dashboard'))

            # Return the patient details and image data (if available)
    # return render_template('patient_detail.html', profile_pic=profile_pic_data, data=patient_data, prescription=prescription)
    return redirect(url_for('login'))

# Route for senior user to add/update prescription
@app.route('/update_prescription', methods=['GET','POST'])
def update_prescription():

    client = MongoClient('mongodb://localhost:27017/')
    mongo_db = client['Project']  # Your MongoDB database
    mongo_patient_images = mongo_db['patients']  # The collection storing patient_id and filenames
        
    # Check if the user is a senior
    if session.get('user_role') != 'senior':
        flash("Only senior users can update prescriptions.")
        return redirect(url_for('patient_detail', patient_id=request.form.get('patient_id')))

    # Get patient_id and prescription text from the form
    patient_id = request.form.get('patient_id')
    prescription_text = request.form.get('prescription')

    # Update the patient's document with the new prescription
    result = mongo_db['patients'].update_one(
        {"patient_id": int(patient_id)},
        {"$set": {"prescription": prescription_text}}
    )

    if result.matched_count > 0:
        flash("Prescription updated successfully.")
    else:
        flash("Failed to update prescription. Patient not found.")

    return redirect(url_for('patient_detail', patient_id=patient_id))

# @app.route('/upload_file', methods=['POST'])
# def upload_file():
#     if 'logged_in' in session and session['role'] == 'Junior':
#         if 'file' not in request.files:
#             return 'No file part'
        
#         file = request.files['file']
#         if file.filename == '':
#             return 'No selected file'
        
#         mongo.db.uploaded_files.insert_one({
#             'file': file.read(),
#             'filename': file.filename,
#             'content_type': file.content_type
#         })
        
#         return 'File uploaded successfully'
#     return redirect(url_for('login'))
