# mc321_p.py - my translation of mc321.c to python

import math
import json
from tqdm import tqdm

PI = math.pi
LIGHTSPEED = 2.997925E10 # in vacuo speed of light [cm/s]
ALIVE = 1 # if photon not yet terminated
DEAD = 0 # if photon is to be terminated
THRESHOLD = 1.0E-4 # used in roulette
CHANCE = 0.1 # used in roulette
    # If cos(theta) <= COS90D, theta >= PI/2 - 1e-6 rad
COS90D = 1.0E-6
ONE_MINUS_COSZERO = 1.0E-12
    # If 1-cos(theta) <= ONE_MINUS_COSZERO, fabs(theta) <= 1e-6 rad
    # If 1+cos(theta) <= ONE_MINUS_COSZERO, fabs(PI-theta) <= 1e-6 rad

SIGN = lambda x: 1 if x >= 0 else -1



# SUBROUTINES

# **************************************************************
#	RandomGen
#      A random number generator that generates uniformly
#      distributed random numbers between 0 and 1 inclusive.
#      The algorithm is based on:
#      W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
#      Flannery, "Numerical Recipes in C," Cambridge University
#      Press, 2nd edition, (1992).
#      and
#      D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
#      of "The Art of Computer Programming", Addison-Wesley, (1981).
#
#      When Type is 0, sets Seed as the seed. Make sure 0<Seed<32000.
#      When Type is 1, returns a random number.
#      When Type is 2, gets the status of the generator.
#      When Type is 3, restores the status of the generator.
#
#      The status of the generator is represented by Status[0..56].
#
#      Make sure you initialize the seed before you get random
#      numbers.
# **************************************************************

MBIG = 1000000000
MSEED = 161803398
MZ = 0
FAC = 1.0E-9

i1 = None
i2 = None
ma = [None for _ in range(56)] # ma[0] is not used
def RandomGen(Type, Seed, Status):
    global i1
    global i2
    global ma
    if (Type == 0): # set seed
        Seed = -Seed if Seed < 0 else Seed
        mj = MSEED - Seed
        mj %= MBIG
        ma[55] = mj
        mk = 1
        for i in range(1,55):
            ii = (21 * i) % 55
            ma[ii] = mk
            mk = mj - mk
            if (mk < MZ):
                mk += MBIG
            mj = ma[ii]
        for ii in range(1,5):
            for i in range(1,56):
                ma[i] -= ma[1 + (i + 30) % 55]
                if (ma[i] < MZ):
                    ma[i] += MBIG
        i1 = 0
        i2 = 31
    elif (Type == 1): # get a number
        i1 += 1
        if (i1 == 56):
            i1 = 1
        i2 += 1
        if (i2 == 56):
            i2 = 1
        mj = ma[i1] - ma[i2]
        if (mj < MZ):
            mj += MBIG
        ma[i1] = mj
        return (mj * FAC)

    elif (Type == 2): # get status
        for i in range(0,55):
            Status[i] = ma[i + 1]
        Status[55] = i1
        Status[56] = i2
    elif (Type == 3): # restore status
        for i in range(0,55):
            ma[i + 1] = Status[i]
        i1 = Status[55]
        i2 = Status[56]
    else:
        print("Wrong parameter to RandomGen().")
    return 0


# Initializes the seed for the random number generator
def InitRandomGen():
    RandomGen(0, 1, None)


# Calls for a random number from the random number generator.
def RandomNum():
    return RandomGen(1, 0, None)



# **************************************************************



