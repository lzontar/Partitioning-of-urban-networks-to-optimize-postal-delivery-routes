cd ./scripts

if %2.==. (
    python data-generation.py -o %1 -g
) else (
    python data-generation.py -o %1 -n %2 -g
)
if %2.==. (
    python road-distance.py -n %1
) else (
    python road-distance.py -n %2
)

cd..
