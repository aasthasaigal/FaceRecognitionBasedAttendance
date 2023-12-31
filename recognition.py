import os
import numpy as np
import cv2
import time

from datetime import datetime

# Current date time in local system
date = datetime.now().date()
date = str(date)
print(date)
currentAdds = []

fileName = str("presentPeople"+date+".txt")


try:
	with open(fileName) as f:
		content = f.readlines()
except FileNotFoundError:
	content = []



content = [x.strip() for x in content]
if len(content) == 0:
	presenties = []
else:
	presenties = content[0].split()
	presenties = [x.lower() for x in presenties]
print("All people",presenties)


files = [f for f in os.listdir('dataset') if f.endswith('.npy')]
names = [f[:-4] for f in files]

face_data = []
present = []

for filename in files:
	data = np.load('dataset/'+filename)
	face_data.append(data)

face_data = np.concatenate(face_data, axis=0)

print(face_data.shape)
print(type(face_data))
face_data = np.reshape(face_data,(face_data.shape[0],100,100,3))


# model
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing.image import ImageDataGenerator

classifier = Sequential()

classifier.add(Convolution2D(32 ,(3 ,3) ,input_shape=(100 ,100 ,3) ,activation = 'relu'))
classifier.add(MaxPooling2D(pool_size=(2,2)))

classifier.add(Convolution2D(32 ,(3 ,3)  ,activation = 'relu'))
classifier.add(MaxPooling2D(pool_size=(2,2)))

classifier.add(Flatten())

classifier.add(Dense(units = 128, activation = 'relu' ))
classifier.add(Dense(units = len(names), activation = 'softmax' ))

classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

classifier.load_weights('model.h5')
#end of training the model

capture = cv2.VideoCapture(0)

past = ""
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

while True:
	returned , image = capture.read()

	if not returned:
		continue
	
	faces = face_cascade.detectMultiScale(image , 1.3, 5)

	for face in faces:
		x,y,w,h = face

		onlyFace = image[y:y+h,x:x+w]
		onlyFace = cv2.resize(onlyFace,(100,100))
		
		print(onlyFace.shape)
		onlyFace = np.reshape(onlyFace,(1,100,100,3))
		print("only face", onlyFace.shape)
        
		# print("After changing shape",onlyFace.shape)

		prediction = classifier.predict([[onlyFace]])
		print(prediction)

		# Drawing rectangle and writing name on it
		cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
		cv2.putText(image,names[np.argmax(prediction)],(x,y),cv2.FONT_ITALIC,1,(0,255,0),2)
		if not past == names[np.argmax(prediction)]:
			present.append(names[np.argmax(prediction)])
		past = names[np.argmax(prediction)]

	cv2.imshow("Attendence for "+date+" (Press q to Quit)",image)
	key = cv2.waitKey(1)
	if key & 0xFF == ord('q'):
		break
print("Present" ,present)

f=open(fileName, "a+")

for value in present:
	if not value.lower() in presenties:
		if not value.lower() in currentAdds:	
			f.write(value.lower()+ " ")
			currentAdds.append(value.lower())
f.close()



capture.release()

cv2.destroyAllWindows()