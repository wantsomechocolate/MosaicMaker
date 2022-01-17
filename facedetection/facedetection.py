
import cv2

imagePath = "test.jpg"

image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray, 1.1, 4)
print("Found {0} face(s)!".format(len(faces)))

eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
print("Found {0} eye(s)!".format(len(eyes)))

#mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml')
#mouths = mouth_cascade.detectMultiScale(gray, 1.1, 4)
print("Found {0} mouth(s)!".format(len(mouths)))

#nose_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_mcs_nose.xml')
#noses = nose_cascade.detectMultiScale(gray, 1.1, 4)
print("Found {0} nose(s)!".format(len(noses)))


# Draw a rectangle around the faces
#for (x, y, w, h) in faces:
#    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

#for (x, y, w, h) in eyes:
#    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

cv2.imshow("Faces found", image)

cv2.waitKey(0)

features_list = [faces,eyes]
