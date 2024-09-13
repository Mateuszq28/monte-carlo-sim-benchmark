
[benchmark_sims](benchmark_sims)

[Link do plików json z wynikami symulacji](https://drive.google.com/drive/folders/1VByTZKmBNYR8t2rjlFV-DcrW1aDlFMf-?usp=sharing)

## Porównanie czasu symulacji

- oryginalne parametry - oryginalne paremetry środowiska symulacji z implementacji z literatury
- własne parametry - parametry wybrane na podstawie przeglądu literatury pod kątem optycznych parametrów skóry

<ins>monte-carlo-python</ins>\
[repozytorium github](https://github.com/Mateuszq28/monte-carlo-sim-python)\
*język programowania: python*\
jednolita tkanka\
Moja implementacja (monte-carlo-sim-python): 3895 sekund (1h 5 min) dla 1 mln fotonów\
Po zoptymalizowaniu liczenia sinusów i cosinusów 1mln fotonów: 1784 sekund (30 min)\

<ins>tiny_mc.c</ins>\
[[5]](#5)\
*język programowania: c*\
oryginalne parametry 10 000 fotonów: 1 sekunda\
oryginalne parametry 1 mln fotonów: 16 sekund\
własne parametry 10 000 fotonów: 1 sekund\
własne parametry 1 mln fotonów: 109 sekund\

<ins>small_mc.c</ins>\
[[5]](#5)\
*język programowania: c*\
oryginalne parametry 10 000 fotonów: 1 sekunda\
oryginalne parametry 100 000 fotonów: 3.5 sekund\
oryginalne parametry 1 mln fotonów: 26.5 sekund\
własne parametry on small 10 000 fotonów: 1.6 sekund\
własne parametry small 100 000 fotonów: 9 sekund\
własne parametry small 1 mln fotonów: 87 sekund\

<ins>mc321_mc.c</ins>
[[5]](#5)\
*język programowania: c*\
oryginalne parametry 10 000 fotonów: 0.6 sekund\
oryginalne parametry 1 mln fotonów: 1.2 sekund\
własne parametry 10 000 fotonów: 1.6 sekund\
własne parametry 1 mln fotonów: 135 sekund\

<ins>mc321_p.py</ins>\
[[5]](#5)\
*język programowania: python*\
oryginalne parametry 10 000 fotonów: 0.2 sekund\
oryginalne parametry 1 mln fotonów: 9.8 sekund\
własne parametry 10 000 fotonów: 35.8 sekund\
własne parametry 1 mln fotonów: 3910 sekund (1h 5 min)\

<ins>mc456_p.py</ins>\
[[5]](#5)\
*język programowania: python*\
oryginalne parametry 10 000 fotonów: 11 sekund\
oryginalne parametry 1 mln fotonów: 19 sekund\
własne parametry 10 000 fotonów: 55 sekund\
własne parametry 1 mln fotonów: 4490 sekund (1h 15 min)\

<ins>mc456_mc.c</ins>\
[[5]](#5)\
*język programowania: python*\
oryginalne parametry 10^4 = 10 000 fotonów: 11 sekund\
oryginalne parametry 10^5 = 100 000 fotonów: 11 sekund\
oryginalne parametry 10^6 = 1 mln fotonów: 12 sekund\
oryginalne parametry 10^7 = 10 mln fotonów: 14 sekund\
oryginalne parametry 10^8 = 100 mln fotonów: 15.6 sekund\
oryginalne parametry 10^9 = 1 mld fotonów: 287.5 sekund (5 min)
własne parametry 10^4 = 10 000 fotonów: 12 sekund\
własne parametry 10^5 = 100 000 fotonów: 38.8 sekund\
własne parametry 10^6 = 1 mln fotonów: 162.8 sekund (2 min 43 s)\
własne parametry 10^7 = 10 mln fotonów: 1358.7 sekund (23 min)\
własne parametry 10^8 = 100 mln fotonów: 13275.9 sekund (3h 42 min)\


<!--
overflow and too less digits in print e notation
<ins>mc456_mc.c</ins>
*programming language: python*
original parameters 10^4 = 10 000 photons: 8.0297 seconds
original parameters 10^5 = 100 000 photons: 7.9869 seconds
original parameters 10^6 = 1 mln photons: 9.4164 seconds
original parameters 10^7 = 10 mln photons: 12.6733 seconds
original parameters 10^8 = 100 mln photons: 36.6226 seconds
original parameters 10^9 = 1 mld photons: 290.9062 seconds (5min)
my parameters on mc456 10^4 = 10 000 photons: 10.5652 seconds
my parameters on mc456 10^5 = 100 000 photons: 23.9545 seconds
my parameters on mc456 10^6 = 1 mln photons: 151.7471 seconds
my parameters on mc456 10^7 = 10 mln photons: 1356.2483 seconds (23 min)
my parameters on mc456 10^8 = 100 mln photons: 13290.7210 seconds (3h 42 min)
-->

## Okres generatora

Okres (lub długość cyklu) generatora bazowego jest definiowany jako maksymalna liczba wartości, które można wygenerować, zanim sekwencja zacznie się powtarzać. [[1]](#1)\

#### tiny i small
<ins>okres funkcji rand z biblioteki standardowej języka c</ins>\
*Z dokumentacji:*\
POSIX wymaga, aby okres generatora liczb pseudolosowych używanego przez rand wynosił co najmniej 2^32. [[2]](#2)\
2^32 = 4 294 967 296\

#### mc321
Autorzy wykorzystali własny algorytm generatora liczb losowych oparty na dwóch książkach. Niestety, ani na stronie internetowej, ani w artykule, ani w kodzie nie podali informacji o jego okresie. Możemy jednak założyć, że był on znacznie większy niż okres generatora zaimplementowany w funkcji rand ze standardowej biblioteki C.\

<ins>Z notatki dołączonej do kodu możemy wyczytać:</ins>

Generator liczb losowych, który generuje równomiernie rozłożone liczby losowe od 0 do 1 włącznie.\

Algorytm opiera się na:\
*W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
Flannery, "Numerical Recipes in C," Cambridge University
Press, 2nd edition, (1992).* [[3]](#3)\
and\
*D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
of "The Art of Computer Programming", Addison-Wesley, (1981).* [[4]](#4)\

#### monte-carlo-sim-python *(własna implementacja)*
domyślnie używa Permuted Congruential Generator (64-bit, PCG64)\
okres generatora = 2^128 = 3,4E38\



## Bibliografia

<a name="1"></a>[1] https://support.nag.com/numeric/mb/nagdoc_mb/manual_25_1/html/g05/g05intro.html#:~:text=The%20period%20(or%20cycle%20length,the%20sequence%20starts%20to%20repeat.

<a name="2"></a>[2] https://devdocs.io/c/numeric/random/rand

<a name="3"></a> [3] *W.H. Press, S.A. Teukolsky, W.T. Vetterling, and B.P.
Flannery, "Numerical Recipes in C," Cambridge University
Press, 2nd edition, (1992).*
https://www.fccdecastro.com.br/CursoC&C++/Numerical%20Recipes%20in%20C%202nd%20-%20%20Press.pdf

<a name="4"></a> [4] *D.E. Knuth, "Seminumerical Algorithms," 2nd edition, vol. 2
of "The Art of Computer Programming", Addison-Wesley, (1981).*
https://seriouscomputerist.atariverse.com/media/pdf/book/Art%20of%20Computer%20Programming%20-%20Volume%202%20(Seminumerical%20Algorithms).pdf

<a name="5"></a> [5] https://omlc.org/software/mc/











<!-- ENGLISH -->
<!-- 
## Time comparison

<ins>monte-carlo-python</ins>
[repo](https://github.com/Mateuszq28/monte-carlo-sim-python)
*programming language: python*
homogeneous tissue
My sim time (monte-carlo-sim-python): 3895.3408 seconds (1h 5 min) for 1 mln photons

<ins>tiny_mc.c</ins>
*programming language: c*
original parameters 10 000 photons: 1.2420 seconds
original parameters 1 mln photons: 16.6361 seconds
my parameters on tiny 10 000 photons: 1.1717 seconds
my parameters on tiny 1 mln photons: 108.9439 seconds

<ins>small_mc.c</ins>
*programming language: c*
original parameters 10 000 photons: 1.1567 seconds
original parameters 100 000 photons: 3.4751 seconds
original parameters 1 mln photons: 26.5167 seconds
my parameters on small 10 000 photons: 1.7543 seconds
my parameters on small 100 000 photons: 8.9404 seconds
my parameters on small 1 mln photons: 86.9339 seconds

<ins>mc321_mc.c</ins>
*programming language: c*
original parameters 10 000 photons: 0.6321 seconds
original parameters 1 mln photons: 1.2259 seconds
my parameters on mc321 10 000 photons: 1.5611 seconds
my parameters on mc321 1 mln photons: 134.7727 seconds

<ins>mc321_p.py</ins>
*programming language: python*
original parameters 10 000 photons: 0.2350 seconds
original parameters 1 mln photons: 9.8403 seconds
my parameters on mc321 10 000 photons: 35.7755 seconds
my parameters on mc321 1 mln photons: 3910.4484 seconds (1h 5 min)

<ins>mc456_p.py</ins>
*programming language: python*
original parameters 10 000 photons: 10.8785 seconds
original parameters 1 mln photons: 19.1455 seconds
my parameters on mc456 10 000 photons: 55.4248 seconds
my parameters on mc456 1 mln photons: 4490.3612 seconds (1h 15 min)

<ins>mc456_mc.c</ins>
*programming language: python*
original parameters 10^4 = 10 000 photons: 11.0115 seconds
original parameters 10^5 = 100 000 photons: 11.3500 seconds
original parameters 10^6 = 1 mln photons: 12.0787 seconds
original parameters 10^7 = 10 mln photons: 14.1013 seconds
original parameters 10^8 = 100 mln photons: 15.6716 seconds
original parameters 10^9 = 1 mld photons: 287.5533 seconds (5 min)
my parameters on mc456 10^4 = 10 000 photons: 12.4692 seconds
my parameters on mc456 10^5 = 100 000 photons: 38.7502 seconds
my parameters on mc456 10^6 = 1 mln photons: 162.7858 seconds (2 min 43 s)
my parameters on mc456 10^7 = 10 mln photons: 1358.7487 seconds (23 min)
my parameters on mc456 10^8 = 100 mln photons: 13275.9499 seconds (3h 42 min)
-->

<!--
overflow and too less digits in print e notation
<ins>mc456_mc.c</ins>
*programming language: python*
original parameters 10^4 = 10 000 photons: 8.0297 seconds
original parameters 10^5 = 100 000 photons: 7.9869 seconds
original parameters 10^6 = 1 mln photons: 9.4164 seconds
original parameters 10^7 = 10 mln photons: 12.6733 seconds
original parameters 10^8 = 100 mln photons: 36.6226 seconds
original parameters 10^9 = 1 mld photons: 290.9062 seconds (5min)
my parameters on mc456 10^4 = 10 000 photons: 10.5652 seconds
my parameters on mc456 10^5 = 100 000 photons: 23.9545 seconds
my parameters on mc456 10^6 = 1 mln photons: 151.7471 seconds
my parameters on mc456 10^7 = 10 mln photons: 1356.2483 seconds (23 min)
my parameters on mc456 10^8 = 100 mln photons: 13290.7210 seconds (3h 42 min)
-->

<!-- ## Generator period

The period (or cycle length) of a base generator is defined as the maximum number of values that can be generated before the sequence starts to repeat. [[1]](#1)

#### tiny and small
<ins>c stdlib rand function perioid</ins>
*From documentation:*
POSIX requires that the period of the pseudo-random number generator used by rand be at least 2^32. [[2]](#2)
2^32 = 4 294 967 296

#### mc321
The authors used their own random number generator algorithm based on two books. Unfortunately, neither on the website, nor in the paper, nor in the code did they provide information on its period. However, we can assume that it was significantly larger than the generator period implemented in the rand function from the standard C library.

<ins>From the note included in the code, we can read:</ins>

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
 -->