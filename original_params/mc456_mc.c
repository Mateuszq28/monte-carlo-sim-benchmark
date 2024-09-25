
/********************************************
 *  mc321.c    , in ANSI Standard C programing language
 *
 *  Monte Carlo simulation yielding spherical, cylindrical, and planar 
 *    responses to an isotropic point source in an infinite homogeneous 
 *    medium with no boundaries. This program is a minimal Monte Carlo 
 *    program scoring photon distributions in spherical, cylindrical, 
 *    and planar shells.
 *
 *  by Steven L. Jacques based on prior collaborative work 
 *    with Lihong Wang, Scott Prahl, and Marleen Keijzer.
 *    partially funded by the NIH (R29-HL45045, 1991-1997) and  
 *    the DOE (DE-FG05-91ER617226, DE-FG03-95ER61971, 1991-1999).
 *
 *  A published report illustrates use of the program:
 *    S. L. Jacques: "Light distributions from point, line, and plane 
 *    sources for photochemical reactions and fluorescence in turbid 
 *    biological tissues," Photochem. Photobiol. 67:23-32, 1998. 
 *
 *  Trivial fixes to remove warnings SAP, 11/2017
 **********/

#include <math.h>
#include <stdio.h>
#include <stdbool.h>

// for Cube
#define MAX_XY 180
#define MAX_Z 240

#define	PI          3.1415926
#define	LIGHTSPEED	2.997925E10 /* in vacuo speed of light [cm/s] */
#define ALIVE       1   		/* if photon not yet terminated */
#define DEAD        0    		/* if photon is to be terminated */
#define THRESHOLD   0.01		/* used in roulette */
#define CHANCE      0.1  		/* used in roulette */
#define COS90D      1.0E-6
     /* If cos(theta) <= COS90D, theta >= PI/2 - 1e-6 rad. */
#define ONE_MINUS_COSZERO 1.0E-12
     /* If 1-cos(theta) <= ONE_MINUS_COSZERO, fabs(theta) <= 1e-6 rad. */
     /* If 1+cos(theta) <= ONE_MINUS_COSZERO, fabs(PI-theta) <= 1e-6 rad. */
#define SIGN(x)           ((x)>=0 ? 1:-1)
#define InitRandomGen    (long double) RandomGen(0, 1, NULL)
     /* Initializes the seed for the random number generator. */     
#define RandomNum        (long double) RandomGen(1, 0, NULL)
     /* Calls for a random number from the randum number generator. */

/* DECLARE FUNCTION */
long double RandomGen(char Type, long Seed, long *Status);  
     /* Random number generator */

void save_3d_array_to_json(const char* filename, long double arr[MAX_XY][MAX_XY][MAX_Z], int x, int y, int z, long long Nphotons, long double cube_overflow, double bins_per_1_cm, double mua, long double W);

void displayProgressBar(long long progress, long long total, long long min_step);


