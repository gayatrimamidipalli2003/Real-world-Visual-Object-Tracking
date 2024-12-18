# import packages 
from imutils.video import VideoStream
from imutils.video import FPS
import matplotlib.pyplot as plt
import numpy as np
import argparse
import imutils
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.4,  # Increased confidence threshold for better accuracy
                help="minimum probability to filter weak predictions")
args = vars(ap.parse_args())

# Define class labels that MobileNet SSD was trained to detect
CLASSES = ["aeroplane", "background", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor", "mobile"]

# Assign random colors to each class
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load the serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# Start the video stream and warm up the camera
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Create a named window and set it to fullscreen
cv2.namedWindow("Object Detection", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Object Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Start the FPS counter
fps = FPS().start()

# Loop over the frames from the video stream
while True:
    # Grab the frame from the threaded video stream
    frame = vs.read()
    
    # Optionally resize it if needed (remove the next line for full frame)
    # frame = imutils.resize(frame, width=400)  # You can adjust this or remove it

    (h, w) = frame.shape[:2]

    # Preprocess the frame by creating a blob
    blob = cv2.dnn.blobFromImage(frame, scalefactor=0.007843, size=(300, 300), mean=127.5, swapRB=True)

    # Set the blob as input to the network and obtain the detections
    net.setInput(blob)
    predictions = net.forward()

    # Loop over the predictions
    for i in np.arange(0, predictions.shape[2]):
        confidence = predictions[0, 0, i, 2]

        # Filter out weak predictions based on the confidence threshold
        if confidence > args["confidence"]:
            idx = int(predictions[0, 0, i, 1])
            box = predictions[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            print("Object detected:", label)

            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    # Show the frame with bounding boxes and labels
    cv2.imshow("Object Detection", frame)

    # Press 'q' to break the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

    # Update the FPS counter
    fps.update()

# Stop the FPS counter
fps.stop()

# Display FPS information
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# Clean up: close all windows and stop the video stream
cv2.destroyAllWindows()
vs.stop()

