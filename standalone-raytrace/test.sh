#!/bin/sh
python3 main.py process ./models/three_squares.vtk ./models/three_squares.json ./gmat_data/ReportFile1.txt ./gmat_data/EclipseLocator1.txt ./three_squares_view_factors.vf
python3 main.py viewm ./models/three_squares.vtk ./models/three_squares.json
#python3 main.py viewvf ./models/three_squares.vtk ./three_squares_properties.json 2