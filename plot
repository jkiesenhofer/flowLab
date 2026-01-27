set terminal pngcairo size 800,600
set output "stokes.png"

set xlabel "dp"
set ylabel "K"

set xtics 0, 0.00005, 0.0001     # Start, Schritt, Ende
set ytics 0, 1, 7
set mxtics 5
set format x "%.5f"
set multiplot layout 2,2

plot "stokes.dat" using 1:2 with lines title "Ua", \
     "stokes.dat" using 1:3 with lines title "Ub", \
     "stokes.dat" using 1:4 with lines title "Uc"

set ylabel "K"
set xtics auto #0, 0.00005, 0.0001
set ytics auto
set mytics 2
set mxtics 10
set logscale x
set xlabel "Re"
plot "stokes.dat" using 1:5 with lines title "dp=0.1mm"


plot "stokes.dat" using 1:2 with lines title "Ua", \
     "stokes.dat" using 1:3 with lines title "Ub", \
     "stokes.dat" using 1:4 with lines title "Uc"

set ylabel "K"
set xtics auto #0, 0.00005, 0.0001
set ytics auto
set mytics 2
set mxtics 10
set logscale x
set xlabel "Re"
plot "stokes.dat" using 1:5 with lines title "dp=0.1mm"


unset multiplot

set output
