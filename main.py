import numpy
import cv2
import sys
from include.haar_cascade import haarCascade
from include.face_landmark_detection import faceLandmarkDetection


#If True enables the verbose mode
DEBUG = True 

#Antropometric constant values
# of the human head.
#X-Y-Z with X pointing forward and Y on the left.
#The X-Y-Z coordinates used are like the standard
# coordinates of ROS (robotic operative system)
P3D_RIGHT_SIDE = numpy.float32([-100.0, -77.5, -5.0]) #0
P3D_MENTON = numpy.float32([0.0, 0.0, -133.0]) #8
P3D_LEFT_SIDE = numpy.float32([-100.0, 77.5, -5.0]) #16
P3D_SELLION = numpy.float32([0.0, 0.0, 0.0]) #27
P3D_NOSE = numpy.float32([21.0, 0.0, -48.0]) #30
P3D_SUB_NOSE = numpy.float32([5.0, 0.0, -55.0]) #33
P3D_RIGHT_EYE = numpy.float32([-20.0, -65.5,-5.0]) #36
P3D_RIGHT_TEAR = numpy.float32([-10.0, -40.5,-5.0]) #39
P3D_LEFT_TEAR = numpy.float32([-10.0, 40.5,-5.0]) #42
P3D_LEFT_EYE = numpy.float32([-20.0, 65.5,-5.0]) #45
P3D_STOMION = numpy.float32([10.0, 0.0, -75.0]) #62

#The points to draw in debug mode
TRIANGLE_POINTS = list(range(36,61))
TRACKED_POINTS = (0, 8, 16, 27, 30, 33, 36, 39, 42, 45, 62)
ALL_POINTS = list(range(0,68))


