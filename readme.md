# LLaVA Fine-Tuning Guide

## 1. Steps to finetune llava on a test dataset
```bash
git clone https://github.com/haotian-liu/LLaVA.git
```
## 2. Please follow setup instructions from the above repository to create the environment
```
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
conda create --name LLaVA python=3.10.12
conda activate LLaV
pip install -e .
pip install flash-attn --no-build-isolation
conda install conda-forge::deepspeed
```
## 3. Create a demo dataset and train llava
### Please update the dataset paths in bash finetune_llava.sh

```
python create_data_to_finetune_llava_test.py
bash finetune_llava.sh
```




