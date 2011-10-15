#!/usr/bin/env python2
import cv, sys
filename = sys.argv[1] if len(sys.argv) > 1 else "small1.jpg"
img = cv.LoadImage(filename)
win_name = "Contours"
cv.NamedWindow(win_name, cv.CV_WINDOW_AUTOSIZE)
storage = cv.CreateMemStorage(1000)
grey = cv.CreateImage(cv.GetSize(img), 8, 1)
cv.CvtColor(img, grey, cv.CV_BGR2GRAY)
level = 2
def track(value):
  global storage, grey, img
  out = cv.CloneImage(grey)
  cv.Threshold(out, out, 250, 255, cv.CV_THRESH_BINARY_INV)
  #contour = cv.FindContours(out, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)
  #contour = cv.FindContours(out, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_TC89_L1)
  contour = cv.FindContours(out, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_TC89_KCOS)
  #contour = cv.FindContours(out, storage, cv.CV_RETR_LIST, cv.CV_LINK_RUNS)
  if contour:
    cv.Zero(out)
    tmp = contour
    while (tmp.h_next()):
      tmp = tmp.h_next()
      if len(tmp) < 4:
        continue
      bb = cv.ConvexHull2(tmp, storage)
      print(bb)
      cv.FillConvexPoly(out, bb, 255)
      continue
      s = cv.ApproxPoly(tmp, storage, cv.CV_POLY_APPROX_DP, value)
      if len(s) < 4:
        continue
      print("SEQUENCE")
      cv.FillConvexPoly(out, s, 255)
      for c in s:
        print(c)
    #cv.DrawContours(out, contour, cv.ScalarAll(255), cv.ScalarAll(100), 100)
    #cv.ShowImage(win_name, img)
    cv.ShowImage(win_name, out)

def segmentation(value):
  global storage, grey, level
  mask = -(1 << level)
  cv.SetImageROI(grey, (0, 0, grey.width & mask, grey.height & mask))
  out = cv.CloneImage(grey)
  #cv.Threshold(grey, grey, value, 255, cv.CV_THRESH_BINARY)
  contour = cv.PyrSegmentation(grey, out, storage, level, value, 30)
  if contour:
    cv.ShowImage(win_name, out)
    #for c in contour:
      #print(c)
    #cv.Zero(out)
    #cv.DrawContours(out, contour, cv.ScalarAll(255), cv.ScalarAll(100), 100)
    cv.ShowImage(win_name, out)

def threshold(value):
  binary = cv.CloneImage(grey)
  cv.Threshold(grey, binary, value, 255, cv.CV_THRESH_BINARY_INV)
  cv.ShowImage(win_name, binary)

def canny():
  cv.NamedWindow("orig", cv.CV_WINDOW_AUTOSIZE)
  cv.ShowImage("orig", img)
  binary = cv.CloneImage(grey)
  cv.Threshold(grey, binary, 200, 255, cv.CV_THRESH_BINARY_INV)
  cv.ShowImage(win_name, binary)
  cv.WaitKey(0)
  cv.Canny(grey, grey, 10, 100, 3);
  cv.ShowImage(win_name, grey)

#cv.CreateTrackbar(win_name, "Contours", 0, 255, segmentation)
#cv.CreateTrackbar(win_name, "Contours", 0, 255, track)
#cv.NamedWindow("orig", cv.CV_WINDOW_AUTOSIZE)
#cv.ShowImage("orig", img)
#track(15)
cv.CreateTrackbar("Threshold", win_name, 0, 255, threshold)
#canny()
cv.WaitKey(0)
cv.DestroyWindow(win_name)
