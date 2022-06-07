from xml.etree.ElementTree import QName
import face_recognition
import cv2
import numpy as np
import pymongo
import datetime

import serial
import time


arduino = serial.Serial(port="/dev/tty.usbmodem14101", baudrate=9600)

db_url = "mongodb+srv://Recognize:SPeDir6zC6wmUFwF@face.2cmws.mongodb.net/myfirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(db_url)
db = "face-rec"
users_col = client[db]["users"]
event_col = client[db]["event_log"]

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(1)
# Load a sample picture and learn how to recognize it.
known_face_encodings = []
known_face_names = []
known_all_data = []

for user in users_col.find({}, {"_id": 0}):
    known_face_encodings.append(user["face_encoding"])
    known_face_names.append(user["name"] + " " + user["surname"])
    known_all_data.append(user)

# Initialize some variables and arrays
event_log_local = []
user_log_local = []
face_locations = []
face_encodings = []

face_names = []
process_this_frame = True
trigger = False
index = -1
while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding
            )
            name = "Unknown"

            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )

            best_match_index = np.argmin(face_distances)
            face_dis = face_distances[best_match_index]
            type(face_dis)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            """face_dis=face_recognition.face_distance(face_encoding)"""
            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        threshold_value = cv2.rectangle(
            frame, (left, top), (right, bottom), (255, 0, 255), 2
        )

        # Draw a label with a name below the face
        cv2.rectangle(
            frame, (left, bottom - 70), (right, bottom), (255, 0, 255), cv2.FILLED
        )

        threshold_value = bottom - top
        q_name = name.split(" ")[0]
        if name != "Unknown":
            if trigger == False:
                for user in known_all_data:
                    if user["name"] == q_name:

                        data = user
                        index = known_all_data.index(user)

        if threshold_value > 170 and data["flag"] == 0 and name != "Unknown":

            name = known_face_names[best_match_index]
            current_date = datetime.datetime.now()
            dt_enter = int(current_date.strftime("%Y%m%d%H%M%S"))
            time = dt_enter - data["exit_date"]
            if data["first"] == 0:
                # log = name + " " + dt_enter + " tarihinde giriş yaptı"

                # event_col.insert_one(
                #     {
                #         "name": name,
                #         "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                #         "aksiyon": "Giriş",
                #         "sure": 0,
                #         "ts": dt_enter,
                #     }
                # )
                event_log_local.append(
                    {
                        "name": name,
                        "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "aksiyon": "Giriş",
                        "sure": 0,
                        "ts": dt_enter,
                    }
                )
                # users_col.update(
                #     {"name": q_name},
                #     {"$set": {"enter_date": dt_enter, "flag": 1, "first": 1}},
                #     False,
                #     True,
                # )
                user_log_local.append(
                    {"name": q_name, "enter_date": dt_enter, "flag": 1, "first": 1}
                )
                known_all_data[index]["enter_date"] = dt_enter
                known_all_data[index]["flag"] = 1
                known_all_data[index]["first"] = 1

                print(data["name"] + " Giriş yapmıştır")
                arduino.write(b"T")
            elif time > 6:
                # # log = name + " " + str(dt_enter) + " tarihinde giriş yaptı"
                # event_col.insert_one(
                #     {
                #         "name": name,
                #         "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                #         "aksiyon": "Giriş",
                #         "sure": 0,
                #         "ts": dt_enter,
                #     }
                # )
                event_log_local.append(
                    {
                        "name": q_name,
                        "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "aksiyon": "Giriş",
                        "sure": 0,
                        "ts": dt_enter,
                    }
                )
                # users_col.update(
                #     {"name": q_name},
                #     {"$set": {"enter_date": dt_enter, "flag": 1}},
                #     False,
                #     True,
                # )
                user_log_local.append(
                    {"name": q_name, "enter_date": dt_enter, "flag": 1}
                )
                known_all_data[index]["enter_date"] = dt_enter
                known_all_data[index]["flag"] = 1
                arduino.write(b"T")
                print(data["name"] + " Giriş yapmıştır")

        elif threshold_value > 170 and data["flag"] == 1 and name != "Unknown":

            name = known_face_names[best_match_index]
            current_date = datetime.datetime.now()
            dt_out = int(current_date.strftime("%Y%m%d%H%M%S"))
            time = dt_out - data["enter_date"]

            if time > 6:
                # log = name + " " + str(dt_out) + " tarihinde çıkış yaptı ve yaklaşık olarak " + str(time)  + " saat okulda kaldı."
                # event_col.insert_one(
                #     {
                #         "name": name,
                #         "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                #         "aksiyon": "Çıkış",
                #         "sure": time,
                #         "ts": dt_out,
                #     }
                # )
                event_log_local.append(
                    {
                        "name": name,
                        "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "aksiyon": "Çıkış",
                        "sure": time,
                        "ts": dt_out,
                    }
                )
                # users_col.update(
                #     {"name": q_name},
                #     {"$set": {"exit_date": dt_out, "school_time": time, "flag": 0}},
                #     False,
                #     True,
                # )
                user_log_local.append(
                    {
                        "name": q_name,
                        "exit_date": dt_out,
                        "school_time": time,
                        "flag": 0,
                    }
                )
                known_all_data[index]["exit_date"] = dt_out
                known_all_data[index]["school_time"] = time
                known_all_data[index]["flag"] = 0
                print(data["name"] + " Çıkış yapmıştır")
                arduino.write(b"F")

                trigger = False
        font = cv2.FONT_HERSHEY_DUPLEX
        if name == "Unknown":
            cv2.putText(frame, name, (left, bottom - 6), font, 1.0, (255, 255, 255), 1)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(
                frame,
                "Ratio :" + str(round(1 - face_dis, 2)),
                (left, bottom - 35),
                font,
                1.0,
                (255, 255, 255),
                1,
            )
        elif name != "Unknown":
            if round(1 - face_dis, 2) < 0.50:
                cv2.putText(
                    frame, "Unknown", (left, bottom - 6), font, 1.0, (255, 255, 255), 1
                )
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    frame,
                    "Ratio :" + str(round(1 - face_dis, 2)),
                    (left, bottom - 35),
                    font,
                    1.0,
                    (255, 255, 255),
                    1,
                )
            else:
                cv2.putText(
                    frame,
                    data["name"],
                    (left, bottom - 6),
                    font,
                    1.0,
                    (255, 255, 255),
                    1,
                )
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    frame,
                    "Ratio :" + str(round(1 - face_dis, 2)),
                    (left, bottom - 35),
                    font,
                    1.0,
                    (255, 255, 255),
                    1,
                )

    # Display the resulting image
    cv2.imshow("Video", frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release handle to the webcam
video_capture.release()
for x in event_log_local:
    event_col.insert_one(x)
for x in user_log_local:
    users_col.update({"name": x["name"]}, {"$set": x}, False, True)
cv2.destroyAllWindows()
