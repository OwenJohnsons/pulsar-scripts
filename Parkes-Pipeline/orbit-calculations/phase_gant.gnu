set xrange [0:1] 
set yrange [0.5:6.5]
set ytics ("221113_123605" 1, "221114_112944" 2, "221109_114040" 3, \
           "221116_111800" 4, "221115_160130" 5, "221118_111155" 6)
set style fill solid 0.5
set boxwidth 0.8
set xlabel "Phase"
set ylabel "Patterns"

# Plot
plot "gantt_data.txt" using 2:($0+1):($3-$2) with boxes title ""
