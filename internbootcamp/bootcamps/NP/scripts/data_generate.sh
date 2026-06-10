#! /bin/bash

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/gcp_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/hamiltonian_cycle_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/knapsack_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/maximum_clique_problem_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/maximum_set_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/meeting_schedule_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/minimum_cut_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/set_cover_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/NP/configs/subset_sum_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/NP/data \
    --split-samples train:10,test:10 \
    --shuffle

# python -m internbootcamp.utils.data_generation \
#     --instruction-config internbootcamp/bootcamps/NP/configs/TSP_instruction_config.yaml \
#     --output-dir internbootcamp/bootcamps/NP/data \
#     --split-samples train:10,test:10 \
#     --shuffle


