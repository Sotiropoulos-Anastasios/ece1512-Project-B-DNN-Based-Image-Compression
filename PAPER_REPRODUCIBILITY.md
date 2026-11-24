# ECE1512 Project B — Report / Paper Reproducibility Checklist

**Artifact:** *From Image Restoration to DNN-Based Image Compression: Project B* (IEEE-style report; final PDF to be submitted separately through ECE1512 Quercus).  
**Companion code:** [Project B GitHub repository](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression).  
**Basis:** [Machine Learning Reproducibility Checklist v2.0 (Pineau et al., April 2020)](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf), provided with the assignment.  
**Scope:** This checklist evaluates whether the **report and its linked experimental evidence** describe the scientific claims and experimental protocol. The separate [code completeness checklist](CODE_REPRODUCIBILITY.md) evaluates the released code and artifacts.  


## Machine Learning Paper Reproducibility Checklist

| Paper checklist question | Status | Evidence / qualification |
|---|---|---|
| Clear mathematical/model description | **Yes** | Report §Implementation and Experiments describes the five-layer residual JPEG-restoration CNN, \(\hat{x}=\operatorname{clip}(y+f_\theta(y))\), and the compact encoder–quantizer–decoder, soft/hard VQ assignment and rate–distortion objective. The report's earlier literature-review sections distinguish Ballé, Minnen, ELIC and the published RDVQ method. |
| Assumptions clearly explained | **Yes** | JPEG restoration changes decoded pixels but **does not change the stored JPEG bitstream**. Learned-compression claims assume an already available shared model/decoder. The implementation is **RDVQ-inspired**, not a complete reproduction of the published multiscale RDVQ architecture. |
| Algorithm complexity (time/space/sample size) analyzed | **Partial** | Model size, tensor/latent dimensions, sample counts, training budgets and some run-resource files are available. The report does not provide a systematic asymptotic or measured time/memory complexity analysis of every codec variant. |
| Theoretical claims and complete proofs | **N/A** | This is an empirical course project; no new mathematical theorem or proof is claimed. |
| Dataset statistics provided | **Yes** | Prepared ADPPatches `data_1um_bicubic` folders: **12,616 training, 1,576 validation, 1,576 test** images. The compression experiment uses **1,024 / 128 / 256** selected images, not the full original test set. |
| Train/validation/test splits documented | **Partial** | Prepared split folders and sample counts are documented. DNN sampling uses seed **1512**, a saved `shared_data_splits.json` and selected-filename `data_protocol.json` records; the held-out DNN subset is from a seeded test shuffle, indices **128:384**. The existing prepared splits are not independently proven source-/patient-disjoint. |
| Exclusions and preprocessing explained | **Yes** | The ~2 GB image dataset is excluded from Git; RGB normalization, crop sizes, crop/flip rules, bicubic resizing when needed, JPEG quality generation and 4:4:4 encoding settings are documented. |
| Downloadable dataset link supplied | **Yes** | [LeonYe/ADPPatches](https://huggingface.co/datasets/LeonYe/ADPPatches); data must be placed locally as `data_1um_bicubic/{train,val,test}/`. The exact prepared split is not bundled in the repository. |
| New data collection / annotation procedure | **N/A** | Existing prepared image data are used; no newly collected or annotated dataset is claimed. |
| Code dependencies available | **Partial** | Root and subproject `requirements.txt` files and Windows setup instructions are available, but installed versions, CUDA runtime and platform details are not locked to a complete environment manifest. |
| Training and evaluation code shared | **Yes** | [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb), [`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb), and accompanying Python modules. |
| Trained weights available | **Yes** | Uploaded Git log listed JPEG `runs/spatial_only/best.pt` and multiple DNN baseline/sweep `best.pt` and `last.pt` files. Exact file availability should be rechecked on the **final submission commit**. |
| Results linked to precise reproduction instructions | **Partial** | README provides notebook setup, saved results and checkpoint links; the report contains tables/figures for JPEG and DNN. There is no independently verified,clean-environment reproduction. |
| Hyperparameter ranges, final choices and selection explained | **Yes** | JPEG: 3 epochs, seed 42, 256-pixel crops, training quality factors 10/20/30/40/50, AdamW, L1 loss, selection by maximum validation PSNR. DNN: seed 1512, 64-pixel crops, baseline `K=256`, `λ=10^-4`, warm-up 8 epochs and main training 40 epochs, lowest validation RD objective; sweeps over `K={32,64,128}` and `λ={0,10^-3,10^-2}`. |
| Exact number of training/evaluation runs specified | **Partial** | The reported controlled protocol has one JPEG-restoration training run and **seven DNN configurations** (one baseline + three codebook sizes + three rate weights); the repository also includes older/other saved runs. No exhaustive inventory of all exploratory runs or independent repetitions is supplied. |
| Evaluation measures/statistics clearly defined | **Yes** | RGB PSNR and Gaussian-window RGB SSIM are defined; average image scores are reported. JPEG-restoration BPP uses actual encoded JPEG bytes. DNN **estimated BPP**, **latent-payload BPP**, and **complete `.ecvq` file BPP** are differentiated, as is 8-bit rounding in Question 4 evaluation. |
| Central tendency and variation reported | **Partial** | Mean PSNR/SSIM across **1,576 JPEG test images** (each Q) and **256 DNN test crops** are reported, along with per-image CSVs. Multi-seed variation, uncertainty intervals and error bars across independent training runs are **not** reported. |
| Runtime or energy cost reported | **Partial** | Training budgets, notebook timing information and DNN `resources.json` / `warmup.json` artifacts provide some resource evidence; the report lacks a consolidated per-configuration runtime/energy table. |
| Computing infrastructure described | **Partial** | CUDA execution is mentioned, but a consolidated hardware model, CPU/GPU RAM, OS, CUDA/driver and fully pinned package-version inventory is not part of the report. |

### Report ↔ repository evidence map

| Report evidence | Released repository evidence |
|---|---|
| JPEG architecture, loss, training and metrics: report `§DNN-Based Image Restoration`, Table `tab:restoration-results` | [`jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb); [`runs/results/`](jpeg_restoration_notebook/runs/results/); [`runs/spatial_only/`](jpeg_restoration_notebook/runs/spatial_only/) |
| Neural architecture, quantizer and training: report `§DNN-Based Image Compression`, Tables `tab:comp-settings` and `tab:comp-test` | [`dnn_compression_notebook/DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb), [`model.py`](dnn_compression_notebook/model.py), [`engine.py`](dnn_compression_notebook/engine.py), [`runs/solution_larger_20261123_050247_803626/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/) |
| Complete-file JPEG vs DNN and ablations: report `§Compression Evaluation and Ablation Study`, Tables `tab:q4-jpeg-test` and `tab:q4-ablation-test` | [`q4_ablation_results/summary.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/summary.csv), [`per_image.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/per_image.csv), [`q4_evaluation_cell.py`](dnn_compression_notebook/q4_evaluation_cell.py) |
| Actual index serialization and codec integrity | [`codec.py`](dnn_compression_notebook/codec.py), [`arithmetic.py`](dnn_compression_notebook/arithmetic.py), [`checks.py`](dnn_compression_notebook/checks.py) |

