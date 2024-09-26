# CMPE 365 Assignment 1
# Building a convex Hull
# By: Jack Switzer (20333026) & Andrea Dovale-Puig ()

# Convex hull
#
# Usage: python main.py [-d] [-np] file_of_points
#
#   -d sets the 'discardPoints' flag
#   -np removes pauses
#
# You can press ESC in the window to exit.
#
# You'll need Python 3 and must install these packages:
#
#   PyOpenGL, GLFW
import sys
import site
sys.path.append(site.getsitepackages()[0])

print(sys.executable)
print(sys.path)



import sys, os, math

try: # PyOpenGL
  from OpenGL.GL import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(0)



# Globals

window = None

windowWidth  = 1000 # window dimensions
windowHeight = 1000

minX = None # range of points
maxX = None
minY = None
maxY = None

r  = 0.01 # point radius as fraction of window size

numAngles = 32
thetas = [ i/float(numAngles)*2*3.14159 for i in range(numAngles) ] # used for circle drawing

allPoints = [] # list of points

lastKey = None  # last key pressed

discardPoints = False
addPauses = True

# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__( self, coords ):

      self.x = float( coords[0] ) # coordinates
      self.y = float( coords[1] )

      self.ccwPoint = None # point CCW of this on hull
      self.cwPoint  = None # point CW of this on hull

      self.highlight = False # to cause drawing to highlight this point


    def __repr__(self):
      return 'pt(%g,%g)' % (self.x, self.y)


    def drawPoint(self):

      # Highlight with yellow fill
      
      if self.highlight:
          glColor3f( 0.9, 0.9, 0.4 )
          glBegin( GL_POLYGON )
          for theta in thetas:
              glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
          glEnd()

      # Outline the point
      
      glColor3f( 0, 0, 0 )
      glBegin( GL_LINE_LOOP )
      for theta in thetas:
          glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
      glEnd()

      # Draw edges to next CCW and CW points.

      if self.ccwPoint:
        glColor3f( 0, 0, 1 )
        drawArrow( self.x, self.y, self.ccwPoint.x, self.ccwPoint.y )

      if self.ccwPoint:
        glColor3f( 1, 0, 0 )
        drawArrow( self.x, self.y, self.cwPoint.x, self.cwPoint.y )



# Draw an arrow between two points, offset a bit to the right

def drawArrow( x0,y0, x1,y1 ):

    d = math.sqrt( (x1-x0)*(x1-x0) + (y1-y0)*(y1-y0) )

    vx = (x1-x0) / d      # unit direction (x0,y0) -> (x1,y1)
    vy = (y1-y0) / d

    vpx = -vy             # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5*r*vx - 0.4*r*vpx # arrow tail
    ya = y0 + 1.5*r*vy - 0.4*r*vpy

    xb = x1 - 1.5*r*vx - 0.4*r*vpx # arrow head
    yb = y1 - 1.5*r*vy - 0.4*r*vpy

    xc = xb - 2*r*vx + 0.5*r*vpx # arrow outside left
    yc = yb - 2*r*vy + 0.5*r*vpy

    xd = xb - 2*r*vx - 0.5*r*vpx # arrow outside right
    yd = yb - 2*r*vy - 0.5*r*vpy

    glBegin( GL_LINES )
    glVertex2f( xa, ya )
    glVertex2f( xb, yb )
    glEnd()

    glBegin( GL_POLYGON )
    glVertex2f( xb, yb )
    glVertex2f( xc, yc )
    glVertex2f( xd, yd )
    glEnd()
      
      

# Determine whether three points make a left or right turn

LEFT_TURN  = 1
RIGHT_TURN = 2
COLLINEAR  = 3

def turn( a, pointB, pointC ):

    det = (a.x-pointC.x) * (pointB.y-pointC.y) - (pointB.x-pointC.x) * (a.y-pointC.y)

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# Build a convex hull from a set of point
#
# Use the method described in class