def main():

    #Defining the video capture object
    video_capture = cv2.VideoCapture(0)

    if(video_capture.isOpened() == False):
        print("Error: the resource is busy or unvailable")
    else:
        print("The video source has been opened correctly...")

    #Obtaining the CAM dimension
    cam_w = int(video_capture.get(3))
    cam_h = int(video_capture.get(4))

    #Defining the camera matrix
    #To have better result it is necessary to find the focal
    # lenght of the camera. fx/fy are the focal lengths (in pixels) 
    # and cx/cy are the optical centres. These values can be obtained 
    # roughly by approximation:
    # cx = 640/2 = 320
    # cy = 480/2 = 240
    # fx = fy = cx/tan(60/2 * pi / 180) = 554.26
    camera_matrix = numpy.float32([[554.26,    0.0,  320],
                                   [   0.0, 554.26,  240], 
                                   [   0.0,    0.0,  1.0] ])

    #Distortion coefficients
    #camera_distortion = numpy.float32([-0.25, 0.11, -0.0002, 0, 0])
    camera_distortion = numpy.float32([0.0, 0.0, 0.0, 0.0, 0.0])

    #This matrix contains the 3D points of the
    # 11 landmarks we want to find. It has been
    # obtained from antrophometric measurement
    # on the human head.
    landmark_main_3d_points = numpy.float32([P3D_RIGHT_SIDE,
                                             P3D_MENTON, 
                                             P3D_LEFT_SIDE,
                                             P3D_SELLION,
                                             P3D_NOSE,
                                             P3D_SUB_NOSE,
                                             P3D_RIGHT_EYE,
                                             P3D_RIGHT_TEAR,
                                             P3D_LEFT_TEAR,
                                             P3D_LEFT_EYE,
                                             P3D_STOMION])

    #Declaring the two classifiers
    my_cascade = haarCascade("./etc/haarcascade_frontalface_alt.xml", "./etc/haarcascade_profileface.xml")
    my_detector = faceLandmarkDetection('./etc/shape_predictor_68_face_landmarks.dat')

    #Error counter definition
    no_face_counter = 0

    #Variables that identify the face
    # position in the main frame.
    face_x1 = 0
    face_y1 = 0
    face_x2 = 0
    face_y2 = 0
    face_w = 0
    face_h = 0

    #Variables that identify the ROI
    # position in the main frame.
    roi_x1 = 0
    roi_y1 = 0
    roi_x2 = cam_w
    roi_y2 = cam_h
    roi_w = cam_w
    roi_h = cam_h
    roi_resize_w = int(cam_w/10)
    roi_resize_h = int(cam_h/10)

    while(True):

        # Capture frame-by-frame
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame[roi_y1:roi_y2, roi_x1:roi_x2], cv2.COLOR_BGR2GRAY)

        #Looking for faces with cascade
        #The scale factor for the frontal face is 1.10 (10%)
        #Scale factor left=1.15 and right=1.25 (25% and 25%)
        #Because the chain is: frontal>left>right the
        # last classifier is sloow. To compensate we
        # increased the scale factor (faster but less
        # accurate).
        # minsize = 40x40 pixel
        #Return code: 1=Frontal, 2=FrontRotLeft, 
        # 3=FrontRotRight, 4=ProfileLeft, 5=ProfileRight.
        my_cascade.findFace(gray, True, True, True, True, 1.10, 1.25, 1.25, 1.25, 40, 40)

        #Accumulate error values in a counter
        if(my_cascade.face_type == 0): 
            no_face_counter += 1

        #If any face is found for a certain
        # number of cycles, then the ROI is reset
        if(no_face_counter == 50):
            no_face_counter = 0
            roi_x1 = 0
            roi_y1 = 0
            roi_x2 = cam_w
            roi_y2 = cam_h
            roi_w = cam_w
            roi_h = cam_h

        #Checking wich kind of face it is returned
        if(my_cascade.face_type > 0):

            #Updating the face position
            face_x1 = my_cascade.face_x + roi_x1
            face_y1 = my_cascade.face_y + roi_y1
            face_x2 = my_cascade.face_x + my_cascade.face_w + roi_x1
            face_y2 = my_cascade.face_y + my_cascade.face_h + roi_y1
            face_w = my_cascade.face_w
            face_h = my_cascade.face_h

            #Updating the ROI position       
            roi_x1 = face_x1 - roi_resize_w
            if (roi_x1 < 0): roi_x1 = 0
            roi_y1 = face_y1 - roi_resize_h
            if(roi_y1 < 0): roi_y1 = 0
            roi_w = face_w + roi_resize_w + roi_resize_w
            if(roi_w > cam_w): roi_w = cam_w
            roi_h = face_h + roi_resize_h + roi_resize_h
            if(roi_h > cam_h): roi_h = cam_h    
            roi_x2 = face_x2 + roi_resize_w
            if (roi_x2 > cam_w): roi_x2 = cam_w
            roi_y2 = face_y2 + roi_resize_h
            if(roi_y2 > cam_h): roi_y2 = cam_h

            #Debugging printing utilities
            if(DEBUG == True):
                print("FACE: ", face_x1, face_y1, face_x2, face_y2, face_w, face_h)
                print("ROI: ", roi_x1, roi_y1, roi_x2, roi_y2, roi_w, roi_h)
                #Drawing a green rectangle
                # (and text) around the face.
                text_x1 = face_x1
                text_y1 = face_y1 - 3
                if(text_y1 < 0): text_y1 = 0
                cv2.putText(frame, "FACE", (text_x1,text_y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1);
                cv2.rectangle(frame, 
                             (face_x1, face_y1), 
                             (face_x2, face_y2), 
                             (0, 255, 0),
                              2)

            #In case of a frontal face it
            # is called the landamark detector
            if(my_cascade.face_type == 1):
                matrix_landmarks = my_detector.returnLandmarks(frame, face_x1, face_y1, face_x2, face_y2)

                if(DEBUG == True):
                    for row in TRACKED_POINTS:
                        cv2.circle(frame,( matrix_landmarks[row].item((0,0)), matrix_landmarks[row].item((0,1)) ), 2, (0,0,255), -1)

                #Applying the PnP solver to find the 3D pose
                # of the head from the 2D position of the
                # landmarks.
                #retval - bool
                #rvec - Output rotation vector that, together with tvec, brings 
                # points from the model coordinate system to the camera coordinate system.
                #tvec - Output translation vector.
                retval, rvec, tvec = cv2.solvePnP(landmark_main_3d_points, 
                                                  my_detector.landmark_main_points, 
                                                  camera_matrix, camera_distortion)

                #Now we project the 3D points into the image plane
                #Creating a 3-axis to be used as reference in the image.
                axis = numpy.float32([[50,0,0], 
                                      [0,50,0], 
                                      [0,0,50]])
                imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, camera_distortion)

                #Drawing the three axis on the image frame.
                #The opencv colors are defined as BGR colors such as: 
                # (a, b, c) >> Blue = a, Green = b and Red = c
                #Our axis/color convention is X=R, Y=G, Z=B
                cv2.line(frame, my_detector._sellion, tuple(imgpts[1].ravel()), (0,255,0), 3) #GREEN
                cv2.line(frame, my_detector._sellion, tuple(imgpts[2].ravel()), (255,0,0), 3) #BLUE
                cv2.line(frame, my_detector._sellion, tuple(imgpts[0].ravel()), (0,0,255), 3) #RED

        #Drawing a yellow rectangle
        # (and text) around the ROI.
        if(DEBUG == True):
            text_x1 = roi_x1
            text_y1 = roi_y1 - 3
            if(text_y1 < 0): text_y1 = 0
            cv2.putText(frame, "ROI", (text_x1,text_y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1);
            cv2.rectangle(frame, 
                         (roi_x1, roi_y1), 
                         (roi_x2, roi_y2), 
                         (0, 255, 255),
                         2)

        #TODO remove this function when tested
        #rows=480
        #cols = 640
        #M = cv2.getRotationMatrix2D((cols/2,rows/2),30,1)
        #dst = cv2.warpAffine(frame, M, (cols,rows))
        #cv2.imshow('Rotated', dst)

        #Showing the frame and waiting
        # for the exit command
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
   
    #Release the camera
    video_capture.release()
    print("Bye...")



if __name__ == "__main__":
    main()
