import raspberry_case
from solid import *
from solid.utils import *  # Not required, but the utils module is useful

SEGMENTS = 100

BASE_Y_LEN=58
PLATE_WIDTH=2
FRONT_X_SHIFT=25
BACK_X_SHIFT=15
BASE_X_LEN=65
SUPPORT_X_LEN=BASE_X_LEN - FRONT_X_SHIFT - BACK_X_SHIFT

REINFORCE_WIDTH=5

RASP_PLATE_HEIGHT=28
RASP_PLATE_X_SHIFT=20

SERVO_HEAD_DIAMETER = 24.5 # 24.5
SERVO_HEAD_DIAMETER_MARGIN = 3.5
HOLE_FRONT_X_SHIFT=16.5
HOLE_FRONT_Y_SHIFT=10
HOLE_BACK_X_SHIFT=32.5
HOLE_BACK_Y_SHIFT=10
HOLE_RADIUS=1.75
RASP_HOLE_MARGIN=5
RASP_HOLE_X_SHIFT=RASP_PLATE_X_SHIFT + BACK_X_SHIFT + RASP_HOLE_MARGIN
RASP_HOLE_X_SHIFT_BACK=RASP_HOLE_X_SHIFT + 15
RASP_HOLE_Y_SHIFT=25
RASP_HOLE_RADIUS=1.75

RASP_PLATE_CUT_Y_LEN=40

def parallelogram(w,h, skew, plate_width):
  return linear_extrude(height = plate_width)(
      polygon(points=[[0,0], [w,0], [w + skew, h], [skew,h], [0,0]], paths=[[0,1,2,3]])
  )


def y_symetry(obj):
  return scale([1,-1,1])(obj)

def x_symetry(obj):
  return scale([-1,1,1])(obj)

RASP_FIX_PLATE_WIDTH=3

def rasp_holes():
  return [
    translate([RASP_HOLE_X_SHIFT, -RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    ),

    translate([RASP_HOLE_X_SHIFT, RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    ),


    translate([RASP_HOLE_X_SHIFT_BACK, -RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    ),

    translate([RASP_HOLE_X_SHIFT_BACK, RASP_HOLE_Y_SHIFT, 55]) (
        cylinder(r = RASP_HOLE_RADIUS, h = 80, center = True)
    )]


def head_mount():
  base = left(FRONT_X_SHIFT)(forward(-BASE_Y_LEN / 2.0)
                             (cube([BASE_X_LEN, BASE_Y_LEN, PLATE_WIDTH])))

  p = parallelogram(SUPPORT_X_LEN,
                    RASP_PLATE_HEIGHT,
                    RASP_PLATE_X_SHIFT,
                    PLATE_WIDTH)
  p = rotate([90,0,0]) (p)
  
  rear_reinforce_l = back(BASE_Y_LEN / 2.0) (p)

  # reinforce elements on base plate
  p2 = parallelogram(SUPPORT_X_LEN,
                     RASP_PLATE_HEIGHT / 4.0,
                     RASP_PLATE_X_SHIFT / 4.0,
                     BASE_Y_LEN)
  p2 = rotate([90,0,0]) (p2)
  rear_reinforce_base = p2
  rear_reinforce_base = forward(BASE_Y_LEN / 2.0)(rear_reinforce_base)

  # cut in p2
  p3 = parallelogram(SUPPORT_X_LEN,
                     RASP_PLATE_HEIGHT / 3.9,
                     RASP_PLATE_X_SHIFT / 3.9,
                     BASE_Y_LEN - REINFORCE_WIDTH * 2.0)
  p3 = rotate([90,0,0])(p3)
  # do the cut p2 - p3
  rear_reinforce_base -= forward(BASE_Y_LEN / 2.0 - REINFORCE_WIDTH)(left(REINFORCE_WIDTH)(p3))

  # Total reinforce elements on base plate
  rear_reinforce = rear_reinforce_l + y_symetry(rear_reinforce_l)

  rear_reinforce = right(BACK_X_SHIFT)(rear_reinforce + rear_reinforce_base)

  # raspberry pi fixation plate
  rasp_plate = right(BACK_X_SHIFT + RASP_PLATE_X_SHIFT)(forward(-BASE_Y_LEN / 2.0 - PLATE_WIDTH)
                                   (cube([SUPPORT_X_LEN, BASE_Y_LEN + 2 * PLATE_WIDTH, PLATE_WIDTH])))

  rasp_plate = up(RASP_PLATE_HEIGHT)(rasp_plate)

  rasp_plate_cut = translate([BACK_X_SHIFT, -RASP_PLATE_CUT_Y_LEN / 2,0]) (cube([SUPPORT_X_LEN * 2 + RASP_PLATE_X_SHIFT, RASP_PLATE_CUT_Y_LEN, 40]))
  
  rasp_plate -= rasp_plate_cut

  servo_hole = up(5)(cylinder(r = (SERVO_HEAD_DIAMETER + SERVO_HEAD_DIAMETER_MARGIN)/ 2.0, h = 100, center = True))

  front_hole_a = translate([-HOLE_FRONT_X_SHIFT,0, 5]) (
        cylinder(r = HOLE_RADIUS, h = 100, center = True)
    )
  front_hole_b = translate([-HOLE_FRONT_X_SHIFT,HOLE_FRONT_Y_SHIFT, 5]) (
        cylinder(r = HOLE_RADIUS, h = 100, center = True)
    )

  back_hole_a = translate([HOLE_BACK_X_SHIFT,0, 5]) (
        cylinder(r = HOLE_RADIUS, h = 20, center = True)
    )
  back_hole_b = translate([HOLE_BACK_X_SHIFT,HOLE_BACK_Y_SHIFT, 5]) (
        cylinder(r = HOLE_RADIUS, h = 20, center = True)
    )

  head_mount = base + rear_reinforce + rasp_plate

  holes = front_hole_a + front_hole_b + servo_hole + back_hole_a + back_hole_b
  for r in rasp_holes():
    holes += r
    
  return head_mount - hole()(holes)


if __name__ == '__main__':
    a = head_mount()
    scad_render_to_file( a, "scad/robothead_mount.scad", file_header='$fn = %s;' % SEGMENTS)
  
