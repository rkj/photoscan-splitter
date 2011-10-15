#!/usr/bin/env python2
import cv, sys
class Splitter:
  def __init__(self, filename):
    self.img = cv.LoadImage(filename)
    cv.ShowImage("orig", self.img)
    self.grey = cv.CreateImage(cv.GetSize(self.img), 8, 1)
    cv.CvtColor(self.img, self.grey, cv.CV_BGR2GRAY)
    self.font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0)

  def test(self, method, min=0, to=100, init=0, step=1):
    name = method.__name__
    cv.NamedWindow(name, cv.CV_WINDOW_AUTOSIZE)
    range = (to - min) / step
    cv.CreateTrackbar(name, name, init, range, lambda v: self.testValue(method, v * step + min))
    self.testValue(method, init)

  def testValue(self, method, value):
    img = method(value)
    cv.PutText(img, str(value), (10, 20), self.font, 255)
    cv.ShowImage(method.__name__, img)

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

  # not working at all
  def segmentation(self, value):
    storage = cv.CreateMemStorage(1000)
    level = 3
    mask = -(1 << level)
    grey = self.grey
    cv.SetImageROI(grey, (0, 0, grey.width & mask, grey.height & mask))
    out = cv.CloneImage(grey)
    grey = self.adaptiveThreshold(31)
    contour = cv.PyrSegmentation(grey, out, storage, level, value, 30)
    if contour:
      for c in contour:
        area, color, rect = c
        cv.Rectangle(out, rect[0:2], rect[2:4], 100, 3, cv.CV_AA)
    return out

  def threshold(self, value):
    binary = cv.CloneImage(self.grey)
    cv.Threshold(binary, binary, value, 255, cv.CV_THRESH_BINARY_INV)
    return binary

  def adaptiveThreshold(self, value):
    binary = cv.CloneImage(self.grey)
    cv.AdaptiveThreshold(binary, binary, 255, cv.CV_ADAPTIVE_THRESH_MEAN_C, cv.CV_THRESH_BINARY_INV, value)
    #cv.AdaptiveThreshold(grey, binary, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY_INV, value)
    return binary

  def canny(self, t1 = 10, t2 = 100):
    can = cv.CloneImage(self.grey)
    cv.Canny(can, can, t1, t2, 3);
    return can

#cv.CreateTrackbar(win_name, "Contours", 0, 255, segmentation)
#cv.CreateTrackbar(win_name, "Contours", 0, 255, track)
#track(15)
filename = sys.argv[1] if len(sys.argv) > 1 else "small1.jpg"
splitter = Splitter(filename)
#splitter.test(splitter.adaptiveThreshold, 3, 100, 3, 2)
#splitter.test(splitter.threshold, 1, 255, 240)
#splitter.test(splitter.canny, 1, 255, 240)
#splitter.test(splitter.segmentation, 1, 255, 240)
cv.WaitKey(0)
