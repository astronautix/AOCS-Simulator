import sys
import os
sys.path.append(os.path.join(os.getcwd(), ".."))
import numpy as np
import trimesh
import loas

dt = 1/25 # Simulation time step
I0 = np.diag((200,200,200)) # Satellite inertia tensor

# load mesh object and resize it
mesh = trimesh.load_mesh("./satellite.stl")
bounds = np.array(mesh.bounds)
mesh.apply_translation(-(bounds[0] + bounds[1])/2) # center the satellite (the mass center should be on 0,0)
mesh.apply_scale(3) # rescale the model

satellite = loas.Satellite( mesh, dt, I0 = I0 )
viewer = loas.output.Viewer( satellite, 30 )
drag_torque = loas.SparseDrag( satellite, 1000, 1, 1, 6, viewer)
satellite.addParasiteTorque( drag_torque )

drag_torque.start() # starts the workers that computes the drag torque
satellite.start() # starts the satellite's simulation
viewer.run() # retuns only when viewer is closed

satellite.stop() # stops the satellite
drag_torque.stop() # stop drag_torque workers
satellite.join()
drag_torque.join()
