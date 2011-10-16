#!/usr/bin/env python2
import cv, sys, numpy

def seqToList(cvseq):
  list = []
  while cvseq is not None:
    list.append(cvseq)
    cvseq = cvseq.h_next()
  return list

class Splitter:
  def __init__(self, filename):
    self.img = cv.LoadImage(filename)
    cv.ShowImage("orig", self.img)
    self.grey = cv.CreateImage(cv.GetSize(self.img), 8, 1)
    cv.CvtColor(self.img, self.grey, cv.CV_BGR2GRAY)
    self.font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0)
    self.changeContourMethod()
    self.registerKeys()

  def registerKeys(self):
    self.keys = {}
    self.keys[27] = self.keys[10] = lambda : sys.exit(0) # ESC or ENTER
    self.keys[190] = lambda : self.changeContourMethod() # F1

  def loop(self):
    while True:
      key = cv.WaitKey(10)
      if key == -1: continue
      key = key % 256
      if key in self.keys:
        self.keys[key]()
      else:
        print key, chr(key)
        sys.stdout.flush()
        

  def test(self, method, min=0, to=100, init=0, step=1):
    name = method.__name__
    setattr(self, '_test_' + name, True)
    cv.NamedWindow(name, cv.CV_WINDOW_AUTOSIZE)
    range = (to - min) / step
    cv.CreateTrackbar(name, name, init, range, lambda v: self.testValue(method, v * step + min))
    self.testValue(method, init)

  def testValue(self, method, value):
    img = method(value)
    cv.PutText(img, str(value), (10, 20), self.font, 255)
    cv.ShowImage(method.__name__, img)

  def changeContourMethod(self):
    if not hasattr(self, 'contourMethod'):
      self.contourMethod = 0
      self.contourMethods = [
        (cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_CODE, 'chain_code'),
        (cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_NONE, 'approx_none'),
        (cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE, 'approx_simple'),
        (cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_TC89_L1, 'tc89_l1'),
        (cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_TC89_KCOS, 'tc89_kcos'),
        (cv.CV_RETR_LIST, cv.CV_LINK_RUNS, 'link_runs')
      ]
    self.contourMethod = (self.contourMethod + 1) % len(self.contourMethods)
    if hasattr(self, '_test_findContours'): self.testValue(self.findContours, self._lastTrackValue)

  def plausiblePhoto(self, contour):
    if len(contour) < 4: return False
    center, size, angle = cv.MinAreaRect2(contour)
    if size[0] < size[1]: size = (size[1], size[0])
    if size[1] < 0.001 : return False
    ratio = size[0] / size[1]
    if ratio > 2.5: return False
    return True

  def findContours(self, value):
    self._lastTrackValue = value
    out = self.adaptiveThreshold(value)
    method = self.contourMethods[self.contourMethod]
    storage = cv.CreateMemStorage()
    contour = cv.FindContours(out, storage, method[0], method[1])
    out = cv.CloneImage(self.img)
    cv.PutText(out, method[2], (50, 20), self.font, (255, 0, 0))
    if contour:
      contours = [( cv.ContourArea(x), x ) for x in seqToList(contour) if self.plausiblePhoto(x)]
      area_max = max([a for (a, s) in contours])
      contours = [c for (a, c) in contours if area_max / a < 10]
      for contour in contours:
        self.processContour(contour, out)
    return out

  def processContour(self, contour, img):
    storage = cv.CreateMemStorage()
    box = (center, size, angle) = cv.MinAreaRect2(contour)
    mat = cv.CreateMat(2, 3, cv.CV_32F)
    cv.GetRotationMatrix2D(center, angle, 1.0, mat)
    out = cv.CloneImage(img)
    cv.WarpAffine(img, out, mat)
    points = [(int(x[0]), int(x[1])) for x in cv.BoxPoints(box)]
    cv.PolyLine(img, [points], True, (0, 255, 0))
    cv.ShowImage("HALO", out)
    cv.ShowImage("IMG", img)
    cv.WaitKey(0)

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
    if value < 3: value = 3
    if value % 2 == 0: value += 1
    binary = cv.CloneImage(self.grey)
    cv.AdaptiveThreshold(binary, binary, 255, cv.CV_ADAPTIVE_THRESH_MEAN_C, cv.CV_THRESH_BINARY_INV, value)
    #cv.AdaptiveThreshold(grey, binary, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY_INV, value)
    return binary

  def canny(self, t1 = 10, t2 = 100):
    can = cv.CloneImage(self.grey)
    cv.Canny(can, can, t1, t2, 3);
    return can

#cv.CreateTrackbar(win_name, "Contours", 0, 255, segmentation)
#cv.CreateTrackbar(win_name, "Contours", 0, 255, findContours)
#findContours(15)
filename = sys.argv[1] if len(sys.argv) > 1 else "small1.jpg"
splitter = Splitter(filename)
#splitter.test(splitter.adaptiveThreshold, 3, 100, 3, 2)
#splitter.test(splitter.threshold, 1, 255, 240)
#splitter.test(splitter.canny, 1, 255, 240)
#splitter.test(splitter.segmentation, 1, 255, 240)
splitter.test(splitter.findContours, 3, 255, 240)
splitter.loop()
