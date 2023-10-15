labels=("10" "20" "30" "35" "36" "37" "38" "39" "40" "41" "45" "49")
echo "" > out.txt

for i in {1..12}
do
    echo ${labels[$i - 1]} >> out.txt
    python3 main.py fruitchain --config "configs/1/cfg_1_$i.yaml"
    python3 res_count.py >> out.txt
    echo "" >> out.txt; echo "" >> out.txt;
done