def main():

    # Propagation parameters
    # x, y, z           # photon position
    # ux, uy, uz        # photon trajectory as cosines
    # uxx, uyy, uzz     # temporary values used during SPIN
    # s                 # step sizes. s = -log(RND)/mus [cm]
    # costheta          # cos(theta)
    # sintheta          # sin(theta)
    # cospsi            # cos(psi)
    # sinpsi            # sin(psi)
    # psi               # azimuthal angle
    # i_photon          # current photon
    # W                 # photon weight
    # absorb            # weighted deposited in a step due to absorption
    # photon_status    # flag = ALIVE=1 or DEAD=0

    # --- other variables ---
    # Csph = [None for _ in range(241)] # spherical   photon concentration CC[ir=0..100]
    # Ccyl = [None for _ in range(241)] # cylindrical photon concentration CC[ir=0..100]
    # Cpla = [None for _ in range(241)] # planar      photon concentration CC[ir=0..100]
    # Fsph       # fluence in spherical shell
    # Fcyl       # fluence in cylindrical shell
    # Fpla       # fluence in planar shell
    # mua        # absorption coefficient [cm^-1]
    # mus        # scattering coefficient [cm^-1]
    # g          # anisotropy [-]
    # albedo     # albedo of tissue
    # nt         # tissue index of refraction
    # Nphotons   # number of photons in simulation
    # NR         # number of radial positions
    # radial_size  # maximum radial size
    # r          # radial position
    # dr         # radial bin size
    # ir         # index to radial position
    # shellvolume  # volume of shell at radial position r

    # --- dummy variables ---
    # rnd       # assigned random value 0-1
    # temp      # dummy variables
    # target    # point to output file


    # ***** INPUT
    # Input the optical properties
    # Input the bin and array sizes 
    # Input the number of photons
    # *****

    mua         = 0.37     # cm^-1
    mus         = 23.88889  # cm^-1
    g           = 0.9
    nt          = 1.36
    Nphotons    = int(1e3) # set number of photons in simulation
    z_size = 2.0 # cm, total range over which bins extend
    xy_size = 1.5 # cm
    NR_z          = 240 # set number of bins.
    NR_xy = 180
    # IF NR IS ALTERED, THEN USER MUST ALSO ALTER THE ARRAY DECLARATION TO A SIZE = NR + 1.
    dr          = z_size/NR_z  # cm
    albedo      = mus/(mus + mua)


    # ***** INITIALIZATIONS 
    # *****
    InitRandomGen()
    Csph = [0 for _ in range(0,NR_z+1)]
    Ccyl = [0 for _ in range(0,NR_z+1)]
    Cpla = [0 for _ in range(0,NR_z+1)]

    # [x][y][z]
    # it could be done in numpy array, but list is easier to save
    Cube = [[[0 for _ in range(0,NR_z+1)] for _ in range(0,NR_xy+1)] for _ in range(0,NR_xy+1)]
    cube_overflow = 0

    # start pos
    x_start = 89 * dr
    y_start = 89 * dr
    z_start = 239 * dr

    
    # ***** RUN
    # Launch N photons, initializing each one before progation.
    # *****
    print("(1 iter = 1 photon) Simulation progerss:")
    for i_photon in tqdm(range(0,Nphotons)):


        # ***** LAUNCH 
        # Initialize photon position and trajectory.
        # Implements a point source [0,0,-1].
        # *****
        W = 1.0                    # set photon weight to one
        photon_status = ALIVE      # Launch an ALIVE photon

        x = x_start                     # Set photon position to origin.
        y = y_start
        z = z_start

        # source - vartical down [0,0,-1]
        # psi - berween x-y axis
        # theta between z and R
        ux = 0
        uy = 0
        uz = -1


        # ***** HOP_DROP_SPIN_CHECK
        # Propagate one photon until it dies as determined by ROULETTE.
        # *****
        while (photon_status == ALIVE):


            # ***** HOP
            # Take step to new position
            # s = stepsize
            # *****
            rnd = RandomNum()
            while (rnd <= 0.0):
                rnd = RandomNum()
                # yields 0 < rnd <= 1
            s = -math.log(rnd)/(mua + mus) # Step size. Note: log() is base e
            x += s * ux # Update positions.
            y += s * uy
            z += s * uz


            # ***** DROP
            # Drop photon weight (W) into local bin.
            # *****
            absorb = W*(1 - albedo) # photon weight absorbed at this step
            W -= absorb # decrement WEIGHT by amount absorbed
            
            # --- spherical ---
            r = math.sqrt(x*x + y*y + z*z) # current spherical radial position
            ir = int(r/dr) # ir = index to spatial bin
            if (ir >= NR_z): # last bin is for overflow
                ir = NR_z
            Csph[ir] += absorb # DROP absorbed weight into bin
            
            # --- cylindrical ---
            r = math.sqrt(x*x + y*y) # current cylindrical radial position
            ir = int(r/dr) # ir = index to spatial bin
            if (ir >= NR_z): # last bin is for overflow
                ir = NR_z
            Ccyl[ir] += absorb # DROP absorbed weight into bin
            
            # --- planar ---
            r = abs(z) # current planar radial position
            ir = int(r/dr) # ir = index to spatial bin
            if (ir >= NR_z): # last bin is for overflow
                ir = NR_z
            Cpla[ir] += absorb # DROP absorbed weight into bin

            # --- cube ---
            ix = int(x/dr)
            iy = int(y/dr)
            iz = int(z/dr)
            ix_is_in = (0 <= ix < NR_xy)
            iy_is_in = (0 <= iy < NR_xy)
            iz_is_in = (0 <= iz < NR_z)
            is_in = ix_is_in and iy_is_in and iz_is_in
            if (not is_in):
                cube_overflow += absorb
            else:
                Cube[ix][iy][iz] += absorb
            

            # ***** SPIN 
            # Scatter photon into new trajectory defined by theta and psi.
            # Theta is specified by cos(theta), which is determined 
            # based on the Henyey-Greenstein scattering function.
            # Convert theta and psi into cosines ux, uy, uz. 
            # *****
            # --- Sample for costheta ---
            rnd = RandomNum()
            if (g == 0.0):
                costheta = 2.0*rnd - 1.0
            else:
                temp = (1.0 - g*g)/(1.0 - g + 2*g*rnd)
                costheta = (1.0 + g*g - temp*temp)/(2.0*g)

            sintheta = math.sqrt(1.0 - costheta*costheta) # sqrt() is faster than sin().

            # --- Sample psi. ---
            psi = 2.0*PI*RandomNum()
            cospsi = math.cos(psi)
            if (psi < PI):
                sinpsi = math.sqrt(1.0 - cospsi*cospsi) # sqrt() is faster than sin().
            else:
                sinpsi = -math.sqrt(1.0 - cospsi*cospsi)

            # --- New trajectory. ---
            if (1 - abs(uz) <= ONE_MINUS_COSZERO): # close to perpendicular.
                uxx = sintheta * cospsi
                uyy = sintheta * sinpsi
                uzz = costheta * SIGN(uz) # SIGN() is faster than division.

            else: # usually use this option
                temp = math.sqrt(1.0 - uz * uz);
                uxx = sintheta * (ux * uz * cospsi - uy * sinpsi) / temp + ux * costheta
                uyy = sintheta * (uy * uz * cospsi + ux * sinpsi) / temp + uy * costheta
                uzz = -sintheta * cospsi * temp + uz * costheta
                
            # --- Update trajectory ---
            ux = uxx;
            uy = uyy;
            uz = uzz;


            # ***** CHECK ROULETTE 
            # If photon weight below THRESHOLD, then terminate photon using Roulette technique.
            # Photon has CHANCE probability of having its weight increased by factor of 1/CHANCE,
            # and 1-CHANCE probability of terminating.
            # *****
            if (W < THRESHOLD):
                if (RandomNum() <= CHANCE):
                    W /= CHANCE
                else:
                    photon_status = DEAD

            # end STEP_CHECK_HOP_SPIN

        # If photon dead, then launch new photon.
        # end RUN



    # ***** SAVE
    # Convert data to relative fluence rate [cm^-2] and save to file called "mcmin321.out".
    # *****
    print("saving data...")
    file = open("mc456_p_out.txt", 'w')

    # --- print header ---
    file.write(f"number of photons = {Nphotons}\n")
    file.write(f"bin size = {dr:5.5f} [cm] \n")
    file.write("last row is overflow. Ignore.\n")

    # --- print column titles ---
    file.write("r [cm] \t Fsph [1/cm2] \t Fcyl [1/cm2] \t Fpla [1/cm2]\n")

    # print data:  radial position, fluence rates for 3D, 2D, 1D geometries
    for ir in range(0,NR_z+1):
        # r = sqrt(1.0/3 - (ir+1) + (ir+1)*(ir+1))*dr
        r = (ir + 0.5)*dr
        shellvolume = 4.0*PI*r*r*dr # per spherical shell
        Fsph = Csph[ir]/Nphotons/shellvolume/mua
        shellvolume = 2.0*PI*r*dr # per cm length of cylinder
        Fcyl = Ccyl[ir]/Nphotons/shellvolume/mua
        shellvolume = dr # per cm2 area of plane
        Fpla =Cpla[ir]/Nphotons/shellvolume/mua
        file.write(f"{r:5.5f} \t {Fsph:4.3e} \t {Fcyl:4.3e} \t {Fpla:4.3e} \n")

    file.close()


    with open('mc456_p_cube.json', 'w') as f:
        data = {
            "n_photons": Nphotons,
            "overflow": cube_overflow,
            "bins_per_1_cm": NR_z/z_size,
            "cube": Cube
        }
        json.dump(data, f)

    print("done")
    # end of main


main()
