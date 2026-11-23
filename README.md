# ECE1512 Project B — From JPEG Image Restoration to Learned Image Compression

**University of Toronto · Digital Image Processing · Fall 2026**  
**Project repository:** https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression

This repository accompanies the IEEE-style Project B report. It provides the implementation, executed notebooks, checkpoints, configuration details, figures and evaluation outputs for two related tasks:

1. **JPEG artifact removal:** a residual convolutional neural network (CNN) improves the decoded JPEG image *without changing the original JPEG bitstream or bitrate*.
2. **Learned image compression:** a neural encoder–quantizer–decoder system encodes learned latent representations and is evaluated using actual compressed-file bitrate and reconstruction quality.

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
│   ├── DNN_Compression_Student.ipynb   # Implemented/executed compression notebook
│   ├── model.py                        # Encoder, decoder, VQ codebook, learned prior
│   ├── data.py                         # Dataset splits, center crops, seeded loaders
│   ├── engine.py                       # Training, checkpoint loading, validation
│   ├── checks.py                       # Quantizer and decoder round-trip checks
│   ├── codec.py                        # ECV1/ECV2 index bitstream serialization
│   ├── arithmetic.py                   # Lossless causal arithmetic coder
│   ├── entropy_context.py              # Optional trained context tables
│   ├── comparison.py                   # JPEG comparison and actual byte counts
│   ├── metrics.py                      # RGB SSIM reference
│   ├── warm_start.py                   # Continuous warm-up and k-means codebook init
│   ├── q4_evaluation_cell.py           # Measured-rate ablations + reconstructions
│   ├── requirements.txt
│   └── runs/
│       ├── shared_data_splits.json     # Saved split manifest; original local root
│       ├── solution_larger_20261123_050247_803626/
│       │   ├── best.pt                 # Baseline validation-selected checkpoint
│       │   ├── config.json / history.csv / warmup.json
│       │   ├── data_protocol.json / test_metrics.json
│       │   ├── validation_sweep.json / codebook_sweep.json
│       │   ├── jpeg_comparison/         # Serialized .ecvq examples + JPEG comparison
│       │   ├── dense_jpeg_comparison/   # JPEG Q1–Q95 sweep
│       │   └── q4_ablation_results/    # Full-file-bpp plots, CSVs, reconstructions
│       ├── sweep_*/                     # Independent rate-weight checkpoints
│       └── codebook_k*/                 # Independent codebook-size checkpoints
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