def buildHull( points ):

    # Check cases

    if len(points) == 3:

        # Base case of 3 points: make a hull
        
        pointA, pointB, pointC = points # extract 3 points: a, b, & c
        
        # Determine the turn direction of points in sequence (a, b, c)
        turnDirection = turn(pointA, pointB, pointC)
        
        if turnDirection == LEFT_TURN:
            # Set CCW and CW pointers for a left turn
            pointA.ccwPoint, pointA.cwPoint = pointB, pointC
            pointB.ccwPoint, pointB.cwPoint = pointC, pointA
            pointC.ccwPoint, pointC.cwPoint = pointA, pointB
        elif turnDirection == RIGHT_TURN:
            # Set CCW and CW pointers for a right turn, reverse of above
            pointA.ccwPoint, pointA.cwPoint = pointC, pointB
            pointB.ccwPoint, pointB.cwPoint = pointA, pointC
            pointC.ccwPoint, pointC.cwPoint = pointB, pointA
        else:
            # Points are collinear, assuming a sorted array makes point b the middle point
            pointA.cwPoint = pointB, pointA.ccwPoint = pointB
            pointB.cwPoint = pointA, pointB.ccwPoint = pointC
            pointC.cwPoint = pointB, pointC.ccwPoint = pointB

        # Flag all points as hull points
        pointA.isHullPoint, pointB.isHullPoint, pointC.isHullPoint = True, True, True
        
        pass # should be unncessary, but keeping from starter code just in case

    elif len(points) == 2:

        # Base case of 2 points: make a hull

        pointA, pointB = points # extract both points a & b
        
        # Set CCW and CW pointers for both points, degenerate hull (line segment)
        pointA.ccwPoint, pointA.cwPoint = pointB, pointB
        pointB.ccwPoint, pointB.cwPoint = pointA, pointA
        
        # Flag both points as hull points
        pointA.isHullPoint, pointB.isHullPoint = True, True

        pass # should be unncessary, but keeping from starter code just in case

    else:

        # Recurse to build left and right hull

        # Step 1: Divide the points into left and right halves
        mid = len(points) // 2
        leftPoints = points[:mid]
        rightPoints = points[mid:]

        # Step 2: Recursively build the left and right hulls
        leftHull = buildHull(leftPoints)
        rightHull = buildHull(rightPoints)

        # Debug: Highlight points and display
        for p in points:
            p.highlight = True
        display(wait=addPauses)

        # Step 3: Merge the two hulls - implementing in main body, could be a nested function but not important
        mergedHull = mergeHulls(leftHull, rightHull)

        # Debug: Highlight points and display
        for p in points:
            p.highlight = True
        display(wait=addPauses)

        # Pause to see the result, then remove the highlighting from
        # the points that you previously highlighted:
        display(wait=addPauses)
        for p in points:
            p.highlight = False

    # At the very end of buildHull(), you should display the result
    # after every merge, as shown below.  This call to display() does
    # not pause.
    display()

  

windowLeft   = None
windowRight  = None
windowTop    = None
windowBottom = None


# merge two convex Hulls, following the aproach described in class
def mergeHulls(leftHull, rightHull):
    # Flag all points in the left and right hulls as non hull points
    for pointA, pointB in zip(leftHull, rightHull):
        pointA.isHullPoint, pointB.isHullPoint = False, False

    # Next find upper hull points
    leftMostPoint = min(leftHull, key=lambda p: p.x) # find right most point of the left hull
    rightMostPoint = max(rightHull, key=lambda p: p.x) # find left most point of the right hull

    # Initialize var's for storing tangent points
    upperLeft, upperRight, lowerLeft, lowerRight = None, None, None, None

    # Find Upper and Lower Tangents
    for isUpper in [True, False]:
        leftPoint, rightPoint = leftMostPoint, rightMostPoint # start with left and right most points
        while True:
            if isUpper: 
                # Finding upper tangent
                if turn(leftPoint, rightPoint, rightPoint.cwPoint) == LEFT_TURN:
                    rightPoint = rightPoint.cwPoint
                    updated = True
                elif turn(rightPoint, leftPoint, leftPoint.ccwPoint) == RIGHT_TURN:
                    leftPoint = leftPoint.ccwPoint
                    updated = True
            else:
                # Finding lower tangent
                if turn(leftPoint, rightPoint, rightPoint.ccwPoint) == RIGHT_TURN:
                    rightPoint = rightPoint.ccwPoint
                    updated = True
                elif turn(rightPoint, leftPoint, leftPoint.cwPoint) == LEFT_TURN:
                    leftPoint = leftPoint.cwPoint
                    updated = True
            if not updated:
                break
        # Store the found tangent points based on whether we're finding the upper or lower tangent
        if isUpper:
            # For the upper tangent, store the leftmost and rightmost points
            upperLeft, upperRight = leftPoint, rightPoint
        else:
            # For the lower tangent, store the leftmost and rightmost points
            lowerLeft, lowerRight = leftPoint, rightPoint

    # Merge Hulls by updating cw and ccw pointers
    upperLeft.cwPoint, upperRight.ccwPoint = upperRight, upperLeft
    lowerLeft.ccwPoint, lowerRight.cwPoint = lowerRight, lowerLeft

    # Traverse the merged hull setting isHullPoint = True
    while True:
        currentPoint.isHullPoint = True
        currentPoint = currentPoint.cwPoint
        if currentPoint == upperLeft:
            break

    # Check all points in the left and right hulls and remove hull pointers if they are not on the hull
    for point in leftHull + rightHull:
        if not point.isHullPoint:
            point.ccwPoint, point.cwPoint = None, None


