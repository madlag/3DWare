from solid import *
from solid.utils import *  # Not required, but the utils module is useful
import robothead_mount

PLATE_WIDTH = 2

SEGMENTS = 40

RASP_TOTAL_X=85.5
RASP_TOTAL_Y=57
RASP_TOTAL_Z=20

AIR_HOLE_NUMBER=6
AIR_HOLE_DIAMETER=2

BASE_PLATE_ENTRETOISE_RADIUS=3
RASP_HOLE_RADIUS=2.9 / 2.0
BASE_PLATE_HOLE_RADIUS=RASP_HOLE_RADIUS
ENTRETOISE_HEIGHT = 7
BASE_PLATE_ENTRETOISES = [[25.5,   18, ENTRETOISE_HEIGHT / 2.0],
                          [  25.5, 43.5, ENTRETOISE_HEIGHT / 2.0],
                          [  79, 43.5, ENTRETOISE_HEIGHT / 2.0],
                          [  77, 10, ENTRETOISE_HEIGHT / 2.0],
                          ]


CALE_HEIGHT=3
CALE_WIDTH=3
CALE_H_LENGTH=10
CALE_V_LENGTH=CALE_H_LENGTH + CALE_WIDTH
H_CALES = [[0, -CALE_WIDTH,0],
           [RASP_TOTAL_X - CALE_H_LENGTH, -CALE_WIDTH,0],
           [RASP_TOTAL_X - CALE_H_LENGTH, RASP_TOTAL_Y,0],
           [0, RASP_TOTAL_Y,0],
          ]

V_CALES = [[-CALE_WIDTH , RASP_TOTAL_Y - CALE_V_LENGTH + CALE_WIDTH,0],
           [RASP_TOTAL_X, RASP_TOTAL_Y - CALE_V_LENGTH + CALE_WIDTH,0],
          ]

HDMI_PORT_X_SHIFT = 45;
USB_PORT_Y_SHIFT = 30;
HDMI_HEIGHT = 15
USB_HEIGHT = 15

def cable_output():
   hdmi = translate([HDMI_PORT_X_SHIFT, -70, ENTRETOISE_HEIGHT + HDMI_HEIGHT / 2]) (
      cube([25,150, HDMI_HEIGHT], center = True)
   )
   usb = translate([170, USB_PORT_Y_SHIFT, ENTRETOISE_HEIGHT + USB_HEIGHT / 2])(
      cube([150,25, USB_HEIGHT], center = True)
   )
   return hdmi + usb


def entretoise (r_outer, r_inner, h, center = False):
  return cylinder(r=r_outer, h=h, center = center) - cylinder(r=r_inner, h=h * 2, center = center)

def air_holes():
  return translate([40,30, 0])(
      [
        rotate(i  * 360 / AIR_HOLE_NUMBER, [0, 0, 1])
        (
              translate([0, 10, 0])
              (
                  cylinder(r=AIR_HOLE_DIAMETER, h=10,  center = True)
              )
        )
        for i in range(6)
      ]
    )

def h_cale(i):
  return translate(i) (
    cube([CALE_H_LENGTH, CALE_WIDTH, ENTRETOISE_HEIGHT + CALE_HEIGHT], center = False)
  )


def v_cale(i):
  return translate(i) (
    cube([CALE_WIDTH, CALE_V_LENGTH, ENTRETOISE_HEIGHT + CALE_HEIGHT], center = False)
  )

def raspberry_case(holes):
  holes = air_holes() + cable_output()
  entretoises = [translate(i)
                 (entretoise(BASE_PLATE_ENTRETOISE_RADIUS, BASE_PLATE_HOLE_RADIUS, h = ENTRETOISE_HEIGHT, center=True))
                 for i in BASE_PLATE_ENTRETOISES]

  h_cales = [h_cale(i) for i in H_CALES ]
  v_cales = [v_cale(i) for i in V_CALES ]

  return union()(entretoises + h_cales + v_cales) + hole()(holes)

def y_nervure(y_size, x_shift):
   return up(PLATE_WIDTH)(right(x_shift)(cube([PLATE_WIDTH, y_size,PLATE_WIDTH])))
   
def x_nervure(x_size, y_shift):
   return left(x_size / 2.0)(up(PLATE_WIDTH)(forward(y_shift)(cube([x_size,PLATE_WIDTH,PLATE_WIDTH]))))


if __name__ == '__main__':
    M = 20
    CASE_X_SIZE = 140
    CASE_Y_SIZE = 110
    CASE_HEIGHT = RASP_TOTAL_Z + ENTRETOISE_HEIGHT + 5
    case_width = PLATE_WIDTH
    outer_case  = cube([CASE_X_SIZE - M * 2, CASE_Y_SIZE - M * 2, CASE_HEIGHT])

    outer_case = minkowski()(outer_case, cylinder(r=M, h=0.01))
      
    inner_case = translate([0,0,case_width])(cube([CASE_X_SIZE - M * 2, CASE_Y_SIZE- M * 2, CASE_HEIGHT  + 10]))
    inner_case = minkowski()(inner_case, cylinder(r=M - case_width, h=0.01))

    outer_case -= inner_case
    outer_case = translate([+M, M, 0])(outer_case)
    
#    outer_case = minkowski()(outer_case, cylinder(r = 1, h = 1))
    holes = union()(robothead_mount.rasp_holes())

    HOLES_Y_SHIFT = robothead_mount.RASP_HOLE_MARGIN - robothead_mount.RASP_HOLE_X_SHIFT
    holes = translate([CASE_X_SIZE / 2, HOLES_Y_SHIFT, -50])(rotate(90, [0,0,1])(holes))

    RASP_X_SHIFT = 30
    RASP_Y_SHIFT = 20
    a = outer_case + translate([RASP_X_SHIFT, RASP_Y_SHIFT])(rotate(0)(raspberry_case(holes)))
    a += hole()(holes)

    HEAD_HOLE_X_SIZE = 42
    HEAD_HOLE_Y_SIZE = 30

    a = left(CASE_X_SIZE / 2.0)(a)
    
    head_hole = cube([HEAD_HOLE_X_SIZE, HEAD_HOLE_Y_SIZE, 100], center = True)
    a += hole()(head_hole)
    n = y_nervure(CASE_Y_SIZE, HEAD_HOLE_X_SIZE / 2.0)
    a += n
    a += robothead_mount.x_symetry(n)

    n = x_nervure(CASE_X_SIZE - 2, HEAD_HOLE_Y_SIZE / 2.0)
    a += n
    
    n = x_nervure(CASE_X_SIZE - 2, RASP_X_SHIFT + RASP_TOTAL_Y)
    a += n
    
    scad_render_to_file( a, "scad/raspberry_pi_case.scad", file_header='$fn = %s;' % SEGMENTS, include_orig_code=True)
