import numpy as np

# basic physical constants for the Reference Earth Model - WGS84
mu = 398600.4418 # GM, [km^3/s^2]  
Re = 6378.137 # Equatorial radius of the Earth from WGS84 ellipsoid model, [km]
f = 1/298.257223563 # flattening
Re_V = 6371.0008 # volumetric radius, [km] 
rot = 7.292115e-5 # Rotational speed of the Earth from WGS84 ellipsoid model, [rad/s]
J2 = 1.08262982e-3

au = 1.495978707e8 # Astronomical unit, [km]
S_R = 4.56e-6 # solar radiation pressure, [N/m^2]
R_sun = 6.957e5 # average radius of sun

# Standard gravitational parameter
mu_sun = 1.32712440018e11 # GM, [km^3/s^2]
mu_moon = 4904.8695 # GM, [km^3/s^2]
mu_jup = 1.26686534e8 # # GM, [km^3/s^2]

# other constants
C_D = 2.2 # drag codfficient
C_R = 1.5 # radiation pressure codfficient between 1 and 2; 
          # 1 for blackbody, which means absorbing all of the momentum of the incident photon stream
          # 2 means reflecting all of the momentum of the incident photon stream

# parameters configuration for targets
m = 100 # mass, [kg]
A_D = np.pi/4 # section area for drag, [m^2]
A_R = np.pi/4 # section area for solar radiation, [m^2]
