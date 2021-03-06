# coding: utf-8

# Gestures for Pythonista
# Copied from https://github.com/mikaelho/pythonista-gestures
# As its author said, this is a convenience class for enabling gestures in Pythonista ui applications, 
# including built-in views. Main intent here has been to make them Python friendly,
# hiding all the Objective-C stuff.

import ui
from objc_util import *
import uuid

# https://developer.apple.com/library/prerelease/ios/documentation/UIKit/Reference/UIGestureRecognizer_Class/index.html#//apple_ref/occ/cl/UIGestureRecognizer

class Gestures():

  TAP = b'UITapGestureRecognizer'
  PINCH = b'UIPinchGestureRecognizer'
  ROTATION = b'UIRotationGestureRecognizer'
  SWIPE = b'UISwipeGestureRecognizer'
  PAN = b'UIPanGestureRecognizer'
  SCREEN_EDGE_PAN = b'UIScreenEdgePanGestureRecognizer'
  LONG_PRESS = b'UILongPressGestureRecognizer'

  POSSIBLE = 0
  BEGAN = 1
  RECOGNIZED = 1
  CHANGED = 2
  ENDED = 3
  CANCELLED = 4
  FAILED = 5

  RIGHT = 1
  LEFT = 2
  UP = 4
  DOWN = 8

  EDGE_NONE = 0
  EDGE_TOP = 1
  EDGE_LEFT = 2
  EDGE_BOTTOM = 4
  EDGE_RIGHT = 8
  EDGE_ALL = 15

  def __init__(self, retain_global_reference = True):
    self.buttons = {}
    self.views = {}
    self.recognizers = {}
    self.actions = {}
    if retain_global_reference:
      retain_global(self)

    # Friendly delegate functions

    def recognize_simultaneously_default(gr_name, other_gr_name):
      return False    
    self.recognize_simultaneously = recognize_simultaneously_default
    
    def fail_default(gr_name, other_gr_name):
      return False    
    self.fail = fail_default
    
    def fail_other_default(gr_name, other_gr_name):
      return False    
    self.fail_other = fail_other_default

    # ObjC delegate functions
    
    def simplify(func, gr, other_gr):
      gr_o = ObjCInstance(gr)
      other_gr_o = ObjCInstance(other_gr)
      if (gr_o.view() != other_gr_o.view()):
        return False
      gr_name = gr_o._get_objc_classname()
      other_gr_name = other_gr_o._get_objc_classname()
      return func(gr_name, other_gr_name)
    
    # Recognize simultaneously

    def gestureRecognizer_shouldRecognizeSimultaneouslyWithGestureRecognizer_(_self, _sel, gr, other_gr):
      return self.objc_should_recognize_simultaneously(self.recognize_simultaneously, gr, other_gr)

    def objc_should_recognize_simultaneously_default(func, gr, other_gr):
      return simplify(func, gr, other_gr)
      
    self.objc_should_recognize_simultaneously = objc_should_recognize_simultaneously_default
    
    # Fail other
    
    def gestureRecognizer_shouldRequireFailureOfGestureRecognizer_(_self, _sel, gr, other_gr):
      return self.objc_should_require_failure(self.fail_other, gr, other_gr)

    def objc_should_require_failure_default(func, gr, other_gr):
      return simplify(func, gr, other_gr)
      
    self.objc_should_require_failure = objc_should_require_failure_default
    
    # Fail
    
    def gestureRecognizer_shouldBeRequiredToFailByGestureRecognizer_(_self, _sel, gr, other_gr):
      return self.objc_should_fail(self.fail, gr, other_gr)

    def objc_should_fail_default(func, gr, other_gr):
      return simplify(func, gr, other_gr)
      
    self.objc_should_fail = objc_should_fail_default
    
    # Delegate
    
    try:
      PythonGestureDelegate = ObjCClass('PythonGestureDelegate')
    except:
      PythonGestureDelegate = create_objc_class('PythonistaGestureDelegate',
      superclass=NSObject,
      methods=[
        gestureRecognizer_shouldRecognizeSimultaneouslyWithGestureRecognizer_,
        gestureRecognizer_shouldRequireFailureOfGestureRecognizer_,
        gestureRecognizer_shouldBeRequiredToFailByGestureRecognizer_],
      classmethods=[],
      protocols=['UIGestureRecognizerDelegate'],
      debug=True)
    self._delegate = PythonGestureDelegate.new()

  @on_main_thread
  def add_tap(self, view, action, number_of_taps_required = None, number_of_touches_required = None):
    recog = self._get_recog('UITapGestureRecognizer', view, self._general_action, action)

    if number_of_taps_required:
      recog.numberOfTapsRequired = number_of_taps_required
    if number_of_touches_required:
      recog.numberOfTouchesRequired = number_of_touches_required

    return recog

  @on_main_thread
  def add_long_press(self, view, action, number_of_taps_required = None, number_of_touches_required = None, minimum_press_duration = None, allowable_movement = None):
    recog = self._get_recog('UILongPressGestureRecognizer', view, self._general_action, action)

    if number_of_taps_required:
      recog.numberOfTapsRequired = number_of_taps_required
    if number_of_touches_required:
      recog.numberOfTouchesRequired = number_of_touches_required
    if minimum_press_duration:
      recog.minimumPressDuration = minimum_press_duration
    if allowable_movement:
      recog.allowableMovement = allowable_movement

    return recog

  @on_main_thread
  def add_pan(self, view, action, minimum_number_of_touches = None, maximum_number_of_touches = None, set_translation = None):
    recog = self._get_recog('UIPanGestureRecognizer', view, self._pan_action, action)

    if minimum_number_of_touches:
      recog.minimumNumberOfTouches = minimum_number_of_touches
    if maximum_number_of_touches:
      recog.maximumNumberOfTouches = maximum_number_of_touches
    if set_translation:
      recog.set_translation_(CGPoint(set_translation.x, set_translation.y), ObjCInstance(view))

    return recog

  @on_main_thread
  def add_screen_edge_pan(self, view, action, edges = None):
    recog = self._get_recog('UIScreenEdgePanGestureRecognizer', view, self._pan_action, action)

    if edges:
      recog.edges = edges

    return recog

  @on_main_thread
  def add_pinch(self, view, action):
    recog = self._get_recog('UIPinchGestureRecognizer', view, self._pinch_action, action)

    return recog

  @on_main_thread
  def add_rotation(self, view, action):
    recog = self._get_recog('UIRotationGestureRecognizer', view, self._rotation_action, action)

    return recog

  @on_main_thread
  def add_swipe(self, view, action, direction = None, number_of_touches_required = None):
    recog = self._get_recog('UISwipeGestureRecognizer', view, self._general_action, action)

    if direction:
      combined_dir = direction
      if isinstance(direction, list):
        combined_dir = 0
        for one_direction in direction:
          combined_dir |= one_direction
      recog.direction = combined_dir
    if number_of_touches_required:
      recog.numberOfTouchesRequired = number_of_touches_required

    return recog

  @on_main_thread
  def remove(self, view, recognizer):
    key = None
    for id in self.recognizers:
      if self.recognizers[id] == recognizer:
        key = id
        break
    if key:
      del self.buttons[key]
      del self.views[key]
      del self.recognizers[key]
      del self.actions[key]
    ObjCInstance(view).removeGestureRecognizer_(recognizer)

  @on_main_thread
  def enable(self, recognizer):
    ObjCInstance(recognizer).enabled = True

  @on_main_thread
  def disable(self, recognizer):
    ObjCInstance(recognizer).enabled = False

  @on_main_thread
  def remove_all_gestures(self, view):
    gestures = ObjCInstance(view).gestureRecognizers()
    for recog in gestures:
      self.remove(view, recog)

  def _get_recog(self, recog_name, view, internal_action, final_handler):
    button = ui.Button()
    key = str(uuid.uuid4())
    button.name = key
    button.action = internal_action
    self.buttons[key] = button
    self.views[key] = view
    recognizer = ObjCClass(recog_name).alloc().initWithTarget_action_(button, sel('invokeAction:')).autorelease()
    self.recognizers[key] = recognizer
    self.actions[key] = final_handler
    ObjCInstance(view).addGestureRecognizer_(recognizer)
    recognizer.delegate = self._delegate
    return recognizer

  class Data():
    def __init__(self):
      self.recognizer = self.view = self.location = self.state = self.number_of_touches = self.scale = self.rotation = self.velocity = None

  def _context(self, button):
    key = button.name
    (view, recog, action) = (self.views[key], self.recognizers[key], self.actions[key])
    data = Gestures.Data()
    data.recognizer = recog
    data.view = view
    data.location = self._location(view, recog)
    data.state = recog.state()
    data.number_of_touches = recog.numberOfTouches()
    return (data, action)

  def _location(self, view, recog):
    loc = recog.locationInView_(ObjCInstance(view))
    return ui.Point(loc.x, loc.y)

  def _general_action(self, sender):
    (data, action) = self._context(sender)
    action(data)

  def _pan_action(self, sender):
    (data, action) = self._context(sender)

    trans = data.recognizer.translationInView_(ObjCInstance(data.view))
    vel = data.recognizer.velocityInView_(ObjCInstance(data.view))
    data.translation = ui.Point(trans.x, trans.y)
    data.velocity = ui.Point(vel.x, vel.y)

    action(data)

  def _pinch_action(self, sender):
    (data, action) = self._context(sender)

    data.scale = data.recognizer.scale()
    data.velocity = data.recognizer.velocity()

    action(data)

  def _rotation_action(self, sender):
    (data, action) = self._context(sender)

    data.rotation = data.recognizer.rotation()
    data.velocity = data.recognizer.velocity()

    action(data)