**Source:** [ADPPatches — LeonYe on Hugging Face](https://huggingface.co/datasets/LeonYe/ADPPatches), referenced in the provided JPEG notebook. The experiments used the prepared local `data_1um_bicubic` split layout. 

Place the prepared data beside (not inside) the two notebook directories:

```text
data_1um_bicubic/
  train/
  val/
  test/
```

The executed dataset-check cell reported:

| Split | Images |
|---|---:|
| Train | 12,616 |
| Validation | 1,576 |
| Test | 1,576 |

### JPEG preprocessing

- Convert source images to RGB and normalize the resulting tensors to `[0,1]`.
- Use `256 × 256` crops for the reported experiments. Images smaller than the crop are resized with bicubic interpolation before cropping.
- **Training:** random crop, independent horizontal/vertical flips (50% chance each), and a randomly selected JPEG quality from `Q = {10,20,30,40,50}` for each sample.
- **Validation/test:** deterministic center crop and no random flips. The test loop evaluates each JPEG quality separately on all 1,576 held-out images.
- Construct the degraded input by JPEG-encoding the clean crop and then decoding it, with Pillow settings `quality=Q`, `subsampling=0` (**4:4:4**), and `optimize=False`.
- Use the exact same clean crop and JPEG-decoded input when comparing the raw JPEG baseline with CNN restoration.

## Part 1 — Reproduce JPEG restoration


Open **[`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb)** in the Jupyter interface, select the correct Python environment and run cells in order.


For evaluation **without retraining**, set `TRAIN_MODELS = False`. The executed notebook defines the specific 3-epoch, 256-pixel, 7-quality evaluation used in the report. 

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
- **SSIM for the reported notebook results:** custom RGB SSIM using an `11×11` Gaussian kernel with `sigma=1.5`, `C1=(0.01)^2`, and `C2=(0.03)^2`; average across batch, channels and valid spatial positions. 
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

`Q=15` and `Q=25` are **unseen during training**; `Q=10,20,30,40,50` are seen training qualities, evaluated on new held-out images. 

### Where to find generated outputs

| Repository-relative path | Contents |
|---|---|
| [`jpeg_restoration_notebook/runs/spatial_only/`](jpeg_restoration_notebook/runs/spatial_only/) | `best.pt`, `last.pt`, configuration and optimization history |
| [`jpeg_restoration_notebook/runs/results/`](jpeg_restoration_notebook/runs/results/) | Per-quality metrics CSVs, quality curves, training curves, qualitative reconstructions |
| [`jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb) | Executed notebook with setup, checks, training, evaluation, and plots |


## Part 2 — Reproduce learned image compression

Open **[`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb)** in Jupyter and run its cells in order. The notebook implements the differentiable quantizer and PSNR/SSIM metrics; the companion Python files implement the compact encoder–decoder, training loop, bitstream coder, JPEG evaluation, and controlled ablations.

This is a **compact, single-scale, RDVQ-inspired educational implementation**. It demonstrates trainable vector quantization and rate–distortion optimization; it is **not a reproduction of every architectural component or every published result** of Jiang *et al.* (CVPR 2026). Refer to the [RDVQ paper](https://openaccess.thecvf.com/content/CVPR2026/html/Jiang_Differentiable_Vector_Quantization_for_Rate-Distortion_Optimization_of_Generative_Image_Compression_CVPR_2026_paper.html) for the full proposed method.

### Run the DNN notebook

From the repository root (after completing **Installation** and placing the local dataset as described above):

```powershell
cd dnn_compression_notebook
..\.venv\Scripts\python.exe -m jupyter lab
```

Open `DNN_Compression_Student.ipynb` in the browser and select the environment's Python kernel. Its first setup cell finds `model.py` relative to the working directory and expects the dataset at `../data_1um_bicubic/`.

**To reproduce the full experiment from training**, leave the executed notebook settings in Step 1/2 and Step 5/6: `MODE = 'larger'`, `SEED = 1512`, `USE_WARM_START = True`, `REUSE_CHECKPOINT = None`, `RUN_SWEEP = True`, and `RUN_CODEBOOK_SWEEP = True`. This trains a baseline, three rate-weight variants, and three codebook-size variants; results are written into newly timestamped run directories rather than overwriting the original runs. Run the test, JPEG-comparison, and Question 4 cells after model selection. Training was performed on CUDA in the supplied execution log; runtime and final scores may vary with hardware and package versions.

**To evaluate the already saved baseline without retraining**, use the following in the Step 5 cell:

```python
REUSE_CHECKPOINT = PROJECT_DIR / 'runs' / 'solution_larger_20261123_050247_803626' / 'best.pt'
```

Set `RUN_SWEEP = False` and `RUN_CODEBOOK_SWEEP = False` in the two ablation-training cells, and run the test and JPEG-comparison cells normally. **Work in a separate local clone or back up the original run folder first:** even the checkpoint-reuse branch writes `data_protocol.json`, and later evaluation cells write figures/CSVs inside `RUN_DIR`. The Question 4 cell can also re-evaluate the ablation checkpoints, but requires the saved sweep-JSON checkpoint paths to be valid on your computer; see **Portability notes** below.

### Compression dataset, image preprocessing, and fixed test protocol

The DNN uses the same prepared local `data_1um_bicubic/{train,val,test}/` dataset described in **Dataset and split protocol**, but its reported experiment trains on smaller **fixed subsets** instead of every available image.

| Setting | Executed DNN protocol |
|---|---|
| Original prepared split folders | 12,616 train / 1,576 validation / 1,576 test |
| Images used for DNN training | 1,024, selected with a seeded shuffle of the prepared training folder |
| Images used for DNN validation | 128, selected with a seeded shuffle of the prepared validation folder |
| Images used for reported DNN testing | 256 distinct held-out test images, selected as `all_test_paths[128:384]` after the deterministic shuffle |
| Split / sampling seed | `SEED = 1512`; `make_loaders` also uses seed offsets per split |
| Input size and color | 64 × 64 RGB, represented as float tensors in `[0,1]` |
| Training augmentation | Random 64 × 64 crop and random horizontal flip (p=0.5) |
| Validation/test preprocessing | Deterministic center crop and no random augmentation |
| Small-image handling | Bicubic upsampling before cropping when the image is smaller than 64 pixels |
| Batch size | 32 |

The `data.py` helper reads prepared split directories if they exist. For unsplit source data, it can alternatively group images by the filename prefix preceding `_crop_` and split by source image. **The reported experiment used the existing prepared split directories**, not a newly generated group split. The notebook stores `data_protocol.json` with the actual selected relative filenames and `shared_data_splits.json` with the split manifest.

The test subset is **256 crops**, not the full 1,576-image prepared test folder. Its size and sampling rule should be stated consistently in the report. The prepared-folder route checks the split directory structure and file existence, but **does not by itself certify independence at the original-source/patient level**.

### Compression model and training settings

| Setting | Value / implementation from the executed notebook |
|---|---|
| Model | Single-scale residual convolutional encoder–quantizer–decoder (`model.py`) |
| Encoder/decoder | Strided convolution with SiLU and a residual block; nearest-neighbor upsampling/convolution in the decoder |
| Width / latent channels / downsampling levels | `width=64`, `latent_dim=16`, `levels=1` |
| Input and latent dimensions | RGB `3 × 64 × 64` → latent `16 × 32 × 32` (one index per latent location) |
| Codebook | `K=256` trainable 16-dimensional vectors |
| Integer symbol width | `ceil(log2(K))=8` bits per raw index at `K=256`, before lossless coding |
| Trainable parameters | 195,987 |
| Training quantization | Softmax over negative squared codeword distances, with straight-through **hard forward / soft backward** enabled |
| Evaluation quantization | Hard nearest-neighbor codeword index for every latent vector |
| Learned rate model | Global categorical codeword prior (`prior_logits`) and soft-training/hard-validation estimated rate |
| Objective | `L = RGB_MSE + λ × estimated_bpp`, with `λ=0.0001` for the baseline |
| Optimizer / learning rate | Adam / `2e-4`; total gradient norm clipped at 1 |
| Training seed / batch size | 1512 / 32 |
| Initialization | 8 epochs of continuous autoencoder warm-up; k-means on up to 32,768 training latent vectors, 20 iterations |
| Main training | 40 epochs; geometrically annealed temperature |
| Executed baseline temperature range | Approximately 0.03019 → 0.00604 after warm-start override (saved exactly in `config.json`) |
| Checkpoint selection | Lowest hard-quantized validation `MSE + λ × estimated_bpp` |
| Selected baseline checkpoint | [`runs/solution_larger_20261123_050247_803626/best.pt`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/best.pt), epoch 39 |

With flattened latent vectors `z_i` and codewords `c_k`, training forms the soft probabilities

`p_ik = softmax_k(-||z_i - c_k||² / τ)` and `z̃_i = Σ_k p_ik c_k`.

The straight-through option uses the nearest codeword in the **forward** training pass while passing gradients through the soft assignment. Evaluation encodes the integer index `k_i = argmin_k ||z_i-c_k||²` and decodes using the same model's codebook. At the baseline resolution, the encoder produces a `32 × 32` index grid. This distinguishes the differentiable training surrogate from the actual stored symbols.

The notebook trains encoder, decoder, codebook and learned categorical prior jointly. Let `r_k` denote the learned prior probability and `B,H,W` the input batch size and spatial dimensions. Its training rate surrogate is `Σ_(i,k) p_ik[-log2(r_k)] / (BHW)`; hard validation uses the corresponding selected-index costs. **Estimated BPP is not a measured compressed-file size.**

### True bitstream, decoding checks, and rate accounting

The `codec.py` implementation serializes hard nearest-codeword indices into an `.ecvq` bitstream; the decoder reconstructs the index grid, looks up vectors in the matching codebook and runs the decoder network. The saved stream includes shape/configuration information and a model fingerprint. `ECV1` uses zlib on packed index bits; `ECV2`, when trained causal context tables are attached to the checkpoint, can select among zlib, left-context arithmetic and up-context arithmetic coding. `entropy_context.py` provides optional training-only context-count fitting. **The recorded main comparison selected zlib for all 256 test images**; do not describe its reported bitrate as an observed arithmetic-coder gain.

Three distinct rate figures occur in the repository:

| Quantity | Definition | Where used |
|---|---|---|
| **Estimated BPP** | Codeword prior cross-entropy divided by input pixel count; not a serialized byte count | Training/validation, `test_metrics.json`, validation rate sweeps |
| **DNN payload BPP** | `8 × len(compressed_latent_payload) / (H × W)`; excludes the `.ecvq` header | Step 8 `jpeg_comparison/` and `dense_jpeg_comparison/` |
| **DNN full-file BPP** | `8 × len(entire_.ecvq_stream) / (H × W)`; **includes the stream header** | Question 4 `q4_ablation_results/` plots and `summary.csv` |

JPEG BPP uses `8 × len(complete_JPEG_file) / (H × W)` with Pillow `subsampling=0` (4:4:4), `optimize=False`, and the specified quality factor. The Question 4 plots consistently use **complete `.ecvq` file BPP versus complete JPEG file BPP**. The earlier Step 8 and dense-JPEG figures compare *DNN latent payload only* against full JPEG file size and **must not be presented as complete-file, like-for-like rate accounting**.

All DNN rates **exclude the shared trained checkpoint/model weights** (790,418 bytes for the selected `best.pt`, according to the executed notebook). Such model storage matters when assessing total deployment cost or very small collections of images. The full-file rate is still the size of the `.ecvq` stream, not the cost of distributing the shared decoder.

**Integrity checks recorded in the notebook/code:**

- `checks.py` verifies differentiable soft assignments (shapes, relative probabilities, temperature behavior, gradients), end-to-end backpropagation, and an odd-sized image encode–decode round trip.
- Step 8 reconstructs each selected test image from its **serialized bitstream** and checks it against the hard-forward reconstruction.
- Question 4 checks bitstream-decoded versus hard-forward output for the first image of each ablation checkpoint. The codec verifies the matching model fingerprint; `ECV2` additionally checks the packed-index CRC.
- Reproducing a saved `.ecvq` image requires the corresponding **exact checkpoint**, not an independently trained model with the same dimensions.

### Reported held-out compression results

The selected baseline used a **256-image, 64 × 64 RGB test subset**. From Step 7's saved `test_metrics.json` and the executed notebook:

| Metric | Baseline result |
|---|---:|
| Test PSNR, per-image mean | 31.6397 dB |
| Test RGB SSIM, per-image mean | 0.91117 |
| Hard-evaluation estimated BPP | 1.94129 |
| Measured compressed latent payload BPP (Step 8) | 1.2531 |
| Measured entire `.ecvq` file BPP (Question 4) | 1.517 (rounded) |
| Codewords used across the Step 8 test set | 221 / 256 |

Question 4 performs two controlled ablations using independently trained checkpoints. All models are compared with **the same fixed 256 test crops**, and PSNR/SSIM are evaluated after decoding the stored bitstream. Question 4 also rounds DNN reconstructions to an 8-bit grid before computing quality metrics; this explains its small difference from the Step 7/8 float-reconstruction PSNR.

| Model / ablation | Full-file BPP | Payload BPP | PSNR (dB) | RGB SSIM |
|---|---:|---:|---:|---:|
| Baseline: `K=256`, `λ=0.0001` | **1.517** | 1.253 | **31.63** | **0.9109** |
| Rate weight `λ=0` | 1.558 | 1.294 | 31.62 | 0.9109 |
| Rate weight `λ=0.001` | 1.479 | 1.215 | 31.47 | 0.9084 |
| Rate weight `λ=0.01` | 1.180 | 0.917 | 30.88 | 0.9017 |
| Codebook `K=32` | 1.266 | 1.003 | 29.70 | 0.8881 |
| Codebook `K=64` | 1.441 | 1.178 | 30.55 | 0.8981 |
| Codebook `K=128` | 1.762 | 1.498 | 31.11 | 0.9041 |

Selected comparison points from the **same Question 4 evaluation** (full JPEG file BPP):

| JPEG quality | Full-file BPP | PSNR (dB) | RGB SSIM |
|---|---:|---:|---:|
| Q1 | 1.501 | 21.11 | 0.5599 |
| Q10 | 1.755 | 26.79 | 0.7651 |
| Q20 | 2.039 | 29.48 | 0.8326 |
| Q30 | 2.283 | 30.86 | 0.8640 |
| Q50 | 2.679 | 32.46 | 0.8954 |
| Q90 | 4.968 | 37.47 | 0.9563 |

The test protocol provides one measured rate–distortion comparison, **not a universal superiority claim**: the experiments use one seed, only 256 small crops, a fixed checkpoint per variant, a particular Pillow JPEG implementation, and exclude common model-weight storage from DNN BPP. The complete JPEG Q1–Q95 sweep is recorded separately in `dense_jpeg_comparison/`.

### DNN files, experiments, and report figures

| Repository-relative path | Contents / report use |
|---|---|
| [`dnn_compression_notebook/DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb) | Implemented quantizer, training and evaluation steps, executed outputs, metrics, plots |
| [`dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/) | Selected baseline checkpoints, `config.json`, `history.csv`, `warmup.json`, `data_protocol.json`, `test_metrics.json` |
| [`.../learning_curves.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/learning_curves.png) | Baseline optimization/validation curves |
| [`.../validation_rate_sweep.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/validation_rate_sweep.png) | Rate-weight ablation on **estimated validation BPP** |
| [`.../codebook_validation_rate_distortion.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/codebook_validation_rate_distortion.png) | Codebook ablation on **estimated validation BPP** |
| [`.../jpeg_comparison/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/jpeg_comparison/) | DNN serialized `.ecvq` examples, JPEG images, `per_image.csv`, `summary.json`, and rate plots (DNN **payload** BPP) |
| [`.../dense_jpeg_comparison/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/dense_jpeg_comparison/) | JPEG Q1–Q95 measured comparison, per-image CSV and rate plots (DNN **payload** BPP) |
| [`.../q4_ablation_results/summary.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/summary.csv) | Baseline, lambda/codebook ablations and JPEG comparison; **full-file BPP** and quality metrics |
| [`.../q4_measured_rate_distortion_overview.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/q4_measured_rate_distortion_overview.png) | Full-file rate–distortion PSNR and SSIM overview |
| [`.../q4_measured_rate_distortion_zoom.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/q4_measured_rate_distortion_zoom.png) | Full-file rate–distortion detail around learned-codec variants |
| [`.../reconstructions_image_0.png`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/reconstructions_image_0.png) | Qualitative comparison on the first selected test image |
| [`dnn_compression_notebook/runs/sweep_*/`](dnn_compression_notebook/runs/) and [`codebook_k*/`](dnn_compression_notebook/runs/) | Independently trained checkpoints and configs for controlled ablations |

**Use the Question 4 full-file-BPP CSV and figures when making a like-for-like stored-file comparison with JPEG in the IEEE report.** Label Step 8 plots as *latent-payload* rate if also included. Numerical tables above summarize the executed notebook outputs; no additional training or test rerun was performed to create this README.

### Portability notes when reproducing on another computer

The released experiment artifacts record local Windows paths. These need adjustment on a fresh clone even when the dataset files and model checkpoints are present:

1. **Dataset manifest:** `dnn_compression_notebook/runs/shared_data_splits.json` stores its original absolute dataset root. On a different machine, in the Step 2 configuration cell change `SPLIT_MANIFEST` to a new local filename such as `OUTPUT_ROOT / 'shared_data_splits_local.json'` **before** `split_images(...)` runs. The helper will create a manifest from the prepared local `train/val/test` folders. Keep the original as an experiment audit record; for an exact subset check, compare the selected relative filenames with the supplied `data_protocol.json`.
2. **Saved ablation checkpoint paths:** `validation_sweep.json` and `codebook_sweep.json` contain original absolute checkpoint paths. Before running `q4_evaluation_cell.py` with released checkpoints on another machine, change the `checkpoint` fields in **local copies** of those JSON files to paths under your current `dnn_compression_notebook/runs/sweep_*/best.pt` and `runs/codebook_k*/best.pt`. The Q4 script loads each path directly. Training the ablation cells again generates new, local paths automatically.
3. **Notebook execution state:** the saved Question 4 cell contains results and figures, but its Jupyter `execution_count` field is empty in the uploaded notebook. To independently certify a clean sequential rerun, execute it again in the correct environment after setting local paths; do not mistake saved output cells for evidence of a fresh execution on another machine.
4. **Source files:** run the notebook against the matching `.py` files in `dnn_compression_notebook/`, rather than mixing versions from older copies. All saved `.ecvq` streams require their corresponding encoder/decoder checkpoint.

## Reproducibility checklist and limitations

The project follows the transparency principles of the [NeurIPS Paper Checklist](https://neurips.cc/Conferences/2021/PaperInformation/PaperChecklist). The statuses below refer to documentation and saved artifacts that were verified from the provided code/notebooks; they do **not** imply that the experiments were independently rerun in a clean environment.

| Requirement | JPEG restoration | Learned compression |
|---|---|---|
| Source code and notebook | Included | Included (implemented quantizer and evaluation code) |
| Dependencies | Project `requirements.txt`; lower bounds, not an exact lockfile | Project/subproject requirements; exact installed versions not pinned |
| Dataset source / placement | ADPPatches, local `data_1um_bicubic` | Same source, local `data_1um_bicubic` |
| Data split and experiment sample sizes | 12,616 / 1,576 / 1,576 prepared images | 1,024 / 128 / 256 sampled images; seeded selection |
| Split audit | SHA-256 exact-duplicate helper; not proof of patient independence | Saved manifest and per-run selected filenames; prepared-directory check is not a source-group leakage test |
| Image size and augmentation | 256 × 256; random crops/flips vs deterministic center crops | 64 × 64; random crop/horizontal flip vs deterministic center crops |
| JPEG settings | `subsampling=0`, `optimize=False`, listed Q values | Same settings for JPEG comparison; Q1–Q95 dense sweep |
| Seed and training configuration | Seed 42, 3 epochs, AdamW | Seed 1512, warm-up 8 + 40 epochs, Adam, baseline `K=256`, `λ=1e-4` |
| Model selection | Highest validation PSNR | Lowest hard-validation RD objective; epoch 39 |
| PSNR / SSIM | RGB per-image PSNR; Gaussian RGB SSIM | RGB per-image PSNR/SSIM; Question 4 reports decoded 8-bit reconstructions |
| Reported bitrate | Actual JPEG file BPP (restoration does not change source bitstream) | Explicit estimated, payload, and complete `.ecvq` stream BPP |
| Index/bitstream decoding | Not applicable | Odd-size round-trip tests, stream-decode comparison, model fingerprint; ECV2 CRC when present |
| Controlled rate–distortion ablations | Not applicable | Rate-weight `0,0.001,0.01` and codebook `32,64,128` versus baseline |
| Figures/results available | Metrics tables, quality curves, comparisons | JSON/CSV tables, PSNR/SSIM rate–distortion plots, decoded image examples |
| Exact independent environment replay | Not demonstrated here | Not demonstrated here; machine-specific paths must be adapted |
| Multiple-seed uncertainty | Not reported | Not reported |

**Known limitations:** Both analyses rely on one reported seed and on a prepared dataset whose 2 GB image files are excluded from GitHub. The JPEG baseline is trained for only three epochs. DNN metrics are from 256 small 64 × 64 held-out crops and one validation-selected checkpoint. Its model file is excluded from BPP; codec container overhead matters at this resolution. Some saved run manifests encode local absolute paths, and the environment dependencies are not fully version-locked. Exact-duplicate checks alone are not sufficient evidence of patient-level/source-level independence. The standalone restoration helper has not been established as an independent replacement for the executed notebook, and new training may yield different numerical results.

## Relationship to the report and submission

The IEEE-style Project B report and this repository should be read together. The report should cite the [GitHub repository](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression), identify the evaluated commit, and reference the exact figures/CSVs above. Use the same dataset splits, sample counts, image sizes, JPEG settings, random seeds, codebook size, rate weights, checkpoint-selection criterion, metric definitions and decoding checks in the text and figure captions. In particular, distinguish **JPEG-restoration source-bitstream BPP**, **compression payload BPP**, and **compression full-file BPP**.

Submit the written IEEE-format PDF through **ECE1512 Quercus**, as specified by the assignment. The GitHub repository provides supporting code, notebooks, pretrained checkpoints and selected auxiliary results; it does not replace the PDF submission or redistribute the excluded dataset. Evaluators should obtain the source data from the cited dataset provider and reconstruct the documented folder structure.

**References:** [LeonYe/ADPPatches](https://huggingface.co/datasets/LeonYe/ADPPatches) (dataset); [Jiang *et al.*, “Differentiable Vector Quantization for Rate-Distortion Optimization of Generative Image Compression,” CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Jiang_Differentiable_Vector_Quantization_for_Rate-Distortion_Optimization_of_Generative_Image_Compression_CVPR_2026_paper.html) (research context); [NeurIPS Paper Checklist](https://neurips.cc/Conferences/2021/PaperInformation/PaperChecklist) (reproducibility reporting). The accompanying IEEE report contains the additional literature-review references.
