# ECE1512 Project B — From JPEG Image Restoration to Learned Image Compression

**University of Toronto · Digital Image Processing · Fall 2026**  
**Project repository:** https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression

This repository accompanies the IEEE-style Project B report. It provides the implementation, executed notebooks, checkpoints, configuration details, figures and evaluation outputs for two related tasks:

1. **JPEG artifact removal:** a residual convolutional neural network (CNN) improves the decoded JPEG image *without changing the original JPEG bitstream or bitrate*.
2. **Learned image compression:** a neural encoder–quantizer–decoder system encodes learned latent representations and is evaluated using actual compressed-file bitrate and reconstruction quality.

**Status of this draft:** The JPEG restoration instructions and reported settings below have been checked against the uploaded, executed notebook. The learned-compression reproducibility section will be finalized after its notebook, code, and configurations are reviewed. This draft is **not yet the final submission README**.

## Repository structure

```text
ECE1512_Student_Project/
├── README.md
├── .gitignore
├── requirements.txt
├── jpeg_restoration_notebook/
│   ├── JPEG_Restoration_Student.ipynb
│   ├── dataset.py                  # JPEG degradation, cropping, image pairs
│   ├── model.py                    # Residual restoration CNN
│   ├── train.py                    # Training-related helpers and CLI
│   ├── evaluate.py                 # Evaluation helpers and CLI
│   ├── metrics.py                  # PSNR and alternative SSIM helper
│   ├── checks.py                   # Mathematical and pipeline tests
│   ├── notebook_utils.py           # Split checks and data helpers
│   ├── requirements.txt
│   └── runs/
│       ├── spatial_only/
│       │   ├── best.pt             # Highest validation-PSNR checkpoint
│       │   ├── last.pt
│       │   ├── config.json
│       │   └── history.json
│       └── results/
│           ├── metrics_long.csv
│           ├── metrics_table.csv
│           ├── gains_over_jpeg.csv
│           ├── quality_curves.png
│           ├── training_curves.png
│           └── comparison_000_q*.png
├── dnn_compression_notebook/
│   ├── DNN_Compression_Student.ipynb
│   └── ...                         # Detailed experiment map: to be verified
└── data_1um_bicubic/               # LOCAL ONLY; excluded from Git
    ├── train/
    ├── val/
    └── test/
```

Some experimental outputs live in deeper subdirectories. See the saved `runs/` files for the exact experiment artifacts. Dataset files are intentionally **not distributed in the Git repository**, to avoid uploading the approximately 2 GB local dataset.

## Installation (Windows / PowerShell)

Use Python with compatible PyTorch support. The environment should include PyTorch, torchvision, torchmetrics, NumPy, Pillow, matplotlib, pandas, tqdm, and JupyterLab. The project requirements are minimum versions rather than a fully pinned environment lockfile; exact package versions may affect numerical reproducibility.

```powershell
git clone https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression.git
cd ece1512-Project-B-DNN-Based-Image-Compression

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install jupyterlab ipykernel
```

The notebooks can use CUDA when available; otherwise CPU execution is supported by the code but can be considerably slower. Run the JPEG notebook **from its own folder**, because its setup cell resolves the dataset relative to the notebook module.

## Dataset and split protocol

