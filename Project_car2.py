import cv2
import numpy as np

cam = cv2.VideoCapture(0)

cam.set(3,320)
cam.set(4,240)

#Optical flow

feature_parameters = dict(maxCorners = 100,
                          qualityLevel = 0.3,
                          minDistance = 7,
                          blockSize =7)
flow_parameters = dict(winSize = (15,15),
                       maxLevel = 3,
                       criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
ret, frame1 = cam.read()
frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
points_frame1 = cv2.goodFeaturesToTrack(frame1_gray, mask = None, **feature_parameters)

mask = np.zeros_like(frame1)


while(1):
    ret,frame2 = cam.read()
    frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    points_frame2, st, err = cv2.calcOpticalFlowPyrLK(frame1_gray, frame2_gray, points_frame1, None, **flow_parameters)
    if st == None:
        good_new = points_frame2[st == 1]
        good_old = points_frame1[st == 1]
    else:
        good_new = points_frame2
        good_old = points_frame1
    for i,(new,old) in enumerate(zip(good_new,good_old)):
        a,b = new.ravel()
        c,d = old.ravel()
        cv2.line(mask, (a,b), (c,d), [255,0,0], 2)
        cv2.circle(frame2, (a,b), 5, [255,0,0], -1)

    img = cv2.add(frame2, mask)
    cv2.imshow('output',frame2)

    if cv2.waitKey(1) == 27:  ## 27 - ASCII for escape key
        break
    frame1_gray = frame2_gray.copy()
    points_frame1 = good_new.reshape(-1,1,2)

cam.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
