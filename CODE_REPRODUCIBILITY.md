# ECE1512 Project B — Code Completeness / Reproducibility Checklist

**Artifact:** [Project B GitHub code repository](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression).  
**Companion artifact:** IEEE-style Project B PDF report, submitted separately through ECE1512 Quercus.  
**Basis:** [ML Code Completeness Checklist (Papers with Code)](https://medium.com/paperswithcode/ml-code-completeness-checklist-e9127b168501), alongside the course's [Machine Learning Reproducibility Checklist v2.0](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf).  
**Scope:** This file concerns the **code, trained checkpoints, figures, configuration records and independent use of the repository**, not completeness of claims in the submitted PDF. See the separate [paper checklist](PAPER_REPRODUCIBILITY.md).  
**Assessment basis:** Uploaded notebooks/modules, accompanying README draft and the Git command log (`main`, initial commit `9ab86c3`). The current live GitHub branch and a fresh end-to-end rerun were **not independently verified** for this checklist.  
**Statuses:** **Yes** = provided in the reviewed artifact snapshot; **Partial** = available but with reproducibility restrictions; **No** = absent/not demonstrated; **N/A** = outside project scope.

The external ML Code Completeness Checklist covers **dependencies, training scripts, evaluation scripts, pretrained weights and result/reproduction instructions**.

| Code completeness item | Status | Evidence / limitation |
|---|---|---|
| **1. Dependencies / installation** | **Partial** | Root and subproject `requirements.txt` files are supplied, and `README.md` documents Windows PowerShell/Jupyter setup. Dependencies use lower bounds rather than a fully pinned Python/PyTorch/CUDA environment or lockfile. |
| **2. Training implementation** | **Partial** | Both executed notebooks include the reported training logic; DNN [`engine.py`](dnn_compression_notebook/engine.py), [`warm_start.py`](dnn_compression_notebook/warm_start.py) and [`data.py`](dnn_compression_notebook/data.py) support baseline and ablation runs. The separate uploaded JPEG `train.py` calls `train_one_batch` without a definition/import; its command-line route is **not** verified as a standalone replacement for the executed notebook. |
| **3. Evaluation implementation** | **Yes** | JPEG [`evaluate.py`](jpeg_restoration_notebook/evaluate.py), notebook metrics/figures, and DNN [`comparison.py`](dnn_compression_notebook/comparison.py), [`codec.py`](dnn_compression_notebook/codec.py), [`q4_evaluation_cell.py`](dnn_compression_notebook/q4_evaluation_cell.py) implement PSNR, SSIM, JPEG byte counts, hard-index bitstreams, decoding and full-file measured-rate ablations. The Q4 cell depends on notebook variables and saved run files rather than being a documented standalone CLI. |
| **4. (Pre)trained model weights** | **Yes** | Initial Git staging/commit log included JPEG [`runs/spatial_only/best.pt`](jpeg_restoration_notebook/runs/spatial_only/best.pt) and DNN [`runs/solution_larger_20261123_050247_803626/best.pt`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/best.pt), with `last.pt` and rate-weight/codebook-size ablation weights. Recheck final remote commit and original artifact paths before submission. |
| **5. Results and reproduction instructions** | **Partial** | [`README.md`](README.md) contains setup, run choices, metric tables and paths to CSV/JSON/figures; notebooks have saved cell outputs. A fully verified one-command fresh-clone run is not supplied; the ~2 GB dataset is external, the manifest records an absolute Windows dataset path, and saved sweep JSONs contain absolute checkpoint paths. |

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

The prepared splits contain **12,616 / 1,576 / 1,576 images**. The DNN experiments do **not** use all prepared examples: their selected working subsets are **1,024 train, 128 validation and 256 test**, sampled deterministically with seed `1512` and recorded in a run's `data_protocol.json`. The DNN held-out subset uses a deterministic shuffled test sequence slice `[128:384]`. The prepared-directory route should not be taken as a proof of source-image/patient-level independence.

## Exact execution path available in the repository

1. Follow [`README.md`](README.md) to create the Python environment and install `requirements.txt`. The dependencies are not version-locked; use a compatible PyTorch build and record actual package versions for any new rerun.
2. Place the prepared external dataset as shown above. Open Jupyter using a working directory compatible with each notebook's relative `data_1um_bicubic` resolution.
3. **JPEG restoration:** open [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb). For training, use the executed notebook's 256×256, seed-42, 3-epoch/batch-16 settings and Q set `{10,20,30,40,50}`. The model is selected by validation restored PSNR. For evaluation without retraining, set `TRAIN_MODELS=False`, load `runs/spatial_only/best.pt`, and evaluate test Q `{10,15,20,25,30,40,50}`. The reported source-JPEG BPP uses the original encoded file bytes; the CNN does not change it.
4. **DNN baseline training:** open [`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb); use `MODE='larger'`, `SEED=1512`, `USE_WARM_START=True`, `REUSE_CHECKPOINT=None`, baseline `K=256`, `latent_dim=16`, `width=64`, `levels=1`, `λ=0.0001`, 8 continuous warm-up epochs and 40 optimization epochs. The run writes a newly timestamped `runs/solution_larger_*/` directory. Select `best.pt` using the lowest validation RD objective—not test PSNR.
5. **DNN controlled ablations:** with `RUN_SWEEP=True` and `RUN_CODEBOOK_SWEEP=True`, fit additional checkpoints for `λ={0,0.001,0.01}` at fixed `K=256`, and `K={32,64,128}` at fixed `λ=0.0001`. Use the same saved protocol and held-out test images; the baseline plus six ablations comprise the seven reported controlled DNN configurations.
6. **DNN evaluation without retraining:** reuse the released baseline `runs/solution_larger_20261123_050247_803626/best.pt`, set `RUN_SWEEP=False`, `RUN_CODEBOOK_SWEEP=False`, then run held-out test and JPEG-comparison steps. The Q4 final evaluation requires **locally valid** ablation checkpoint paths in `validation_sweep.json` and `codebook_sweep.json`; the uploaded JSON files encode the original Windows paths. Work on local copies rather than overwriting published audit artifacts.
7. **Decode and rate verification:** run the quantizer/pipeline checks and compare serialized `compress()`→`decompress()` output with the hard-forward reconstruction. For like-for-like storage comparisons, use `q4_ablation_results/summary.csv` **`file_bpp`** (`8×full .ecvq bytes/pixels`), versus full JPEG file BPP. The Step 8 `jpeg_comparison/` figures instead show DNN **payload-only** bpp; `estimated_bpp` is a training surrogate. The shared checkpoint bytes are excluded from reported DNN rates.

> The uploaded standalone JPEG `train.py` is not confirmed as a working single-command training entry point because it references an undefined `train_one_batch`. The primary reproduction instructions deliberately point to the executed notebook. Likewise, `q4_evaluation_cell.py` is written as a notebook-inserted cell, not a self-contained command-line program.

## Key results and where to inspect them

| Experiment / output | Result/evidence location | Interpretation |
|---|---|---|
| JPEG restoration metrics, Q10–Q50 | [`jpeg_restoration_notebook/runs/results/metrics_long.csv`](jpeg_restoration_notebook/runs/results/metrics_long.csv), [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb) | Seven held-out quality factors on 1,576 256×256 crops; JPEG and CNN share source input BPP. |
| JPEG qualitative/training curves | [`jpeg_restoration_notebook/runs/results/`](jpeg_restoration_notebook/runs/results/) | `quality_curves.png`, `training_curves.png`, `comparison_000_q*.png`. |
| Restoration trained weights | [`jpeg_restoration_notebook/runs/spatial_only/`](jpeg_restoration_notebook/runs/spatial_only/) | `best.pt`, `last.pt`, saved config/history. |
| DNN baseline configuration, selection and metrics | [`dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/) | `config.json`, `history.csv`, `best.pt`, `test_metrics.json`, `warmup.json`, `data_protocol.json`. |
| DNN hard-index encode/decode and JPEG samples | [`jpeg_comparison/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/jpeg_comparison/) | Saved `.ecvq` streams, decoded PNGs, JPEG samples, per-image CSV and **payload-bpp** rate plots. |
| DNN like-for-like full-file rate–distortion | [`q4_ablation_results/summary.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/summary.csv) | Same 256 crops, complete-file rate; baseline **1.517 bpp**, **31.63 dB PSNR**, **0.9109 RGB SSIM** (rounded). |
| DNN two controlled ablations | [`q4_ablation_results/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/) | Rate-weight and codebook sweeps, `per_image.csv`, PSNR/SSIM plots and reconstruction examples. |
| DNN selected baseline and ablation checkpoints | [`runs/`](dnn_compression_notebook/runs/) | Baseline `solution_larger_*`, independent `sweep_*`, `codebook_k*` folders and JSON configs/history. |

The complete-file reference comparison for the reported 256-image experiment is the **Q4** CSV/plots, not the Step 8 payload-only plot. The `codec.py` decoder verifies the stream fingerprint against the exact checkpoint; the optional ECV2 arithmetic-coded path checks additional index integrity (CRC). The recorded main-comparison streams selected **zlib**, so the published baseline is not evidence of an achieved arithmetic-coder gain.

## Known reproducibility limitations and required checks before submission

- **Dataset:** the prepared ~2 GB images are not in Git. The public dataset link and required folder layout are given, but the precise prepared files, group independence and any upstream processing must be confirmed independently.
- **Environment:** minimum dependency versions are available, but there is no complete locked OS/CUDA/PyTorch environment or tested fresh-clone script.
- **Checkpoints:** the supplied Git upload log confirms `.pt` files were committed; verify all intended weights and figures on the **final** GitHub commit, and record that commit hash in the report.
- **Relative/absolute paths:** DNN `shared_data_splits.json` stores a machine-specific `root`; the saved sweep JSON files have absolute checkpoint paths. Use a fresh *local* manifest and remap paths before rerunning a released checkpoint on another computer.
- **Training:** JPEG's standalone `train.py` has an unresolved helper reference. Use the documented notebook for the current reproduction pathway; repair and separately test the CLI before advertising it.
- **Statistics:** primary findings use single training seeds and limited training budgets. No independent multi-seed confidence intervals are provided; individual-image means are **not** a substitute for variation across training runs.
- **Fair storage comparison:** full `.ecvq` file BPP and full JPEG BPP exclude the separately shared neural checkpoint; results may shift with image size and model-distribution assumptions.
- **Re-run status:** saved notebook outputs/checkpoints demonstrate recorded executions, but this checklist does **not** certify an independent clean-machine training/evaluation run.

## Report–code linkage

The IEEE report must include the repository URL and should identify the **final Git commit SHA**. Refer to the [paper checklist](PAPER_REPRODUCIBILITY.md) for a report-to-source mapping of the JPEG restoration, DNN method, Question 4 results, figures, codec checks and remaining limitations. Submit the final IEEE PDF through Quercus; these Markdown checklists remain supporting files in the GitHub repository and do not replace the PDF.
