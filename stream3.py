import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime

st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1454117096348-e4abbeba002c?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8d2Vic2l0ZSUyMGJhY2tncm91bmR8ZW58MHx8MHx8fDA%3D');
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)
known_face_enc = []
known_face_names = []
students = []
face_names = []
# Function to load all images from a folder


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        img = face_recognition.load_image_file(img_path)
        face_locations = face_recognition.face_locations(img)
        print(f"Number of faces detected in {filename}: {len(face_locations)}")
        images.append(img)
    return images


# Define folders for each person
person1_folder = "C:\\Users\\User\\Desktop\\Ccoder\\opencv\\Deepika"
person2_folder = "C:\\Users\\User\\Desktop\\Ccoder\\opencv\\Virat"
person3_folder = "C:\\Users\\User\\Desktop\\Ccoder\\opencv\\Einstein"
person4_folder = "C:\\Users\\User\\Desktop\\Ccoder\\opencv\\Parth"
# Function to perform face recognition


def recognize_faces(video_frame, known_face_enc, students, student_present, lnwriter):
    x = cv2.resize(video_frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = x[:, :, ::-1]
    face_loc = face_recognition.face_locations(rgb_small)
    face_enc = face_recognition.face_encodings(rgb_small, face_loc)
    face_names = []

    for (top, right, bottom, left), enc in zip(face_loc, face_enc):
        match = face_recognition.compare_faces(known_face_enc, enc)
        name = ""
        face_dis = face_recognition.face_distance(known_face_enc, enc)
        best_match = np.argmin(face_dis)

        if match[best_match]:
            name = known_face_names[best_match]
            if not student_present[name]:
                st.markdown(f"**{name}**: Present")
                students.remove(name)
                student_present[name] = True
                current_time = datetime.now().strftime("%H:%M:%S")
                lnwriter.writerow([name, current_time])
                # Remove the name from the students list
                students.remove(name)

        # Draw a rectangle around the detected face
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(video_frame, (left, top),
                      (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(video_frame, name, (left + 6, bottom - 6),
                    font, 0.5, (255, 255, 255), 1)

        face_names.append(name)

    return video_frame


# Initialize session state
if 'i' not in st.session_state:
    st.session_state.i = 0


def load_student_names():
    try:
        df = pd.read_csv("")
        return df["Name"].tolist()
    except FileNotFoundError:
        return []


now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
nav = st.sidebar.radio("Navigation", ["Home", "Login", "Add New Student",
                                      "Record Attendance", "View Attendance"])

if nav == "Home":
    st.title("Attendance System")
    st.subheader("Welcome Dear User")
    st.text(" This web Application has been designed to record,\n view and automate attendance using face recognition\n hence making it a seamless and comparatively,\n a faster way to record attendance.")
    st.write("On the left side, you have been provided a navigation panel which enables you to sign into your account, record and view attendance or add a new student")

if nav == "Login":
    st.title("Login")

    if st.session_state.i == 1:
        st.text("Welcome Parth Hemdan :)")
        if st.button("Logout"):
            st.session_state.i = 0  # Set i to 0 for logout
            st.session_state.clear()
    else:
        st.write("Enter the credentials")
        first, last = st.columns(2)

        first = first.text_input("First Name")
        last = last.text_input("Last Name")

        email, pwd = st.columns(2)
        email = email.text_input("Email Address")
        pwd = pwd.text_input("Password", type="password")

        ch, bl, sub = st.columns(3)
        ch = ch.checkbox("I'm not a robot")
        sub = sub.button("Submit")
        if sub:
            # Check login credentials
            if (
                first == "Parth"
                and last == "Hemdan"
                and email == "parthhemdan@gmail.com"
                and pwd == "abcd"
                and ch
            ):
                st.text("Welcome Parth Hemdan :)")
                st.session_state.i = 1  # Set i to 1 for a successful login
            else:
                st.text("Invalid credentials. Please try again.")

if nav == "Add New Student":
    if st.session_state.i == 0:
        st.title("Cannot Access")
        st.text("Please log into your account to perform this action")
    else:
        st.title("Add Student")
        st.text("Enter details of student")

        f1, l1 = st.columns(2)
        first_name = f1.text_input("First Name")
        last_name = l1.text_input("Last Name")

        roll, stud_id = st.columns(2)
        roll_number = roll.number_input("Roll Number", step=1)
        student_id = stud_id.text_input("Student ID")

        # Create a folder for each student using only the first name
        student_folder_path = os.path.join(
            'C:\\Users\\User\\Desktop\\Ccoder\\opencv', f"{first_name}")

        if not os.path.exists(student_folder_path):
            os.makedirs(student_folder_path)

        # a dropdown menu lets the user choose if a new student's image is to be uploaded by uploading or webcam
        select, bl2, img = st.columns(3)
        select = st.selectbox(
            "Select choice", ["Choose from:", "Capture with webcam", "Image Upload"])
        if (select == "Image Upload"):
            uploaded_file = st.file_uploader(
                "Choose an image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                # Save the uploaded image to the student's folder
                image_path = os.path.join(
                    student_folder_path, f"{first_name}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(uploaded_file.read())

            # Load the newly added student's image
                new_student_images = load_images_from_folder(
                    student_folder_path)

            # Add the new student's images to the list of known face encodings
                known_face_enc.extend(face_recognition.face_encodings(img)[
                                      0] for img in new_student_images)

            # Add the new student's name to the list of known face names
                known_face_names.extend(
                    [f"{first_name} {last_name}"] * len(new_student_images))

            # Print debugging information
                st.write(f"New Student Images: {new_student_images}")
                st.write(f"Known Face Encodings: {known_face_enc}")
                st.write(f"Known Face Names: {known_face_names}")

                st.image(image_path, caption="Uploaded Image",
                         use_column_width=True)

        if (select == "Capture with webcam"):
            class ImageCaptureProcessor(VideoProcessorBase):
                def __init__(self) -> None:
                    self.image = None

                def recv(self, frame):
                    if frame:
                        self.image = frame.to_ndarray(format="rgb24")
                        return self.image

                def on_button_click(self, button):
                    if button == self.button:
                        # Save the captured image to the student's folder
                        image_path = os.path.join(
                            student_folder_path, f"{first_name}_{last_name}_{roll_number}.jpg")
                        cv2.imwrite(image_path, cv2.cvtColor(
                            self.image, cv2.COLOR_RGB2BGR))

                        # Load the newly added student's image
                        new_student_image = face_recognition.load_image_file(
                            image_path)

                        # Extract face encoding for the new student
                        new_student_encoding = face_recognition.face_encodings(new_student_image)[
                            0]

                        # Append the new student's information to the existing lists
                        known_face_enc.append(new_student_encoding)
                        known_face_names.append(f"{first_name} {last_name}")

                        st.image(image_path, caption="Captured Image",
                                 use_column_width=True)

            def display_image(image, button):
                if image is not None:
                    st.image(image, channels="RGB", use_column_width=True)
                    if st.button("Save Image", key=button):
                        processor.on_button_click(button)

            # Create a button for saving the captured image
            button = st.button("Save Image")

            webrtc_ctx = webrtc_streamer(
                key="example", video_processor_factory=ImageCaptureProcessor, async_processing=False)

            if webrtc_ctx.video_processor:
                processor = webrtc_ctx.video_processor
                display_image(processor.image, button)

# Initialize video_capture outside of the 'try' block
if nav == "Record Attendance":
    if st.session_state.i == 0:
        st.title("Cannot Access")
        st.text("Please log into your account to perform this action")
    else:
        st.title("Record Attendance")

        # Add a dropdown for selecting periods with a default value of None
        selected_period = st.selectbox(
            "Select Lecture", [None, "Lecture 1", "Lecture 2", "Lecture 3", "Lecture 4", "Lecture 5"])

        if selected_period:
            stframe = st.empty()
            video_capture = cv2.VideoCapture(0)
            # Initialize student_present dictionary
            student_present = {name: False for name in students}
            # Add the period to the CSV file name
            current_period = selected_period.replace(" ", "_").lower()
            csv_file_path = os.path.join(
                'C:\\Users\\User\\Desktop\\Ccoder\\opencv', f'{current_date}_{current_period}.csv')

            try:
                with open(csv_file_path, 'w+', newline='') as f:
                    lnwriter = csv.writer(f)
                    lnwriter.writerow([selected_period, " "])

                    # Load images for each person
                    person1_images = load_images_from_folder(person1_folder)
                    person2_images = load_images_from_folder(person2_folder)
                    person3_images = load_images_from_folder(person3_folder)
                    person4_images = load_images_from_folder(person4_folder)

                    known_face_enc.extend(face_recognition.face_encodings(img)[0] for img in
                                          person1_images + person2_images + person3_images + person4_images)
                    known_face_names.extend(["Deepika Padukone"] * len(person1_images) + ["Virat Kohli"] * len(
                        person2_images) + ["Albert Einstein"] * len(person3_images) + ["Parth Hemdan"] * len(person4_images))
                    students = known_face_names.copy()

                    while True:
                        ret, frame = video_capture.read()
                        if not ret:
                            st.error("Error: Couldn't read frame. Exiting...")
                            break

                        # Perform face recognition
                        frame_with_recognition = recognize_faces(
                            frame, known_face_enc, students, student_present, lnwriter)

                        # Display the frame using OpenCV
                        cv2.imshow("Webcam Feed", frame_with_recognition)

                        # OpenCV: Break the loop when the user presses 'q'
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                # OpenCV: Release the webcam
                video_capture.release()

                # OpenCV: Close the window
                cv2.destroyAllWindows()

            except PermissionError as pe:
                st.error(f"Permission Error: {pe}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                # Close the CSV file if it was opened successfully
                if 'f' in locals() and f is not None:
                    f.close()

# View Attendance section
if nav == "View Attendance":
    if st.session_state.i == 0:
        st.title("Cannot Access")
        st.text("Please log into your account to perform this action")
    else:
        st.title("View Attendance")

        # List all CSV files in the directory for the selected date
        csv_files = [f for f in os.listdir('C:\\Users\\User\\Desktop\\Ccoder\\opencv') if
                     f.startswith(f'{current_date}_') and f.endswith('.csv')]

        if not csv_files:
            st.warning("No CSV files found in the directory.")
            st.stop()

        # Let the user choose the period
        selected_period_view = st.selectbox("Select Lecture",
                                            ["All Lectures"] + [file.split('_')[2].split('.')[0] for file in csv_files])

        # csv_file_path_view = ""
        # Load attendance data based on the selected period
        if selected_period_view == "All Lectures":
            # Load data for all periods
            headers = ["Name", "Time"]  # Adjust column names accordingly
            attendance_data = pd.concat([pd.read_csv(os.path.join('C:\\Users\\User\\Desktop\\Ccoder\\opencv', file),
                                                     header=None, names=headers) for file in csv_files if os.path.exists(os.path.join('C:\\Users\\User\\Desktop\\Ccoder\\opencv', file))])
        else:
            # Load data for the selected period
            headers = ["Name", "Time"]  # Adjust column names accordingly
            selected_csv_view = f'{current_date}_lecture_{selected_period_view.lower()}.csv'
            csv_file_path_view = os.path.join(
                'C:\\Users\\User\\Desktop\\Ccoder\\opencv', selected_csv_view)

            if os.path.exists(csv_file_path_view):
                attendance_data = pd.read_csv(
                    csv_file_path_view, header=None, names=headers)
            else:
                st.warning(
                    f"No attendance data found for {selected_period_view}")
                st.stop()

        # Display the attendance data
        st.write("Attendance Data:")
        st.write(attendance_data)

        # Provide a button to download the selected CSV file
        download_button = st.button("Download Selected CSV")

        # Handle the button click event
        if download_button:
            if selected_period_view == "All Lectures":
                st.download_button(
                    label="Download CSV",
                    data=attendance_data.to_csv(index=False).encode('utf-8'),
                    file_name=f'{current_date}_all_periods.csv',
                    key="download_csv_button")
            # Download the selected CSV file
            else:
                st.download_button(
                    label="Download CSV",
                    data=open(csv_file_path_view, 'rb').read(),
                    file_name=selected_csv_view,
                    key="download_csv_button"
                )