int main() {

/* Propagation parameters */
double	x, y, z;    /* photon position */
double	ux, uy, uz; /* photon trajectory as cosines */
double  uxx, uyy, uzz;	/* temporary values used during SPIN */
double	s;          /* step sizes. s = -log(RND)/mus [cm] */
double	costheta;   /* cos(theta) */
double  sintheta;   /* sin(theta) */
double	cospsi;     /* cos(psi) */
double  sinpsi;     /* sin(psi) */
double	psi;        /* azimuthal angle */
long double	W;          /* photon weight */
long double	absorb;     /* weighted deposited in a step due to absorption */
short   photon_status;  /* flag = ALIVE=1 or DEAD=0 */

/* other variables */
long double	Csph[241];  /* spherical   photon concentration CC[ir=0..100] */
long double	Ccyl[241];  /* cylindrical photon concentration CC[ir=0..100] */
long double	Cpla[241];  /* planar      photon concentration CC[ir=0..100] */

// to avoid stack overflow
// Correct allocation with malloc
long double (*Cube)[MAX_XY][MAX_Z] = (long double (*)[MAX_XY][MAX_Z])malloc(MAX_XY * MAX_XY * MAX_Z * sizeof(long double));
if (Cube == NULL) {
    printf("Memory allocation failed.\n");
    return 1;
}

long double cube_overflow;
long double	Fsph;       /* fluence in spherical shell */
long double	Fcyl;       /* fluence in cylindrical shell */
long double	Fpla;       /* fluence in planar shell */
double	mua;        /* absorption coefficient [cm^-1] */
double	mus;        /* scattering coefficient [cm^-1] */
double	g;          /* anisotropy [-] */
double	albedo;     /* albedo of tissue */
double	nt;         /* tissue index of refraction */
long long	Nphotons;   /* number of photons in simulation */
long long min_step_progress_bar;
short	NR_z;         /* number of z positions */
short	NR_xy;         /* number of xy positions */
double	z_size;  /* maximum z size of cube */
double	xy_size;  /* maximum xy size of cube */
double	r;          /* radial position */
double  dr;         /* radial bin size */
short	ir;         /* index to radial position */
short ix;
short iy;
short iz;
double x_start;
double y_start;
double z_start;
bool ix_is_in;
bool iy_is_in;
bool iz_is_in;
bool is_in;
long double  shellvolume;  /* volume of shell at radial position r */

/* dummy variables */
long double  rnd;        /* assigned random value 0-1 */
long double	temp;    /* dummy variables */
FILE*	target;     /* point to output file */
double z_focus, x_focus, b_rad, w_rad;


/**** INPUT
   Input the optical properties
   Input the bin and array sizes 
   Input the number of photons
*****/

mua         = 1.673;     /* cm^-1 */ /*ID_EDIT_4_1*/
mus         = 312.0;  /* cm^-1 */ /*ID_EDIT_4_2*/
g           = 0.9;  /*ID_EDIT_5*/
nt          = 1.33; /*ID_EDIT_4_3*/
Nphotons    = 100000000; /* set number of photons in simulation */ /*ID_EDIT_1_3*/
min_step_progress_bar = Nphotons/100;
z_size = 2.0;   /* cm, total range over which bins extend */
xy_size = 1.5; // cm
NR_z          = 240;	 /* set number of bins.  */
NR_xy = 180;
   /* IF NR_z IS ALTERED, THEN USER MUST ALSO ALTER THE ARRAY DECLARATION TO A SIZE = NR_z + 1. */
dr          = z_size/NR_z;  /* cm */
albedo      = mus/(mus + mua);


/**** INITIALIZATIONS 
*****/
InitRandomGen;
printf("initializing arrays with zeros...\n");
for (ir=0; ir<=NR_z; ir++) {
  Csph[ir] = 0;
  Ccyl[ir] = 0;
  Cpla[ir] = 0;
}

// [x][y][z]
for (int ix=0; ix<NR_xy; ix++)
  for (int iy=0; iy<NR_xy; iy++)
    for (int iz=0; iz<NR_z; iz++)
      Cube[ix][iy][iz] = 0;
cube_overflow = 0;
printf("initializing done...\n");

// start pos
x_start = 89 * dr;
y_start = 89 * dr;
z_start = 239 * dr;


/**** RUN
   Launch N photons, initializing each one before progation.
*****/
printf("simulation progress:\n");
for (long long i_photon = 1; i_photon <= Nphotons; i_photon++)
{
displayProgressBar(i_photon, Nphotons, min_step_progress_bar);
  


/**** LAUNCH 
   Initialize photon position and trajectory.
   Implements a point source [0,0,-1].
*****/
W = 1.0;                    /* set photon weight to one */
photon_status = ALIVE;      /* Launch an ALIVE photon */

w_rad = 20 * SIGN(2*RandomNum-1) * dr;    /* Set photon position to origin. */ /*ID_EDIT_6_FIXED*/
x = x_start + w_rad * sqrt(-log(RandomNum)); /* log is e base */ /*ID_EDIT_6_DEL*/
y = y_start; /*ID_EDIT_6_DEL*/
z = z_start; /*ID_EDIT_6_DEL*/
z_focus = 60 * dr; /*ID_EDIT_6_DEL*/
x_focus = w_rad * sqrt(-log(RandomNum)) * SIGN(2*RandomNum-1); /*ID_EDIT_6_DEL*/
temp = sqrt(pow((x-x_focus),2) + pow(z_focus,2)); /*ID_EDIT_6_DEL*/
sintheta = -(x-x_focus)/temp; /*ID_EDIT_6_DEL*/
costheta = z_focus/temp; /*ID_EDIT_6_DEL*/
ux = sintheta; /*ID_EDIT_6_DEL*/
uy = 0; /*ID_EDIT_6_DEL*/
uz = costheta; /*ID_EDIT_6_DEL*/


/* HOP_DROP_SPIN_CHECK
   Propagate one photon until it dies as determined by ROULETTE.
*******/
do {


/**** HOP
   Take step to new position
   s = stepsize
   ux, uy, uz are cosines of current photon trajectory
*****/
  while ((rnd = RandomNum) <= 0.0);   /* yields 0 < rnd <= 1 */
  s = -log(rnd)/(mua + mus);          /* Step size.  Note: log() is base e */
  x += s * ux;                        /* Update positions. */
  y += s * uy;
  z += s * uz;


/**** DROP
   Drop photon weight (W) into local bin.
*****/
   absorb = W*(1 - albedo);      /* photon weight absorbed at this step */
   W -= absorb;                  /* decrement WEIGHT by amount absorbed */
   
   /* spherical */
   r = sqrt(x*x + y*y + z*z);    /* current spherical radial position */
   ir = (short)(r/dr);           /* ir = index to spatial bin */
   if (ir >= NR_z) ir = NR_z;        /* last bin is for overflow */
   Csph[ir] += absorb;           /* DROP absorbed weight into bin */
   
   /* cylindrical */
   r = sqrt(x*x + y*y);          /* current cylindrical radial position */
   ir = (short)(r/dr);           /* ir = index to spatial bin */
   if (ir >= NR_z) ir = NR_z;        /* last bin is for overflow */
   Ccyl[ir] += absorb;           /* DROP absorbed weight into bin */
   
   /* planar */
   r = fabs(z);                  /* current planar radial position */
   ir = (short)(r/dr);           /* ir = index to spatial bin */
   if (ir >= NR_z) ir = NR_z;        /* last bin is for overflow */
   Cpla[ir] += absorb;           /* DROP absorbed weight into bin */

  // --- cube ---
  ix = x/dr;
  iy = y/dr;
  iz = z/dr;
  ix_is_in = (0 <= ix && ix < NR_xy);
  iy_is_in = (0 <= iy && iy < NR_xy);
  iz_is_in = (0 <= iz && iz < NR_z);
  is_in = (ix_is_in && iy_is_in && iz_is_in);
  if (!is_in) cube_overflow += absorb;
  else Cube[ix][iy][iz] += absorb;

/**** SPIN 
   Scatter photon into new trajectory defined by theta and psi.
   Theta is specified by cos(theta), which is determined 
   based on the Henyey-Greenstein scattering function.
   Convert theta and psi into cosines ux, uy, uz.
   psi - berween x-y axis
   theta between z and R
*****/
  /* Sample for costheta */
  rnd = RandomNum;
     if (g == 0.0)
        costheta = 2.0*rnd - 1.0;
     else {
        long double temp = (1.0 - g*g)/(1.0 - g + 2*g*rnd);
        costheta = (1.0 + g*g - temp*temp)/(2.0*g);
        }
  sintheta = sqrt(1.0 - costheta*costheta); /* sqrt() is faster than sin(). */

  /* Sample psi. */
  psi = 2.0*PI*RandomNum;
  cospsi = cos(psi);
  if (psi < PI)
    sinpsi = sqrt(1.0 - cospsi*cospsi);     /* sqrt() is faster than sin(). */
  else
    sinpsi = -sqrt(1.0 - cospsi*cospsi);

  /* New trajectory. */
  if (1 - fabs(uz) <= ONE_MINUS_COSZERO) {      /* close to perpendicular. */
    uxx = sintheta * cospsi;
    uyy = sintheta * sinpsi;
    uzz = costheta * SIGN(uz);   /* SIGN() is faster than division. */
    } 
  else {					/* usually use this option */
    temp = sqrt(1.0 - uz * uz);
    uxx = sintheta * (ux * uz * cospsi - uy * sinpsi) / temp + ux * costheta;
    uyy = sintheta * (uy * uz * cospsi + ux * sinpsi) / temp + uy * costheta;
    uzz = -sintheta * cospsi * temp + uz * costheta;
    }
    
  /* Update trajectory */
  ux = uxx;
  uy = uyy;
  uz = uzz;


/**** CHECK ROULETTE 
   If photon weight below THRESHOLD, then terminate photon using Roulette technique.
   Photon has CHANCE probability of having its weight increased by factor of 1/CHANCE,
   and 1-CHANCE probability of terminating.
*****/
if (W < THRESHOLD) {
   if (RandomNum <= CHANCE)
      W /= CHANCE;
   else photon_status = DEAD;
   }


} /* end STEP_CHECK_HOP_SPIN */
while (photon_status == ALIVE);

  /* If photon dead, then launch new photon. */
} /* end RUN */


/**** SAVE
   Convert data to relative fluence rate [cm^-2] and save to file called "mcmin321.out".
*****/
// target = fopen("mc321.out", "w");
printf("saving data...\n");
target = fopen("mc456_out.txt", "w");

fprintf(target, "number of photons = %lld\n", Nphotons);
fprintf(target, "overflow: %.20e\n", cube_overflow);
long double cube_sum = 0;
for (int i=0; i<NR_xy; i++)
  for (int j=0; j<NR_xy; j++)
    for (int k=0; k<NR_z; k++)
      cube_sum += Cube[i][j][k];
fprintf(target, "sum: %.20e\n", cube_sum);
long double cube_sum2 = Nphotons - cube_overflow;
fprintf(target, "sum: %.20e\n", cube_sum2);
long double avg = cube_sum / Nphotons;
fprintf(target, "avg: %.20e\n", avg);
float perc_in = cube_sum / Nphotons * 100;
fprintf(target, "perc_in: %2.2f\n\n", perc_in);

/* print header */
fprintf(target, "number of photons = %lld\n", Nphotons);
fprintf(target, "bin size = %5.5f [cm] \n", dr);
fprintf(target, "last row is overflow. Ignore.\n");

/* print column titles */
fprintf(target, "r [cm] \t Fsph [1/cm2] \t Fcyl [1/cm2] \t Fpla [1/cm2]\n");

/* print data:  radial position, fluence rates for 3D, 2D, 1D geometries */
for (ir=0; ir<=NR_z; ir++) {
  	/* r = sqrt(1.0/3 - (ir+1) + (ir+1)*(ir+1))*dr; */
  	r = (ir + 0.5)*dr;
  	shellvolume = 4.0*PI*r*r*dr; /* per spherical shell */
    Fsph = Csph[ir]/Nphotons/shellvolume/mua;
  	shellvolume = 2.0*PI*r*dr;   /* per cm length of cylinder */
    Fcyl = Ccyl[ir]/Nphotons/shellvolume/mua;
  	shellvolume = dr;            /* per cm2 area of plane */
    Fpla =Cpla[ir]/Nphotons/shellvolume/mua;
  	fprintf(target, "%5.5f \t %.20e \t %.20e \t %.20e \n", r, Fsph, Fcyl, Fpla);
  	}

// Flush the buffer to ensure all data is written
fflush(target);
fclose(target);

printf("saving cube into file...\n");
double bins_per_1_cm = NR_z/z_size;
save_3d_array_to_json("mc456_mc_cube.json", Cube, NR_xy, NR_xy, NR_z, Nphotons, cube_overflow, bins_per_1_cm, mua, W);
printf("saving cube completed\n");

} /* end of main */

 

