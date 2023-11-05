#!/bin/bash

actions=("pancake" "salat" "friedegg" "scrambledegg" "sandwich" "juice" "milk" "tea" "cereals" "coffee")
clusters=(14 8 9 12 9 8 5 7 5 7)
seed=0
gpu=1

for i in ${!actions[@]}; do
	python3 train.py -d Breakfast -ac ${actions[$i]} -c ${clusters[$i]} -ne 15 -g $gpu --seed 0 --group main_results --rho 0.15 -ut 0.05 -vf 5 -lr 1e-3 -wd 1e-4 -r 0.04 --wandb -s -at 0.4 -ae 0.4
done