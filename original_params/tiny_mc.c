char   t1[80] = "Tiny Monte Carlo by Scott Prahl (https://omlc.org)";
char   t2[80] = "1 W Point Source Heating in Infinite Isotropic Scattering Medium";

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define SHELL_MAX  241

double mu_a = 1.673;			   /* Absorption Coefficient in 1/cm !!non-zero!! */
double mu_s = 312.0;			   /* Reduced Scattering Coefficient in 1/cm */
double microns_per_shell = 83.3333333; /* Thickness of spherical shells in microns */
long   i, shell, photons = 10000; /*ID_EDIT_1_1*/
double x, y, z, u, v, w, weight;
double albedo, shells_per_mfp, xi1, xi2, t, heat[SHELL_MAX];


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


int main () 
{
	albedo = mu_s / (mu_s + mu_a);
	shells_per_mfp = 1e4/microns_per_shell/(mu_a+mu_s);
	long progressBarStep = photons / 100;
	
	for (i = 1; i <= photons; i++)
	{
		displayProgressBar(i, photons, progressBarStep);

		x = 0.0; y = 0.0; z = 0.0;					/*launch*/  
		u = 0.0; v = 0.0; w = 1.0;		
		weight = 1.0;
		
		for (;;) {
			t = -log((rand()+1.0)/(RAND_MAX+1.0));	/*move*/
			x += t * u;
			y += t * v;
			z += t * w;  

			shell=sqrt(x*x+y*y+z*z)*shells_per_mfp;	/*absorb*/
			if (shell > SHELL_MAX-1) shell = SHELL_MAX-1;	
			heat[shell] += (1.0-albedo)*weight;
			weight *= albedo;
		
			for(;;) {								/*new direction*/
				xi1=2.0*rand()/RAND_MAX - 1.0; 
				xi2=2.0*rand()/RAND_MAX - 1.0; 
				if ((t=xi1*xi1+xi2*xi2)<=1) break;
			}
			u = 2.0 * t - 1.0;
			v = xi1 * sqrt((1-u*u)/t);
			w = xi2 * sqrt((1-u*u)/t);
			
			if (weight < 0.001){ 					/*roulette*/
				if (rand() > 0.1 * RAND_MAX) break; 
				weight /= 0.1;
			}
		} 
	}	
	
	printf("%s\n%s\n\nScattering = %8.3f/cm\nAbsorption = %8.3f/cm\n",t1,t2,mu_s,mu_a);
	printf("Photons    = %8ld\n\n Radius         Heat\n[microns]     [W/cm^3]\n",photons);
	t = 4*3.14159*pow(microns_per_shell,3)*photons/1e12;
	for (i=0;i<SHELL_MAX-1;i++)
		printf("%6.0f    %12.5e\n",i*microns_per_shell, heat[i]/t/(i*i+i+1.0/3.0));
	printf(" extra    %12.5f\n",heat[SHELL_MAX-1]/photons);
	return 0;
}
