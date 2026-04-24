#!/bin/bash

# --- 1. Configuration ---
VTK_FILE="flotation7_1063.vtk"
DATA_FILE="flotation_data.dat"
OUTPUT_IMG="alpha_contour_black.png"

echo "Step 1: Extracting data from $VTK_FILE..."

# --- 2. Inline Python Extraction ---
# This creates the .dat file without needing a separate .py file
python3 <<EOF
import vtk
import numpy as np

try:
    reader = vtk.vtkGenericDataObjectReader()
    reader.SetFileName("$VTK_FILE")
    reader.Update()
    data = reader.GetOutput()

    points = data.GetPoints()
    # Attempt to get alpha.water; adjust string if your field name varies
    field_name = "alpha.water"
    alpha = data.GetPointData().GetArray(field_name)

    if not alpha:
        print(f"Error: Could not find field '{field_name}' in VTK file.")
        exit(1)

    with open("$DATA_FILE", "w") as f:
        for i in range(points.GetNumberOfPoints()):
            p = points.GetPoint(i)
            # Writing X, Y, and alpha.water value
            f.write(f"{p[0]} {p[1]} {alpha.GetValue(i)}\n")
    print("Extraction successful.")
except Exception as e:
    print(f"Python Error: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then echo "Extraction failed. Exiting."; exit 1; fi

echo "Step 2: Generating Gnuplot contour..."

# --- 3. Inline Gnuplot Execution ---
gnuplot <<EOF
set terminal pngcairo size 1000,1000
set output "$OUTPUT_IMG"

set dgrid3d 120,120          # Resolution of the interpolation grid
set contour base
set cntrparam level auto 6   # Fewer levels = cleaner black & white look
set cntrparam bspline
unset surface
set view map

unset colorbox
set style line 1 lc rgb "black" lw 1.2
set cntrlabel font ",9" format "%g" interval 50

set title "Contour Map: alpha.water (File: $VTK_FILE)"
set xlabel "X-axis"
set ylabel "Y-axis"

# Plotting lines and labels
splot "$DATA_FILE" using 1:2:3 with lines linestyle 1 notitle, \
      "$DATA_FILE" using 1:2:3 with labels notitle
EOF

echo "Done! Visualization saved to $OUTPUT_IMG"
