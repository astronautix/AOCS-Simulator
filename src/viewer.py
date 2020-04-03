"""This script shows an example of using the PyWavefront module."""
import ctypes
import os
import numpy as np
from quaternion import Quaternion
import pyglet
from pyglet.gl import *
from pywavefront import visualization
import pywavefront


vehicle_line_length = 1.5
reference_line_length = 0.5

class Viewer(pyglet.window.Window):
    def __init__(self, modelFile, Qgetter, fps=30):
        super().__init__(resizable=True)

        self.fps = fps
        self.getQ = Qgetter
        self.Q = Quaternion(1,0,0,0)
        self.rotation = 0
        self.meshes = pywavefront.Wavefront(modelFile)
        self.lightfv = ctypes.c_float * 4


    def on_resize(self, width, height):
        viewport_width, viewport_height = self.get_framebuffer_size()
        glViewport(0, 0, viewport_width, viewport_height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., float(width)/height, 1., 100.)
        glMatrixMode(GL_MODELVIEW)
        return True


    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(-1.0, 1.0, 1.0, 0.0))
        #glDisable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glEnable(GL_DEPTH_TEST)

        glTranslated(0.0, 0.0, -3.0)

        glTranslated(-1.5,-1.5,0.)
        ref_axis = pyglet.graphics.Batch()
        ref_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,reference_line_length,0.,0.)),
            ('c3B', (255,0,0,255,0,0))
        )
        ref_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,0.,reference_line_length,0.)),
            ('c3B', (0,255,0,0,255,0))
        )
        ref_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,0.,0.,reference_line_length)),
            ('c3B', (0,0,255,0,0,255))
        )
        ref_axis.draw()
        glTranslated(1.5,1.5,0.)

        glRotatef(self.Q.angle()*180/3.14, *self.Q.axis())


        visualization.draw(self.meshes)

        sat_axis = pyglet.graphics.Batch()
        sat_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,vehicle_line_length,0.,0.)),
            ('c3B', (255,0,0,255,0,0))
        )
        sat_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,0.,vehicle_line_length,0.)),
            ('c3B', (0,255,0,0,255,0))
        )
        sat_axis.add(2, GL_LINES, None,
            ('v3f', (0.,0.,0.,0.,0.,vehicle_line_length)),
            ('c3B', (0,0,255,0,0,255))
        )
        sat_axis.draw()

    def update(self, dt):
        self.Q = self.getQ()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/self.fps)
        pyglet.app.run()