/* SUBROUTINES */

/**************************************************************************
 *	RandomGen
 *      A random number generator that generates uniformly
 *      distributed random numbers between 0 and 1 inclusive.
 *      The algorithm is based on:
 *      W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
 *      Flannery, "Numerical Recipes in C," Cambridge University
 *      Press, 2nd edition, (1992).
 *      and
 *      D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
 *      of "The Art of Computer Programming", Addison-Wesley, (1981).
 *
 *      When Type is 0, sets Seed as the seed. Make sure 0<Seed<32000.
 *      When Type is 1, returns a random number.
 *      When Type is 2, gets the status of the generator.
 *      When Type is 3, restores the status of the generator.
 *
 *      The status of the generator is represented by Status[0..56].
 *
 *      Make sure you initialize the seed before you get random
 *      numbers.
 ****/
#define MBIG 1000000000
#define MSEED 161803398
#define MZ 0
#define FAC 1.0E-9

long double RandomGen(char Type, long Seed, long *Status){
  static long i1, i2, ma[56];   /* ma[0] is not used. */
  long        mj, mk;
  short       i, ii;

  if (Type == 0) {              /* set seed. */
    mj = MSEED - (Seed < 0 ? -Seed : Seed);
    mj %= MBIG;
    ma[55] = mj;
    mk = 1;
    for (i = 1; i <= 54; i++) {
      ii = (21 * i) % 55;
      ma[ii] = mk;
      mk = mj - mk;
      if (mk < MZ)
        mk += MBIG;
      mj = ma[ii];
    }
    for (ii = 1; ii <= 4; ii++)
      for (i = 1; i <= 55; i++) {
        ma[i] -= ma[1 + (i + 30) % 55];
        if (ma[i] < MZ)
          ma[i] += MBIG;
      }
    i1 = 0;
    i2 = 31;
  } else if (Type == 1) {       /* get a number. */
    if (++i1 == 56)
      i1 = 1;
    if (++i2 == 56)
      i2 = 1;
    mj = ma[i1] - ma[i2];
    if (mj < MZ)
      mj += MBIG;
    ma[i1] = mj;
    return (mj * FAC);
  } else if (Type == 2) {       /* get status. */
    for (i = 0; i < 55; i++)
      Status[i] = ma[i + 1];
    Status[55] = i1;
    Status[56] = i2;
  } else if (Type == 3) {       /* restore status. */
    for (i = 0; i < 55; i++)
      ma[i + 1] = Status[i];
    i1 = Status[55];
    i2 = Status[56];
  } else
    puts("Wrong parameter to RandomGen().");
  return (0);
}
#undef MBIG
#undef MSEED
#undef MZ
#undef FAC



