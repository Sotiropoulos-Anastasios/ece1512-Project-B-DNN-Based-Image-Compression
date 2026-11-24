# ECE1512 Project B — Code Completeness / Reproducibility Checklist

**Artifact:** [Project B GitHub code repository](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression).  
**Companion artifact:** IEEE-style Project B PDF report, submitted separately through ECE1512 Quercus.  
**Basis:** The course's [Machine Learning Reproducibility Checklist v2.0](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf).  
**Scope:** This file concerns the **code, trained checkpoints, figures, configuration records and independent use of the repository**, not completeness of claims in the submitted PDF. See the separate [paper checklist](PAPER_REPRODUCIBILITY.md).  


| Code completeness item | Status | Evidence / limitation |
|---|---|---|
| **1. Dependencies / installation** | **Partial** | Root and subproject `requirements.txt` files are supplied, and `README.md` documents Windows PowerShell/Jupyter setup. Dependencies use lower bounds rather than a fully pinned Python/PyTorch/CUDA environment or lockfile. |
| **2. Training implementation** | **Yes** | Both executed notebooks include the reported training logic; DNN [`engine.py`](dnn_compression_notebook/engine.py), [`warm_start.py`](dnn_compression_notebook/warm_start.py) and [`data.py`](dnn_compression_notebook/data.py) support baseline and ablation runs. |
| **3. Evaluation implementation** | **Yes** | JPEG [`evaluate.py`](jpeg_restoration_notebook/evaluate.py), notebook metrics/figures, and DNN [`comparison.py`](dnn_compression_notebook/comparison.py), [`codec.py`](dnn_compression_notebook/codec.py), [`q4_evaluation_cell.py`](dnn_compression_notebook/q4_evaluation_cell.py) implement PSNR, SSIM, JPEG byte counts, hard-index bitstreams, decoding and full-file measured-rate ablations.  |
| **4. (Pre)trained model weights** | **Yes** | Initial Git staging/commit log included JPEG [`runs/spatial_only/best.pt`](jpeg_restoration_notebook/runs/spatial_only/best.pt) and DNN [`runs/solution_larger_20261123_050247_803626/best.pt`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/best.pt), with `last.pt` and rate-weight/codebook-size ablation weights.  |
| **5. Results and reproduction instructions** | **Partial** | [`README.md`](README.md) contains setup, run choices, metric tables and paths to CSV/JSON/figures; notebooks have saved cell outputs. The ~2 GB dataset is external, the manifest records an absolute Windows dataset path, and saved sweep JSONs contain absolute checkpoint paths. |

## Notebooks and supporting modules: what each demonstrates

| Notebook / entry point | Reproduction role |
|---|---|
| [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb) | Primary JPEG restoration training/evaluation path: RGB crops, online JPEG degradation, residual CNN, validation-selected `best.pt`, held-out PSNR/SSIM and measured source JPEG BPP. |
| [`jpeg_restoration_notebook/dataset.py`](jpeg_restoration_notebook/dataset.py) + [`evaluate.py`](jpeg_restoration_notebook/evaluate.py) | Repeatable crop/degradation rules (`quality=Q`, 4:4:4, `optimize=False`) and checkpoint evaluation by Q. The notebook defines the exact reported 7-Q test. |
| [`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb) | Main learned-compression workflow: soft-VQ student implementation, model tests, warm start, training, rate-weight/codebook ablations, validation/test results, JPEG comparisons and Q4 measured-rate evaluation. |
| [`dnn_compression_notebook/model.py`](dnn_compression_notebook/model.py) + [`engine.py`](dnn_compression_notebook/engine.py) | Compact single-scale residual encoder–decoder, trainable codebook/global prior, hard-index inference and RD optimization with validation-selected checkpoints. |
| [`codec.py`](dnn_compression_notebook/codec.py) + [`arithmetic.py`](dnn_compression_notebook/arithmetic.py) + [`checks.py`](dnn_compression_notebook/checks.py) | Serialize integer VQ indices into `.ecvq` streams, decode using matching checkpoint, and test soft-VQ gradients / index bitstream round trips. |
| [`comparison.py`](dnn_compression_notebook/comparison.py) + [`q4_evaluation_cell.py`](dnn_compression_notebook/q4_evaluation_cell.py) | Fair JPEG-vs-DNN evaluation on the same images; distinguish latent payload from complete-file bytes; compare baseline and independently trained ablations. |

## Dataset availability and expected layout

The original image source is [LeonYe/ADPPatches on Hugging Face](https://huggingface.co/datasets/LeonYe/ADPPatches). The approximately **2 GB prepared `data_1um_bicubic/` directory is intentionally excluded from GitHub**. Obtain the dataset from its provider and arrange the **prepared training, validation and test folders** beside the notebook directories:

```text
ECE1512_Student_Project/
├── README.md
├── PAPER_REPRODUCIBILITY.md
├── CODE_REPRODUCIBILITY.md
├── jpeg_restoration_notebook/
├── dnn_compression_notebook/
└── data_1um_bicubic/              # local, excluded by .gitignore
    ├── train/
    ├── val/
    └── test/
```

The prepared splits contain **12,616 / 1,576 / 1,576 images**. The DNN experiments do **not** use all prepared examples: their selected working subsets are **1,024 train, 128 validation and 256 test**, sampled deterministically with seed `1512` and recorded in a run's `data_protocol.json`. 

## Exact execution path available in the repository

1. Follow [`README.md`](README.md) to create the Python environment and install `requirements.txt`. The dependencies are not version-locked; use a compatible PyTorch build and record actual package versions for any new rerun.
2. Place the prepared external dataset as shown above. Open Jupyter using a working directory compatible with each notebook's relative `data_1um_bicubic` resolution.
3. **JPEG restoration:** open [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb). For training, use the executed notebook's 256×256, seed-42, 3-epoch/batch-16 settings and Q set `{10,20,30,40,50}`. The model is selected by validation restored PSNR. For evaluation without retraining, set `TRAIN_MODELS=False`, load `runs/spatial_only/best.pt`, and evaluate test Q `{10,15,20,25,30,40,50}`. The reported source-JPEG BPP uses the original encoded file bytes; the CNN does not change it.
4. **DNN baseline training:** open [`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb); use `MODE='larger'`, `SEED=1512`, `USE_WARM_START=True`, `REUSE_CHECKPOINT=None`, baseline `K=256`, `latent_dim=16`, `width=64`, `levels=1`, `λ=0.0001`, 8 continuous warm-up epochs and 40 optimization epochs. The run writes a newly timestamped `runs/solution_larger_*/` directory. Select `best.pt` using the lowest validation RD objective—not test PSNR.


## Known reproducibility limitations 

- **Dataset:** the prepared ~2 GB images are not in Git. The public dataset link and required folder layout are given.
- **Environment:** minimum dependency versions are available, but there is no complete locked OS/CUDA/PyTorch environment or tested fresh-clone script.
