#!/bin/bash

# Set root directory and dataset directory variables
ROOT_DIR="/staging/users/tpadhi1/toxicity_kidvlm/ExplainHM-WWW2024/LLaVA"
DATASET_DIR="/staging/users/tpadhi1/toxicity_kidvlm/ExplainHM-WWW2024/hate_speech_dataset"


# Set the prompt and model versions directly in the command
deepspeed "$ROOT_DIR/llava/train/train_mem.py" \
    --deepspeed "$ROOT_DIR/scripts/zero2.json" \
    --lora_enable True \
    --lora_r 128 \
    --lora_alpha 256 \
    --mm_projector_lr 2e-5 \
    --bits 4 \
    --model_name_or_path "llava-hf/llava-1.5-7b-hf" \
    --version llava_llama_2 \
    --data_path "$DATASET_DIR/train/dataset.json" \
    --image_folder "$DATASET_DIR/images/" \
    --vision_tower openai/clip-vit-large-patch14-336 \
    --mm_projector_type mlp2x_gelu \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --image_aspect_ratio pad \
    --group_by_modality_length True \
    --bf16 True \
    --output_dir "$ROOT_DIR/llava/checkpoints/llama-2-7b-chat-task-qlora" \
    --num_train_epochs 50 \
    --per_device_train_batch_size 32 \
    --per_device_eval_batch_size 32 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 50000 \
    --save_total_limit 1 \
    --learning_rate 2e-4 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --dataloader_num_workers 4 \
    --lazy_preprocess True \
    --report_to wandb
