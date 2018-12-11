for i in "1" "2" "3" "4" 
do
    echo $i
    python3 PuzzleGame.py test_data/Oblig3-Opg3-Test$i.txt out.txt
    diff out.txt test_data/Oblig3-Opg3-Test$i-svar.txt
done