# TESTING AND DEMONSTRATION

if __name__ == "__main__":

  class EventDisplay(ui.View):
    def __init__(self):
      self.tv = ui.TextView(flex='WH')
      self.add_subview(self.tv)
      self.tv.frame = (0, 0, self.width, self.height)
      
      g = Gestures()
      
      g.recognize_simultaneously = lambda gr, other_gr: gr == Gestures.PAN and other_gr == Gestures.PINCH
        
      g.fail_other = lambda gr, other_gr: other_gr == Gestures.PINCH
  
      g.add_tap(self, self.general_handler)
  
      g.add_long_press(self.tv, self.long_press_handler)
  
      pan = g.add_pan(self, self.pan_handler)
  
      #g.add_screen_edge_pan(self.tv, self.pan_handler, edges = Gestures.EDGE_LEFT)
  
      #g.add_swipe(self.tv, self.general_handler, direction = [Gestures.DOWN])
  
      g.add_pinch(self, self.pinch_handler)
  
      #g.add_rotation(self.tv, self.rotation_handler)
  
    def t(self, msg):
      self.tv.text = self.tv.text + msg + '\n'
  
    def general_handler(self, data):
      self.t('General: ' + str(data.location) + ' - state: ' + str(data.state) + ' - touches: ' + str(data.number_of_touches))
  
    def long_press_handler(self, data):
      if data.state == Gestures.ENDED:
        self.t('Long press: ' + str(data.location) + ' - state: ' + str(data.state) + ' - touches: ' + str(data.number_of_touches))
  
    def pan_handler(self, data):
      self.t('Pan: ' + str(data.translation) + ' - state: ' + str(data.state))
  
    def pinch_handler(self, data):
      self.t('Pinch: ' + str(data.scale) + ' state: ' + str(data.state))
  
    def rotation_handler(self, data):
      self.t('Rotation: ' + str(data.rotation))

  view = EventDisplay()
  view.present()

