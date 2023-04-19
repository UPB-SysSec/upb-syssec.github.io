#!/bin/sh

for f in *.drawio.svg
do
    infile="$f"
    outfile="${f%.drawio.svg}.dark.svg"
    sed \
        -e 's/rgb(0, 0, 0)/rgb(255, 255, 255)/g' \
        -e 's/fill="#000000"/fill="#ffffff"/g' \
        -e 's/stroke="#000000"/stroke="#ffffff"/g' \
        "$infile" > "$outfile"
done