**Source:** [ADPPatches — LeonYe on Hugging Face](https://huggingface.co/datasets/LeonYe/ADPPatches), referenced in the provided JPEG notebook. The experiments used the prepared local `data_1um_bicubic` split layout; merely downloading the upstream dataset does not guarantee identical split membership.

Place the prepared data beside (not inside) the two notebook directories:

```text
data_1um_bicubic/
  train/
  val/
  test/
```

Image files may be nested inside these split directories. The JPEG loader recursively scans for `jpg`, `jpeg`, `png`, `bmp`, `tif`, `tiff`, and `webp` files. The executed dataset-check cell reported:

| Split | Images |
|---|---:|
| Train | 12,616 |
| Validation | 1,576 |
| Test | 1,576 |

The notebook calls `notebook_utils.check_split_overlap()`, which checks for **byte-identical images across these three splits using SHA-256**. This is not a patient-level or scene-level leakage test. For exact numerical replication, use the same prepared split and verify these counts before training. The current supplied materials do not include a portable, complete manifest of all source-image identities; the dataset version, license, and split provenance should be documented separately if available.

### JPEG preprocessing

- Convert source images to RGB and normalize the resulting tensors to `[0,1]`.
- Use `256 × 256` crops for the reported experiments. Images smaller than the crop are resized with bicubic interpolation before cropping.
- **Training:** random crop, independent horizontal/vertical flips (50% chance each), and a randomly selected JPEG quality from `Q = {10,20,30,40,50}` for each sample.
- **Validation/test:** deterministic center crop and no random flips. The test loop evaluates each JPEG quality separately on all 1,576 held-out images.
- Construct the degraded input by JPEG-encoding the clean crop and then decoding it, with Pillow settings `quality=Q`, `subsampling=0` (**4:4:4**), and `optimize=False`.
- Use the exact same clean crop and JPEG-decoded input when comparing the raw JPEG baseline with CNN restoration.

## Part 1 — Reproduce JPEG restoration

### Authoritative reproduction path: the executed notebook

From the repository root, start Jupyter in the restoration module:

```powershell
cd jpeg_restoration_notebook
..\.venv\Scripts\python.exe -m jupyter lab
```

Open **[`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb)** in the Jupyter interface, select the Python environment created above, and run cells in order.

The notebook's configuration cell should have the following settings for the **reported run**:

```python
MODE = "full"
DATA_ROOT = PROJECT_DIR.parent / "data_1um_bicubic"
OUTPUT_ROOT = Path("runs")
TRAIN_MODELS = True             # Retrain; set to False to reuse a saved checkpoint
NUM_WORKERS = 0
SEED = 42
TRAIN_QUALITIES = [10, 20, 30, 40, 50]
TEST_QUALITIES = [10, 15, 20, 25, 30, 40, 50]

CFG = {
    "train_dir": str(DATA_ROOT / "train"),
    "val_dir": str(DATA_ROOT / "val"),
    "test_dir": str(DATA_ROOT / "test"),
    "epochs": 3,
    "batch_size": 16,
    "patch_size": 256,
    "eval_patch_size": 256,
    "channels": 32,
    "depth": 5,
    "qualities": TRAIN_QUALITIES,
    "lr": 2e-4,
    "num_workers": 0,
    "seed": 42,
}
```

For evaluation **without retraining**, set `TRAIN_MODELS = False` while retaining the other protocol settings and ensure `runs/spatial_only/best.pt` exists. Run the notebook in order; it loads the checkpoint, evaluates the chosen test qualities, and saves figures/tables. Its embedded correctness-check cell should print `All correctness checks passed.` A GPU was used for the originally executed training run; the exact accelerator/software package build is not fully pinned by the provided requirements files.

**Why use the notebook instead of the starter shell script?** The executed notebook defines the specific 3-epoch, 256-pixel, 7-quality evaluation used in the report. The stand-alone script defaults and paths are different, so `run_experiments.sh` is **not an exact reproduction command for the reported results**. The standalone `train.py` CLI should not be treated as the validated reproduction path until its implementation is corrected and tested.

### Restoration model and training settings

| Setting | Value / implementation |
|---|---|
| Model | Five `3×3` convolution layers, 32 hidden channels, four ReLU activations |
| Trainable parameters | 29,507 |
| Output | `clip(y + f_theta(y), 0, 1)` for decoded JPEG input `y` |
| Objective | Mean absolute error (spatial L1) against the clean RGB crop |
| Optimizer | AdamW, learning rate `2e-4`, weight decay `1e-4` |
| Schedule | Cosine annealing over 3 epochs |
| Epochs / batch size | 3 / 16 |
| Training random seed | 42 (Python, NumPy, PyTorch, CUDA when present) |
| Checkpoint selection | Highest restored **validation PSNR**, saved as `runs/spatial_only/best.pt` |
| Final evaluation | Held-out test split; no test-driven checkpoint selection |

The executed notebook logged 789 mini-batches per epoch. Validation restored PSNR increased over the three epochs to approximately **31.42 dB**, so the baseline is computationally limited rather than demonstrably converged.

### Metric definitions and rate accounting

- **PSNR:** compute per-image RGB mean squared error with pixel range `[0,1]`, convert to dB, then average the image scores. The implementation clamps MSE below `1e-10`, capping the perfect-match score at 100 dB.
- **SSIM for the reported notebook results:** custom RGB SSIM using an `11×11` Gaussian kernel with `sigma=1.5`, `C1=(0.01)^2`, and `C2=(0.03)^2`; average across batch, channels and valid spatial positions. This notebook implementation is the reference for the table below. The separate `metrics.py` uses a TorchMetrics SSIM implementation, which should not automatically be assumed numerically identical.
- **JPEG BPP:** measured from the actual JPEG bytes for the clean `256×256` crop, *including file headers*, using `8 × JPEG_file_bytes / (256 × 256)`. Encode with `subsampling=0`, `optimize=False` and the evaluated `Q`.
- **Restoration bitrate:** JPEG post-processing changes only the decoded pixels, not the stored JPEG bitstream. The CNN and JPEG baseline thus have the **same input JPEG BPP at a given Q**. Do not substitute the size of a saved PNG restoration image for the original JPEG bitstream bitrate.

### Reported held-out test results

These values are transcribed from the **executed** `JPEG_Restoration_Student.ipynb` and correspond to 1,576 center crops at each quality factor:

| JPEG Q | Input BPP | JPEG PSNR (dB) | CNN PSNR (dB) | JPEG SSIM | CNN SSIM |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.6002 | 26.3657 | 28.2078 | 0.7708 | 0.8298 |
| 15 | 0.7465 | 27.8539 | 29.8326 | 0.8122 | 0.8668 |
| 20 | 0.8787 | 28.8730 | 30.8611 | 0.8378 | 0.8869 |
| 25 | 1.0040 | 29.6422 | 31.5748 | 0.8553 | 0.8994 |
| 30 | 1.1187 | 30.2382 | 32.0939 | 0.8681 | 0.9078 |
| 40 | 1.3186 | 31.1346 | 32.8180 | 0.8858 | 0.9184 |
| 50 | 1.5075 | 31.8450 | 33.3319 | 0.8985 | 0.9252 |

`Q=15` and `Q=25` are **unseen during training**; `Q=10,20,30,40,50` are seen training qualities, evaluated on new held-out images. The improvements are reconstruction-quality gains **at unchanged JPEG input BPP**, not evidence of new compression efficiency.

### Where to find generated outputs

| Repository-relative path | Contents |
|---|---|
| [`jpeg_restoration_notebook/runs/spatial_only/`](jpeg_restoration_notebook/runs/spatial_only/) | `best.pt`, `last.pt`, configuration and optimization history |
| [`jpeg_restoration_notebook/runs/results/`](jpeg_restoration_notebook/runs/results/) | Per-quality metrics CSVs, quality curves, training curves, qualitative reconstructions |
| [`jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb) | Executed notebook with setup, checks, training, evaluation, and plots |

For a fresh run, these artifacts are written or overwritten under the corresponding `runs/` folders. Training results can vary with hardware, library versions and sources of nondeterminism even when a seed is fixed.

## Part 2 — Learned image compression

> **To be completed after code review.** The repository already contains `dnn_compression_notebook/DNN_Compression_Student.ipynb` and supporting code/results, but this README draft intentionally does not assert details that have not yet been verified against the provided DNN files.

The completed section will document **the exact executed run**: encoder/decoder architecture, latent sizes, codebook sizes and initialization, differentiable training quantization, hard nearest-codeword assignment at evaluation, entropy coding, checkpoint/context requirements, output file format, true measured file BPP, test-set image sizes, random seeds, tested lambda values, controlled ablations, index-to-reconstruction checks, JPEG comparison settings, exact reproduction commands, and experiment-to-figure mapping.

## Reproducibility checklist and limitations

The project uses the [NeurIPS Paper Checklist](https://neurips.cc/Conferences/2021/PaperInformation/PaperChecklist) as a transparency guide. The following status describes the **currently verified JPEG restoration experiment**; compression items remain pending until their code is reviewed.

| Requirement | Restoration status | Learned compression status |
|---|---|---|
| Source code and executed notebook | Included | Pending verification |
| Dependency list | Included; lower bounds, not exact lock | Pending verification |
| Dataset source and local path | Documented | Pending verification |
| Split counts and leakage check | Documented; SHA-256 exact-duplicate check | Pending verification |
| Exact image crop/resize protocol | Documented | Pending verification |
| JPEG quality and encode settings | Documented | Pending verification |
| Random seed and model hyperparameters | Documented | Pending verification |
| Checkpoint choice and test protocol | Documented | Pending verification |
| Metrics and bitrate definition | Documented | Pending verification |
| Stored codebook indices and decoding integrity | Not applicable | Pending verification |
| Rate–distortion ablations | Not applicable | Pending verification |
| Multiple-seed uncertainty/error bars | Not provided in the verified experiment | Pending verification |

**Known limitations:** The restoration run uses one seed and three epochs; exact numerical reproducibility depends on obtaining the original prepared splits and a compatible software/hardware environment. The present exact-duplicate check does not establish patient-level independence. Dataset files are intentionally excluded from GitHub; evaluators need access to the underlying data. The readme does not claim that every standalone CLI helper is an independently validated reproduction route.

## Relationship to the report

The IEEE-style Project B report describes the same training/evaluation protocol and includes figures corresponding to the files in `jpeg_restoration_notebook/runs/results/`. The report should include a URL to this repository, identify the tested commit, and use the same image counts, crop sizes, quality factors, seed, PSNR/SSIM conventions and BPP definitions. The compression results and their links will be synchronized with the report after Part 2 has been verified.

**References:** The source dataset is identified in the original notebook as [LeonYe/ADPPatches](https://huggingface.co/datasets/LeonYe/ADPPatches). Reproducibility reporting guidance: [NeurIPS 2021 Paper Checklist](https://neurips.cc/Conferences/2021/PaperInformation/PaperChecklist). See the accompanying report for academic references on JPEG artifact removal, learned compression and RDVQ.
