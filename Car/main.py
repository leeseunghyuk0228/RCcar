from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from mainUI import Ui_MainWindow
from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
from sense_hat import SenseHat
from time import sleep
import threading
import mysql.connector
import cv2
import os
import argparse
import numpy as np
import sys
import importlib.util

# speed adj check
speed_up,speed_down=0,0
# motor on or off check
powered=0
# DB Driving Cnt
cnt=1
isc=0
# DB command index
oidx=1
idx=1
camUsing=0
# Motor
speed = 0
flag=0
TF=0
mh = Raspi_MotorHAT(addr=0x6f)
myMotor = mh.getMotor(2)  # 핀번호
sense = SenseHat()
servo = PWM(0x6F)
servo.setPWMFreq(60)  # Set frequency to 60 Hz
print("Motor Setting Success")
cmd_list=[0,"Motor Start","Motor Stop","Speed Up Start","Speed UP End","Speed Down Start","Speed Down End"]

class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(320,240),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        threading.Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.init()
        self.ui.horizontalSlider.valueChanged.connect(self.change_angle)

    def init(self):
        #### Database Connection
        self.DBConnect()
        #### Servo Motor Neutral
        servo.setPWM(0,0,375)


    def od(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--modeldir', help='Folder the .tflite file is located in',default='Sample_TFLite_model')
        parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                            default='detect.tflite')
        parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                            default='labelmap.txt')
        parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                            default=0.5)
        parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support thentered, errors may occur.',
                            default='1280x720')
        parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                            action='store_true')

        args = parser.parse_args()

        MODEL_NAME = args.modeldir
        GRAPH_NAME = args.graph
        LABELMAP_NAME = args.labels
        min_conf_threshold = float(args.threshold)
        resW, resH = args.resolution.split('x')
        imW, imH = int(resW), int(resH)
        use_TPU = args.edgetpu

        pkg = importlib.util.find_spec('tflite_runtime')
        if pkg:
            from tflite_runtime.interpreter import Interpreter
            if use_TPU:
                from tflite_runtime.interpreter import load_delegate
        else:
            from tensorflow.lite.python.interpreter import Interpreter
            if use_TPU:
                from tensorflow.lite.python.interpreter import load_delegate

        if use_TPU:
            if (GRAPH_NAME == 'detect.tflite'):
                GRAPH_NAME = 'edgetpu.tflite'

        CWD_PATH = os.getcwd()

        PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
        PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

        with open(PATH_TO_LABELS, 'r') as f:
            labels = [line.strip() for line in f.readlines()]

        if labels[0] == '???':
            del(labels[0])

        if use_TPU:
            interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                      experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
            print(PATH_TO_CKPT)
        else:
            interpreter = Interpreter(model_path=PATH_TO_CKPT)

        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]

        floating_model = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5

        outname = output_details[0]['name']

        if ('StatefulPartitionedCall' in outname): # This is a TF2 model
            boxes_idx, classes_idx, scores_idx = 1, 3, 0
        else: # This is a TF1 model
            boxes_idx, classes_idx, scores_idx = 0, 1, 2

        frame_rate_calc = 1
        freq = cv2.getTickFrequency()

        self.videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
        sleep(1)

        while True:
            if(TF==1):
                break
            # Start timer (for calculating frame rate)
            t1 = cv2.getTickCount()

            # Grab frame from video stream
            frame1 = self.videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] # Bounding box coordinates of detect
            classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] # Class index of detected object
            scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0] # Confidence of detected objects

            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                global oidx
                if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                    ymin = int(max(1,(boxes[i][0] * imH)))
                    xmin = int(max(1,(boxes[i][1] * imW)))
                    ymax = int(min(imH,(boxes[i][2] * imH)))
                    xmax = int(min(imW,(boxes[i][3] * imW)))

                    # Draw label
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                    label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                    print(label)
                    Time = QDateTime().currentDateTime().toPython()
                    query = "insert into Driving_object(cmdIDX,driving_cnt,time,object,percent) values (%s,%s,%s,%s,%s)"
                    value = (oidx, cnt, Time, object_name,int(scores[i]*100))
                    self.cur.execute(query, value)
                    self.db.commit()
                    oidx+=1
                    sleep(0.5)

        # Clean up



    ############### About Thread Create ##############
    def ThCreate(self):
        print("Create Thread Try...")
        self.adj_speed()
        if(isc==1):
            self.show_cam()
        else:
            self.odth=threading.Thread(target=self.od)
            self.odth.daemon=True
            self.odth.start()

        print("Create Thread Success")

    ############### About Cam ########################
    def isCamera(self):
        global isc
        isc=1

    def show_cam(self):
        global camUsing
        if(camUsing==0):
            self.cam = cv2.VideoCapture(0)
            self.cam.set(3,480)
            self.cam.set(4,320)
            camUsing=1
        ret, self.img = self.cam.read()
        if ret:
            imgBGR = cv2.flip(self.img, 0)
            imgRGB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB)
            h, w, byte = imgRGB.shape
            img = QImage(imgRGB, w, h, byte * w, QImage.Format_RGB888)
            pix_img = QPixmap(img)
            self.setImage(pix_img)
        else:
            print("Can't Read from Camera")

        self.t3 = threading.Timer(0.01,self.show_cam)
        self.t3.start()
        if(flag==1):
            self.t3.cancel()

    ############### Sense HAT ########################
    def sense_set(self):
        myMotor.setSpeed(speed)
        R, G, B = 0, 0, 0
        if (speed > 200):  # red
            R = 255
        elif (speed > 100):  # yellow
            R, G = 255, 255
        elif (speed > 50):  # Blue
            B = 255
        elif (speed > 0):
            R, G, B = 100, 100, 100

        for i in range(8):
            for j in range(8):
                sense.set_pixel(i, j, R, G, B)

    ############### About RC Car Move ################
    def adj_speed(self):
        global speed, myMotor
        if (speed_up == 1 and speed + 3 <= 250):
            speed += 3
            myMotor.setSpeed(speed)
            self.ui.Display_Speed.display(speed)
            print("speed : " + str(speed))

            self.sense_set()

        elif (speed_down == 1 and speed - 3 >= 0):
            speed -= 3
            myMotor.setSpeed(speed)
            self.ui.Display_Speed.display(speed)
            print("speed : " + str(speed))
            self.sense_set()

        self.t1 = threading.Timer(0.1, self.adj_speed)
        self.t1.start()
        if(flag==1):
            self.t1.cancel()

    def change_angle(self):
        global servo
        servo.setPWM(0,0,self.ui.horizontalSlider.value())

    def go(self):
        global myMotor,speed,powered,TF
        if(powered==0):
            self.ThCreate()
            TF=0
            powered=1
            speed = 10
            self.InsertCommand(1)
            sleep(0.2)
            myMotor.run(Raspi_MotorHAT.BACKWARD)

    def stop(self):
        global speed,myMotor,powered
        if(powered==1):
            global TF
            powered=0
            speed = 0
            TF=1
            sleep(0.2)
            self.InsertCommand(2)
            myMotor.run(Raspi_MotorHAT.RELEASE)

    # Button pressed
    def speedup(self):
        global speed_up
        if(powered==1):
            self.InsertCommand(3)
            speed_up=1

    # Button pressed
    def speeddown(self):
        global speed_down
        if (powered == 1):
            self.InsertCommand(5)
            speed_down = 1

    # Button Released
    def upreleased(self):
        global speed_up
        if(powered==1):
            self.InsertCommand(4)
            speed_up=0

    # Button Released
    def downreleased(self):
        global speed_down
        if(powered==1):
            self.InsertCommand(6)
            speed_down=0

    # MotorForward
    def motorf(self):
        myMotor.run(Raspi_MotorHAT.BACKWARD)
    # MotorBackward
    def motorb(self):
        myMotor.run(Raspi_MotorHAT.FORWARD)

    #################### About UI Display ####################

    ## Display Camera
    def setImage(self,img):
        self.ui.Display_Camera.setPixmap(img)

    #################### Database Connecting ####################
    def DBConnect(self):
        print("DB Connect Try ... ")
        self.db = mysql.connector.connect(host='3.39.189.58', user='ssafy',
                                          password='ssafy1234', database='minDB', 
                                          auth_plugin='mysql_native_password')
        self.cur = self.db.cursor()
        print("DB Connecting Success ")
        self.cur.execute("select * from Driving_command order by cmdIDX desc")
        result = self.cur.fetchall()

        if (len(result) != 0):
            global cnt, idx
            cnt = result[0][1] + 1  # driving cnt
            idx = result[0][0] + 1  # Comand idx

        self.cur.execute("select * from Driving_object order by cmdIDX desc")
        result = self.cur.fetchall()

        if(len(result)!=0):
            global oidx
            oidx = result[0][0] + 1  # Comand idx

    def InsertCommand(self,cmd):
        global idx,cnt

        print("This Command is : "+cmd_list[cmd])

        Time = QDateTime().currentDateTime().toPython()
        query = "insert into Driving_command(cmdIDX,driving_cnt,time,command,speed) values (%s,%s,%s,%s,%s)"
        value = (idx,cnt, Time,cmd_list[cmd],speed)

        idx+=1
        self.cur.execute(query,value)
        self.db.commit()

    def pollingQuery(self):
        self.cur.execute("select * from Driving_command where driving_cnt = %s order by cmdIDX desc",(cnt,))
        result= self.cur.fetchall()
        if(len(result)>0):
            print("\nCommand List From This Driving")
            for (cmdIDX,driving_cnt, time, command, speed) in reversed(result):
                print("%5d | %5d | %6s | %15s | %4d" %(cmdIDX,driving_cnt, time.strftime("%Y%m%d %H:%M:%S"), command,speed))

            self.cur.execute("select AVG(speed) from Driving_command where driving_cnt = %s",(cnt,))
            AVGSPD= self.cur.fetchall()[0][0]
            condition = ''
            if(AVGSPD > 200):
                condition = "BADBADBAD"
            elif(AVGSPD > 180):
                condition = "Not Bad"
            elif(AVGSPD > 100):
                condition = "SAFE"
            else:
                condition = "Too Slow...-_-"
            for _ in range(3):
                print('.')
            print("Average Speed : " + str(AVGSPD))
            print("Driving Score : " + str(condition))
            for _ in range(3):
                print('.')

        self.cur.execute("select * from Driving_object where driving_cnt = %s order by cmdIDX desc", (cnt,))
        result = self.cur.fetchall()
        if (len(result) > 0):
            print("\nFinding Objects From This Driving")
            for (cmdIDX, driving_cnt, time, object, percent) in reversed(result):
                print("%5d | %5d | %6s | %15s | %4d" % (
                cmdIDX, driving_cnt, time.strftime("%Y%m%d %H:%M:%S"), object, percent))

            for _ in range(3):
                print('.')

    ##################### Closing Event ##################
    def closeEvent(self,event):
        global flag
        flag=1
        if(isc==0):
            self.videostream.stop()
        self.pollingQuery()
        self.cur.close()
        self.db.close()

app = QApplication()
win = MyApp()
win.show()
app.exec_()
