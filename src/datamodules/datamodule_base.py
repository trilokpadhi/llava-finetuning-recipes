import torch

from pytorch_lightning import LightningDataModule
from torch.utils.data import DataLoader
from transformers import (
    DataCollatorForLanguageModeling,
    DataCollatorForWholeWordMask,
    AutoTokenizer,
)


def get_pretrained_tokenizer(from_pretrained):
    if torch.distributed.is_initialized():
        if torch.distributed.get_rank() == 0:
            AutoTokenizer.from_pretrained(from_pretrained)
        torch.distributed.barrier()

    return AutoTokenizer.from_pretrained(from_pretrained)


class BaseDataModule(LightningDataModule):
    def __init__(self, _config):
        super().__init__()

        self.data_dir = _config["data_root"]

        self.num_workers = _config["num_workers"]
        self.batch_size = _config["per_gpu_batchsize"]
        self.eval_batch_size = self.batch_size

        self.image_size = _config["image_size"]
        self.patch_size = _config["patch_size"]
        self.max_text_len = _config["max_text_len"]

        self.train_transform_keys = (
            ["default_train"]
            if len(_config["train_transform_keys"]) == 0
            else _config["train_transform_keys"]
        )

        self.val_transform_keys = (
            ["default_val"]
            if len(_config["val_transform_keys"]) == 0
            else _config["val_transform_keys"]
        )

        tokenizer = _config["tokenizer"]
        self.tokenizer = get_pretrained_tokenizer(tokenizer)
        self.vocab_size = self.tokenizer.vocab_size

        collator = (
            DataCollatorForWholeWordMask
            if _config["whole_word_masking"]
            else DataCollatorForLanguageModeling
        )

        self.mlm_collator = collator(
            tokenizer=self.tokenizer, mlm=False, mlm_probability=_config["mlm_prob"]
        )
        self.setup_flag = False

    @property
    def dataset_cls(self):
        raise NotImplementedError("return tuple of dataset class")

    @property
    def dataset_name(self):
        raise NotImplementedError("return name of dataset")

    def set_train_dataset(self):
        self.train_dataset = self.dataset_cls(
            data_dir=self.data_dir,
            transform_keys=self.train_transform_keys,
            split="train",
            image_size=self.image_size,
            patch_size=self.patch_size,
            max_text_len=self.max_text_len,
            tokenizer=self.tokenizer,
        )

    def set_val_dataset(self):
        self.val_dataset = self.dataset_cls(
            data_dir=self.data_dir,
            transform_keys=self.val_transform_keys,
            split="val",
            image_size=self.image_size,
            patch_size=self.patch_size,
            max_text_len=self.max_text_len,
            tokenizer=self.tokenizer,
        )

    def set_test_dataset(self):
        self.test_dataset = self.dataset_cls(
            data_dir=self.data_dir,
            transform_keys=self.val_transform_keys,
            split="test",
            image_size=self.image_size,
            patch_size=self.patch_size,
            max_text_len=self.max_text_len,
            tokenizer=self.tokenizer,
        )
    
    def make_val_dset(self, image_only=False):
        return self.dataset_cls(
            data_dir=self.data_dir,
            transform_keys=self.val_transform_keys,
            split="test",
            image_size=self.image_size,
            patch_size=self.patch_size,
            max_text_len=self.max_text_len,
            image_only=image_only,
            tokenizer=self.tokenizer,
        )

    def setup(self, stage):
        if not self.setup_flag:
            self.set_train_dataset()
            self.set_val_dataset()
            self.set_test_dataset()

            self.train_dataset.tokenizer = self.tokenizer
            self.val_dataset.tokenizer = self.tokenizer
            self.test_dataset.tokenizer = self.tokenizer

            self.setup_flag = True

    def train_dataloader(self):
        loader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=self.train_dataset.collate,
            drop_last=False,
        )
        return loader

    def val_dataloader(self):
        loader = DataLoader(
            self.val_dataset,
            batch_size=self.eval_batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=self.val_dataset.collate,
            drop_last=False
        )
        return loader

    def test_dataloader(self):
        loader = DataLoader(
            self.test_dataset,
            batch_size=self.eval_batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=self.test_dataset.collate,
            drop_last=False
        )
        return loader
