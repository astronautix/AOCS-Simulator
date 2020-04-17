import numpy as np
import loas
from threading import Thread
import time

class Satellite(Thread):

    """
    The satellite class, represents the simulated satellite itself.

    Stores the shape of the satellite, its mass properties, current attitude and angular velocity.

    Can be used directly as loas.Satellite
    """

    def __init__(
        self,
        mesh,
        dt = 1/30,
        M0 = np.array([[0.],[0.],[0.]]),
        dw0 = np.array([[0.],[0.],[0.]]),
        J0 = 1,
        B0 = np.array([[0.],[0.],[0.]]),
        I0 = np.array([[1.],[1.],[1.]]),
        L0 = np.array([[0.],[0.],[0.]]),
        Q0 = loas.Quaternion(1,0,0,0)
    ):
        """
        :param mesh: Mesh of the satellite
        :type mesh: trimesh.Trimesh
        :param dt: Time step of the simulation
        :type dt: float
        :param M0: Initial magnetic moment of the magnetorquer
        :type M0: (3,1) numpy array
        :param dw0: Initial rotation speed vector of the reaction wheels
        :type dw0: (3,1) numpy array
        :param J0: Inertia momentum of reaction wheel
        :type J0: float
        :param B0: Initial external magnetic field
        :type M0: (3,1) numpy array
        :param I0: Initial inertia matrix of the satellite
        :type I0: (3,1) numpy array
        :param L0: Initial angular momentum of the satellite
        :type L0: (3,1) numpy array
        :param Q0: Initial attitude of the satellite
        :type Q0: (3,1) numpy array
        """
        Thread.__init__(self)
        self.t = 0 #temps écoulé
        self.dt = dt
        self.Q = Q0 #quaternion de rotation de Rv par rapport à Rr
        self.L = L0 #Moment cinétique du satellite dans Rr
        self.M = M0 # moment magnétique des MC exprimé dans # REVIEW:
        self.dw = dw0 #vecteur accélération angulaire des RI exprimé dans Rv
        self.J = J0 #Moment d'inertie des RI
        self.B = B0 #Vecteur champ magnétique environnant, exprimé dans Rr
        self.I = I0 #Tenseur d'inertie du satellite exprimé dans Rv
        self.running = False,
        self.mesh = mesh

    def dQ(self,W): #renvoie la dérivée du quaternion
        """
        Gives the first derivative of the attitude quaternion

        :param W: Angular speed of the satellite
        :type W: (3,1) numpy array
        """
        qw,qx,qy,qz = self.Q[0],self.Q[1],self.Q[2],self.Q[3]
        expQ = np.array([[-qx, -qy, -qz],
                         [ qw,  qz, -qy],
                         [-qz,  qw,  qx],
                         [ qy, -qx,  qw]])
        return 1/2*np.dot(expQ,W)

    def dL(self): #renvoie la dérivée du moment cinétique avec le th du moment cinétique
        """
        Gives the first derivative of the angular momentum (uses dynamic equations)
        """
        C_Rv = np.cross(self.M, self.Q.R2V(self.B), axisa=0, axisb=0,axisc=0) - self.J*self.dw #couple dans Rv du au MC et aux RW
        C_Rr = self.Q.V2R(C_Rv)
        return C_Rr

    def getNextIteration(self):
        """
        Update the instance at the next simulation iteration
        """
        self.L += self.dL()*self.dt #calcul du nouveau moment cinétique
        W = self.Q.V2R(np.dot(np.linalg.inv(self.I),self.Q.R2V(self.L))) #Vecteur rotation du satellite dans Rr
        Qnump = self.Q.vec() + self.dQ(W)*self.dt #calcul de la nouvelle orientation
        Qnump /= np.linalg.norm(Qnump)
        self.Q = loas.Quaternion(*Qnump[:,0])
        self.t += self.dt
        return self.Q

    def setM(self, M):
        """
        Magnetorquer moment setter
        """
        self.M = M

    def setDW(self, dw):
        """
        Angular acceleration of reaction wheel setter
        """
        self.dw = dw

    def setB(self, B):
        """
        External magnetic field setter
        """
        self.B = B

    def stop(self):
        """
        Breaks the thread
        """
        self.running = False

    def run(self):
        """
        Launches the simulation in a thread
        """
        self.running = True
        while self.running:
            self.getNextIteration()
            time.sleep(self.dt)