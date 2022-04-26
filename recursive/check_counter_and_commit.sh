#!/bin/bash

COUNTER_FILE=./recursive/counter.txt

count=$(cat "$COUNTER_FILE") 
if (( $count > 3 ));
then 
    echo "Count too high... Exit";
else
    echo "Count okay... Continue";
    echo $(( $count + 1 )) > $COUNTER_FILE
    git config --global user.email "sjuanandres0@gmail.com"
    git config --global user.name "Chewie"
    git add -A #$COUNTER_FILE
    git commit -m "TDS updated"
    git push 
fi; 