# Set up the display and draw the current image

def display( wait=False ):

    global lastKey, windowLeft, windowRight, windowBottom, windowTop
    
    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor( 1,1,1,0 )
    glClear( GL_COLOR_BUFFER_BIT )
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()

    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    if maxX-minX > maxY-minY: # wider point spread in x direction
        windowLeft = -0.1*(maxX-minX)+minX
        windowRight = 1.1*(maxX-minX)+minX
        windowBottom = windowLeft
        windowTop    = windowRight
    else: # wider point spread in y direction
        windowTop    = -0.1*(maxY-minY)+minY
        windowBottom = 1.1*(maxY-minY)+minY
        windowLeft   = windowBottom
        windowRight  = windowTop

    glOrtho( windowLeft, windowRight, windowBottom, windowTop, 0, 1 )

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers( window )

    # Maybe wait until the user presses 'p' to proceed
    
    if wait:

        sys.stderr.write( 'Press "p" to proceed ' )
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80 and lastKey != glfw.KEY_ESCAPE: # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write( '\r                     \r' )
        sys.stderr.flush()

        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

    global lastKey
    
    if action == glfw.PRESS:
        lastKey = key



# Handle window reshape


def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight



# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    if action == glfw.PRESS:

        # Find point under mouse

        x,y = glfw.get_cursor_pos( window ) # mouse position

        wx = (x-0)/float(windowWidth)  * (windowRight-windowLeft) + windowLeft
        wy = (windowHeight-y)/float(windowHeight) * (windowTop-windowBottom) + windowBottom

        minDist = windowRight-windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt( (p.x-wx)*(p.x-wx) + (p.y-wy)*(p.y-wy) )
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print( minPoint )

        
    
# Initialize GLFW and run the main event loop

def main():

    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints, addPauses
    
    # Check command-line args
    
    if len(sys.argv) < 2:
        print( 'Usage: %s filename' % sys.argv[0] )
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        if args[0] == '-d':
            discardPoints = True
        elif args[0] == '-np':
            addPauses = False
        args = args[1:]

    # Set up window
  
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )
    glfw.swap_interval( 1 )
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # Read the points

    with open( args[0], 'rb' ) as f:
      allPoints = [ Point( line.split(b' ') ) for line in f.readlines() ]

    # Get bounding box of points

    minX = min( p.x for p in allPoints )
    maxX = max( p.x for p in allPoints )
    minY = min( p.y for p in allPoints )
    maxY = max( p.y for p in allPoints )

    # Adjust point radius in proportion to bounding box
    
    if maxX-minX > maxY-minY:
        r *= maxX-minX
    else:
        r *= maxY-minY

    # Sort by increasing x.  For equal x, sort by increasing y.
    
    allPoints.sort( key=lambda p: (p.x,p.y) )

    # Run the code
    
    buildHull( allPoints )

    # Wait to exit

    while not glfw.window_should_close( window ):
        glfw.wait_events()
        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    glfw.destroy_window( window )
    glfw.terminate()
    


if __name__ == '__main__':
    main()
