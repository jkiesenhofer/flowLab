set terminal pngcairo size 800,600
set output "stokes.png"

set title "Bubble follows the flow"
set xlabel "dp"
set ylabel "St"
plot "stokes.dat" with lines title "ρ=2500, μ = 1.8d-5 "

set output
