## Time comparison

<u>tiny</u>
original parameters 10 000 photons: 0.3641 seconds
original parameters 1 mln photons: 18.0910 seconds
My sim time (monte-carlo-sim-python): 3895.3408 seconds (1h) for 1 mln photons
my parameters on tiny 10 000 photons: 1.1717 seconds
my parameters on tiny 1 mln photons: 108.9439 seconds

<u>small</u>
original parameters 100 000 photons: 2.9074 seconds
original parameters 1 mln photons: 27.4483 seconds
My sim time (monte-carlo-sim-python): 3895.3408 seconds (1h) for 1 mln photons
my parameters on small 100 000 photons: 8.9404 seconds
my parameters on small 1 mln photons: 86.9339 seconds

<u>mc321</u>
original parameters 10 000 photons: 0.3167 seconds
original parameters 1 mln photons: 0.5768 seconds
My sim time (monte-carlo-sim-python): 3895.3408 seconds (1h) for 1 mln photons
my parameters on mc321 10 000 photons: 1.5611 seconds
my parameters on mc321 1 mln photons: 134.7727 seconds

## Generator period

The period (or cycle length) of a base generator is defined as the maximum number of values that can be generated before the sequence starts to repeat. [[1]](#1)

#### tiny and small
<u>c stdlib rand function perioid</u>
*From documentation:*
POSIX requires that the period of the pseudo-random number generator used by rand be at least 2^32. [[2]](#2)
2^32 = 4 294 967 296

#### mc321
The authors used their own random number generator algorithm based on two books. Unfortunately, neither on the website, nor in the paper, nor in the code did they provide information on its period. However, we can assume that it was significantly larger than the generator period implemented in the rand function from the standard C library.

<u>From the note included in the code, we can read:</u>

A random number generator that generates uniformly
distributed random numbers between 0 and 1 inclusive.

The algorithm is based on:
*W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
Flannery, "Numerical Recipes in C," Cambridge University
Press, 2nd edition, (1992).* [[3]](#3)
and
*D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
of "The Art of Computer Programming", Addison-Wesley, (1981).* [[4]](#4)

#### monte-carlo-sim-python *(my implementation)*
by default it uses Permuted Congruential Generator (64-bit, PCG64)
generator period = 2^128 = 3,4E38



## Bibliography

<a name="1"></a>[1] https://support.nag.com/numeric/mb/nagdoc_mb/manual_25_1/html/g05/g05intro.html#:~:text=The%20period%20(or%20cycle%20length,the%20sequence%20starts%20to%20repeat.

<a name="2"></a>[2] https://devdocs.io/c/numeric/random/rand

<a name="3"></a> [3] *W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
Flannery, "Numerical Recipes in C," Cambridge University
Press, 2nd edition, (1992).*
https://www.fccdecastro.com.br/CursoC&C++/Numerical%20Recipes%20in%20C%202nd%20-%20%20Press.pdf

<a name="4"></a> [4] *D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
of "The Art of Computer Programming", Addison-Wesley, (1981).*
https://seriouscomputerist.atariverse.com/media/pdf/book/Art%20of%20Computer%20Programming%20-%20Volume%202%20(Seminumerical%20Algorithms).pdf