void save_3d_array_to_json(const char* filename, long double arr[180][180][240], int x, int y, int z, long long Nphotons, long double cube_overflow, double bins_per_1_cm, double mua, long double W) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }

    /*
    data = {
    "n_photons": Nphotons,
    "overflow": cube_overflow,
    "cube": Cube
    }
    */

    fprintf(file, "{\n");
    fprintf(file, "\"n_photons\": %lld,\n", Nphotons);
    fprintf(file, "\"overflow\": %.20e,\n", cube_overflow);
    fprintf(file, "\"bins_per_1_cm\": %.20e,\n",  bins_per_1_cm);
    fprintf(file, "\"mu_a\": %.20e,\n",  mua);
    fprintf(file, "\"name\": \"org_%dmln_cube\",\n",  (int)(Nphotons/1000000));
    fprintf(file, "\"photon_weight\": %.20e,\n",  W);
    fprintf(file, "\"normalized_already\": false,\n");

    // Start the JSON array
    fprintf(file, "\"cube\": [\n");

    // Iterate through the 3D array
    for (int i = 0; i < x; i++) {
        fprintf(file, "  [\n");  // Start of the 2D array
        for (int j = 0; j < y; j++) {
            fprintf(file, "    [");  // Start of the 1D array
            for (int k = 0; k < z; k++) {
                fprintf(file, "%.20e", arr[i][j][k]);
                if (k < z - 1) {
                    fprintf(file, ", ");
                }
            }
            fprintf(file, "]");  // End of the 1D array
            if (j < y - 1) {
                fprintf(file, ",\n");
            } else {
                fprintf(file, "\n");
            }
        }
        fprintf(file, "  ]");  // End of the 2D array
        if (i < x - 1) {
            fprintf(file, ",\n");
        } else {
            fprintf(file, "\n");
        }
    }

    // End the JSON array
    fprintf(file, "]\n");
    fprintf(file, "}\n");

    // Flush the buffer to ensure all data is written
    fflush(file);
    fclose(file);
}


void displayProgressBar(long long progress, long long total, long long min_step) {
    if (progress % min_step == 0)
    {
      int barWidth = 50; // Width of the progress bar
      int completed = (progress * barWidth) / total;

      printf("[");
      for (int i = 0; i < barWidth; i++) {
          if (i < completed) {
              printf("#");
          } else {
              printf(" ");
          }
      }
      printf("] %lld%%", (progress * 100) / total);
      if (progress != total) printf("\r");
      else printf("\n");
      fflush(stdout);  // Force the output to be printed immediately
    }
}


free(Cube);