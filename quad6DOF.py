# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 16:54:51 2017

@author: ctytl
"""

from pylab import *
import numpy as np
import scipy.linalg as splin


# Physical Constants
m = 0.1         #kg
Ixx = 0.00062   #kg-m^2
Iyy = 0.00113   #kg-m^2
Izz = 0.9*(Ixx + Iyy) #kg-m^2 (Assume nearly flat object, z=0)
dx = 0.114      #m
dy = 0.0825     #m
g = 9.81  #m/s/s
DTR = 1/57.3; RTD = 57.3
    
# Propeller Thrust function
def Fthrust(u):
    #Input: u (PWM)
    #Return: Thrust (Newtons)
    return 0.00128*u - 1.55
    
# Torque function
def T(F,dx,dy):
    # Returns torque about cg given thrust force and dx,dy distance from cg
    return 0


# Nonlinear Dynamics Equations of Motion
def f(x,u):
    #idx  0, 1, 2, 3, 4, 5, 6,  7,  8,  9,10,11
    #x = [u, v, w, p, q, r,phi,the,psi,xE,yE,hE]
    
    # Store values in a readable format
    ub = x[0]; vb = x[1]; wb = x[2]
    p = x[3]; q = x[4]; r = x[5]
    phi = x[6]; theta = x[7]; psi = x[8]
    xE = x[9]; yE = x[10]; hE = x[11]
    
    # Calculate forces from propeller inputs
    F1 = Fthrust(u[0])
    F2 = Fthrust(u[1])
    F3 = Fthrust(u[2])
    F4 = Fthrust(u[3])
    Fz = F1 + F2 + F3 + F4
    L = (F1 + F4)*dy - (F2 + F3)*dy
    M = (F1 + F3)*dx - (F2 + F4)*dx
    N = -T(F1,dx,dy) - T(F2,dx,dy) + T(F3,dx,dy) + T(F4,dx,dy)
    
    # Pre-calculate trig values
    cphi = cos(phi);   sphi = sin(phi)
    cthe = cos(theta); sthe = sin(theta)
    cpsi = cos(psi);   spsi = sin(psi)
    
    # Calculate the derivative of the state matrix using EOM
    xdot = zeros(12)
    xdot[0] = -g*sthe + r*vb - q*wb  # = udot
    xdot[1] = g*sphi*cthe - r*ub + p*wb # = vdot
    xdot[2] = 1/m*(-Fz) + g*cphi*cthe + q*ub - p*vb # = wdot
    xdot[3] = 1/Ixx*(L + (Iyy-Izz)*q*r)  # = pdot
    xdot[4] = 1/Iyy*(M + (Izz-Ixx)*p*r)  # = qdot
    xdot[5] = 1/Izz*(N + (Ixx-Iyy)*p*q)  # = rdot
    xdot[6] = p + (q*sphi + r*cphi)*sthe/cthe  # = phidot
    xdot[7] = q*cphi - r*sphi  # = thetadot
    xdot[8] = (q*sphi + r*cphi)/cthe  # = psidot
    xdot[9] = cthe*cpsi*xdot[0] + (-cthe*spsi+sphi*sthe*cpsi)*x[1] +\
        (sphi*spsi+cphi*sthe*cpsi)*xdot[2]  # = xEdot
    xdot[10] = cthe*spsi*xdot[0] + (cphi*cpsi+sphi*sthe*spsi)*xdot[1] +\
        (-sphi*cpsi+cphi*sthe*spsi)*xdot[2] # = yEdot
    xdot[11] = -1*(-sthe*xdot[0] + sphi*cthe*xdot[1] +\
        cphi*cthe*xdot[2]) # = hEdot
    return xdot

# 4th Order Runge Kutta Calculation
def RK4(x,u,dt):
    K1 = f(x,u)
    K2 = f(x + K1*dt/2,u)
    K3 = f(x + K2*dt/2,u)
    K4 = f(x + K3*dt,u)
    xest = x + 1/6*(K1 + 2*K2 + 2*K3 + K4)*dt
    return xest


tstep = .01  #Sampling time (sec)

ns = 12  # Number of states
nu = 4   # Number of inputs
t = arange(0,10,tstep)
x = zeros((ns,size(t)))
xc = zeros((ns,size(t)))
u = zeros((nu,size(t)))

# Initial Conditions
x[11,0] = 0.3
x[7,0] = 0.2



# Initial inputs
u[:,0] = zeros(4)




for k in range(1,size(t)):   #run for 60 sec
    
    # State truth
    x[:,k] = RK4(x[:,k-1],u[:,k-1],tstep)
    
#    #Ground detection
#    if x[11,k] < 0:
#        x[11,k] = 0
#        x[2,k] = max(0,x[1,k])
        
    # Sensed information
    phi = x[6,k]
    theta = x[7,k]
    p = x[3,k]; q = x[4,k]; r = x[5,k]
    
    phidot = p + (q*sin(phi) + r*cos(phi))*tan(theta)
    thetadot = q*cos(phi) - r*sin(phi)
    
    h = x[11,k]
    hdot = -x[2,k]  #for small angle
    
    
    # Control Law Gains
    Kp = 500
    Kd = 50
    Kh = 500
    Khdot = 250
    
    #State error
    #e = x[:,k] - xc[:,k]
    

    
    # Reference values
    hCmd = 0.2

    #feedback = K * [e,None]    # e must be a column vector
    #u[:,k] = np.array([T1e,T2e]).T - feedback.A1
    #u[:,k] = u[:,k-1]
    pitch = -Kp*theta - Kd*thetadot
    roll = -Kp*phi - Kd*phidot
    height = -Kh*(h-hCmd) - Khdot*hdot
    trim = 1402
    u[0,k] = int(roll + pitch + height) + trim
    u[1,k] = int(-roll - pitch + height) + trim
    u[2,k] = int(-roll + pitch + height) + trim
    u[3,k] = int(roll - pitch + height) + trim
    
#    u[0,k] = 1500
#    u[1,k] = 1500
#    u[2,k] = 1500
#    u[3,k] = 1500
    
    # Limits
    u[0,k] = max(1000,min(2000,u[0,k]))
    u[1,k] = max(1000,min(2000,u[1,k]))
    u[2,k] = max(1000,min(2000,u[2,k]))
    u[3,k] = max(1000,min(2000,u[3,k]))
    
    
     
figure(1)
subplot(311)
plot(t,x[11,:],'b',label='h')
ylabel('h [m]')
legend(loc='best')
subplot(312)
plot(t,x[9,:],'b',label='x')
ylabel('x [m]')
#plot(t,x[2,:]*57.3,'b',label='x')
#ylabel('pitch rate [deg/s]')
subplot(313)
plot(t,x[7,:]*57.3,'b',label='theta')
ylabel('theta [deg]')
figure(2)
plot(x[9,:],x[10,:],'b',label='y')
ylabel('y [m]'); xlabel('x [m]')
legend(loc='best')
figure(3)
plot(t,u[0,:],'b',label='T1')
plot(t,u[1,:],'g',label='T2')
xlabel('Time (sec)')
legend(loc='best')

#figure(4)
#plot(t,height)

show()

