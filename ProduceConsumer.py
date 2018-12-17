#!/usr/bin/env python3

import threading
import cv2
import queue


q1 = queue.Queue()
q2 = queue.Queue()
sem1 = threading.Semaphore(10)
sem2 = threading.Semaphore(0)
sem3 = threading.Semaphore(10)
sem4 = threading.Semaphore(0)

class ExtractFrames(threading.Thread):
    def __init__(self,fileName, outputQ):
        threading.Thread.__init__(self)
        self.fileName = fileName
        self.q = outputQ

    def run(self):
        count = 0
        vidcap = cv2.VideoCapture(self.fileName)
        success, image = vidcap.read()
        while success:
            sem1.acquire()
            success, jpgImage = cv2.imencode('.jpg',image)
            self.q.put(jpgImage)
            sem2.release()
            success, image = vidcap.read()
            print("done extracting frame ", count)
            count += 1
        print("done extracting frames")


class Convert2grayScale(threading.Thread):
    def __init__(self, outputQ, inputQ):
        threading.Thread.__init__(self)
        self.oQ = outputQ
        self.iQ = inputQ

    def run(self):
        count = 0
        while not self.oQ.empty():
            sem2.acquire()
            frame = self.oQ.get()
            sem1.release()
            image = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED)
            grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            sem3.acquire()
            self.iQ.put(grayFrame)
            sem4.release()
            print("done converting frame ", count)
            count += 1
        print("done converting frames")

class DisplayFrames(threading.Thread):
    def __init__(self, inputQ):
        threading.Thread.__init__(self)
        self.iQ = inputQ

    def run(self):
        while not self.iQ.empty():
            sem4.acquire()
            frame = self.iQ.get()
            sem3.release()

            cv2.imshow("Video", frame)
            if cv2.waitKey(24) and 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()




fileName = 'clip.mp4'

extractFrames = ExtractFrames(fileName, q1)
convert2gray = Convert2grayScale(q1,q2)
displayFrames = DisplayFrames(q2)
extractFrames.start()
convert2gray.start()
displayFrames.start()
            
        
     
