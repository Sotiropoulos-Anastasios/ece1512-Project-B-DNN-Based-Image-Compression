# ECE1512 Project B — Report / Paper Reproducibility Checklist

**Artifact:** *From Image Restoration to DNN-Based Image Compression: Project B* (IEEE-style report; final PDF to be submitted separately through ECE1512 Quercus).  
**Companion code:** [Project B GitHub repository](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression).  
**Basis:** [Machine Learning Reproducibility Checklist v2.0 (Pineau et al., April 2020)](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf), provided with the assignment.  
**Scope:** This checklist evaluates whether the **report and its linked experimental evidence** describe the scientific claims and experimental protocol. The separate [code completeness checklist](CODE_REPRODUCIBILITY.md) evaluates the released code and artifacts.  
**Assessment basis:** The supplied November 23, 2026 LaTeX report draft, both uploaded notebooks/source files, the accompanying README draft, and the Git upload log. This is **not** an independent reproduction or a verification of the final Quercus PDF.  
**Statuses:** **Yes** = documented in the reviewed materials; **Partial** = documented with gaps or not fully verified; **No** = not demonstrated; **N/A** = not applicable.

## Machine Learning Paper Reproducibility Checklist

| Paper checklist question | Status | Evidence / qualification |
|---|---|---|
| Clear mathematical/model description | **Yes** | Report §Implementation and Experiments describes the five-layer residual JPEG-restoration CNN, \(\hat{x}=\operatorname{clip}(y+f_\theta(y))\), and the compact encoder–quantizer–decoder, soft/hard VQ assignment and rate–distortion objective. The report's earlier literature-review sections distinguish Ballé, Minnen, ELIC and the published RDVQ method. |
| Assumptions clearly explained | **Yes** | JPEG restoration changes decoded pixels but **does not change the stored JPEG bitstream**. Learned-compression claims assume an already available shared model/decoder. The implementation is **RDVQ-inspired**, not a complete reproduction of the published multiscale RDVQ architecture. |
| Algorithm complexity (time/space/sample size) analyzed | **Partial** | Model size, tensor/latent dimensions, sample counts, training budgets and some run-resource files are available. The report does not provide a systematic asymptotic or measured time/memory complexity analysis of every codec variant. |
| Theoretical claims and complete proofs | **N/A** | This is an empirical course project; no new mathematical theorem or proof is claimed. |
| Dataset statistics provided | **Yes** | Prepared ADPPatches `data_1um_bicubic` folders: **12,616 training, 1,576 validation, 1,576 test** images. The compression experiment uses **1,024 / 128 / 256** selected images, not the full original test set. |
| Train/validation/test splits documented | **Partial** | Prepared split folders and sample counts are documented. DNN sampling uses seed **1512**, a saved `shared_data_splits.json` and selected-filename `data_protocol.json` records; the held-out DNN subset is from a seeded test shuffle, indices **128:384**. The existing prepared splits are not independently proven source-/patient-disjoint. |
| Exclusions and preprocessing explained | **Yes** | The ~2 GB image dataset is excluded from Git; RGB normalization, crop sizes, crop/flip rules, bicubic resizing when needed, JPEG quality generation and 4:4:4 encoding settings are documented. No new image collection is claimed. |
| Downloadable dataset link supplied | **Yes** | [LeonYe/ADPPatches](https://huggingface.co/datasets/LeonYe/ADPPatches); data must be placed locally as `data_1um_bicubic/{train,val,test}/`. The exact prepared split is not bundled in the repository. |
| New data collection / annotation procedure | **N/A** | Existing prepared image data are used; no newly collected or annotated dataset is claimed. |
| Code dependencies available | **Partial** | Root and subproject `requirements.txt` files and Windows setup instructions are available, but installed versions, CUDA runtime and platform details are not locked to a complete environment manifest. |
| Training and evaluation code shared | **Yes** | [`JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb), [`DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb), and accompanying Python modules. The notebook path is the primary documented reproduction route. |
| Trained weights available | **Yes** | Uploaded Git log listed JPEG `runs/spatial_only/best.pt` and multiple DNN baseline/sweep `best.pt` and `last.pt` files. Exact file availability should be rechecked on the **final submission commit**. |
| Results linked to precise reproduction instructions | **Partial** | README provides notebook setup, saved results and checkpoint links; the report contains tables/figures for JPEG and DNN. There is no independently verified, single-command clean-environment reproduction. Existing absolute dataset/checkpoint paths need editing in new environments. |
| Hyperparameter ranges, final choices and selection explained | **Yes** | JPEG: 3 epochs, seed 42, 256-pixel crops, training quality factors 10/20/30/40/50, AdamW, L1 loss, selection by maximum validation PSNR. DNN: seed 1512, 64-pixel crops, baseline `K=256`, `λ=10^-4`, warm-up 8 epochs and main training 40 epochs, lowest validation RD objective; sweeps over `K={32,64,128}` and `λ={0,10^-3,10^-2}`. |
| Exact number of training/evaluation runs specified | **Partial** | The reported controlled protocol has one JPEG-restoration training run and **seven DNN configurations** (one baseline + three codebook sizes + three rate weights); the repository also includes older/other saved runs. No exhaustive inventory of all exploratory runs or independent repetitions is supplied. |
| Evaluation measures/statistics clearly defined | **Yes** | RGB PSNR and Gaussian-window RGB SSIM are defined; average image scores are reported. JPEG-restoration BPP uses actual encoded JPEG bytes. DNN **estimated BPP**, **latent-payload BPP**, and **complete `.ecvq` file BPP** are differentiated, as is 8-bit rounding in Question 4 evaluation. |
| Central tendency and variation reported | **Partial** | Mean PSNR/SSIM across **1,576 JPEG test images** (each Q) and **256 DNN test crops** are reported, along with per-image CSVs. Multi-seed variation, uncertainty intervals and error bars across independent training runs are **not** reported. |
| Runtime or energy cost reported | **Partial** | Training budgets, notebook timing information and DNN `resources.json` / `warmup.json` artifacts provide some resource evidence; the report lacks a consolidated per-configuration runtime/energy table. |
| Computing infrastructure described | **Partial** | CUDA execution is mentioned, but a consolidated hardware model, CPU/GPU RAM, OS, CUDA/driver and fully pinned package-version inventory is not part of the report. |

## Project B–specific reproducibility protocol (assignment item 3)

| Required detail | JPEG restoration | Learned compression |
|---|---|---|
| Dataset source and location | ADPPatches; local `data_1um_bicubic/{train,val,test}/`; data excluded from Git | Same prepared source folders; the DNN experiment uses selected fixed subsets and records chosen filenames |
| Split / sample counts | **12,616 / 1,576 / 1,576**; test evaluates the full 1,576 held-out image set per Q | **1,024 / 128 / 256** selected; DNN test subset is seeded-shuffle slice `[128:384]` of prepared test folder |
| Image size / conversion | **256×256 RGB**, values in `[0,1]`; training random crops and horizontal/vertical flips, evaluation center crops | **64×64 RGB**, values in `[0,1]`; training random crops and horizontal flips, evaluation center crops |
| JPEG settings | Training `Q={10,20,30,40,50}`; reported test `Q={10,15,20,25,30,40,50}`; Pillow `subsampling=0` (4:4:4), `optimize=False` | Fair JPEG comparison uses the same test crops, 4:4:4, `optimize=False`; Question 4 checks Q 1/5/10/15/20/25/30/40/50/70/90, with a further dense sweep recorded separately |
| Random seeds | **42** for training/splitting helpers | **1512** for seeded subset selection/training and sweep protocol |
| Codebook / RD training | N/A: residual CNN operates after JPEG decoding | Baseline `K=256`, `D=16`, `width=64`, one downsampling level; latent grid **32×32**; baseline `λ=10^-4`, straight-through soft-backward/hard-forward VQ; hard assignment at evaluation |
| Test-set model selection | Best **validation PSNR**, not best test score | Lowest hard-validation `MSE + λ × estimated BPP`; baseline checkpoint at epoch **39** |
| Rate-accounting rules | `8×JPEG file bytes/(256×256)`; **the CNN does not change that original rate** | Estimated rate is a training proxy; DNN `payload_bpp` excludes container header; DNN **`file_bpp` includes the `.ecvq` header**; JPEG uses complete file bytes; shared model weights are excluded |
| Index / decoding checks | N/A: no stored learned indices | Hard nearest-codebook indices serialized; `compress`→`decompress` compared with hard-forward output; code checks include odd image sizes, checkpoint fingerprint and optional ECV2 CRC consistency |
| Fair comparison / outputs | PSNR, SSIM and measured source-JPEG BPP on identical crops | PSNR/SSIM and **full-file BPP** on the same 256 test crops for baseline, JPEG and two controlled ablations |

### Report ↔ repository evidence map

| Report evidence | Released repository evidence |
|---|---|
| JPEG architecture, loss, training and metrics: report `§DNN-Based Image Restoration`, Table `tab:restoration-results` | [`jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb`](jpeg_restoration_notebook/JPEG_Restoration_Student.ipynb); [`runs/results/`](jpeg_restoration_notebook/runs/results/); [`runs/spatial_only/`](jpeg_restoration_notebook/runs/spatial_only/) |
| Neural architecture, quantizer and training: report `§DNN-Based Image Compression`, Tables `tab:comp-settings` and `tab:comp-test` | [`dnn_compression_notebook/DNN_Compression_Student.ipynb`](dnn_compression_notebook/DNN_Compression_Student.ipynb), [`model.py`](dnn_compression_notebook/model.py), [`engine.py`](dnn_compression_notebook/engine.py), [`runs/solution_larger_20261123_050247_803626/`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/) |
| Complete-file JPEG vs DNN and ablations: report `§Compression Evaluation and Ablation Study`, Tables `tab:q4-jpeg-test` and `tab:q4-ablation-test` | [`q4_ablation_results/summary.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/summary.csv), [`per_image.csv`](dnn_compression_notebook/runs/solution_larger_20261123_050247_803626/q4_ablation_results/per_image.csv), [`q4_evaluation_cell.py`](dnn_compression_notebook/q4_evaluation_cell.py) |
| Actual index serialization and codec integrity | [`codec.py`](dnn_compression_notebook/codec.py), [`arithmetic.py`](dnn_compression_notebook/arithmetic.py), [`checks.py`](dnn_compression_notebook/checks.py) |

## Interpretation and evidence boundaries

- **Do not identify the teaching codec as a faithful/full recreation of RDVQ.** It reproduces selected differentiable-VQ and rate–distortion ideas using a smaller single-scale architecture and a global categorical prior.
- **Do not conflate rates.** Question 4's complete-file-bpp results are the appropriate on-disk comparison against JPEG; earlier Step 8 plots use DNN **payload-only** BPP against JPEG complete-file BPP. In both cases the DNN checkpoint is assumed pre-shared and excluded from the rate.
- **The prepared train/val/test directories do not establish patient-/source-level independence.** A filename-manifest check is not the same as a provenance audit. The repo includes checks for exact duplicate files in the JPEG helpers, not a full provenance-level proof.
- **Single seeds are not uncertainty estimates.** Per-image means do not substitute for error bars over independent training runs; conclusions should remain tied to the reported small-crop experiments.
- **The report draft still needs final editorial and artifact checks.** The supplied LaTeX has an empty `abstract` and an instructional bold paragraph under JPEG restoration; replace these before final PDF compilation. Verify that all referenced figures resolve rather than showing placeholder boxes, and that tables/figures correspond to the **final Git commit**.
- **The PDF and GitHub are distinct submitted artifacts.** Submit the IEEE PDF via Quercus; include the live repository URL **and the final commit SHA** in the PDF so the cited code/figures/checkpoints match the graded submission.

**Checklist sources:** [Pineau, ML Reproducibility Checklist v2.0](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf); [Project B assignment rubric](https://github.com/Sotiropoulos-Anastasios/ece1512-Project-B-DNN-Based-Image-Compression) (course-provided rubric reviewed separately); [Papers with Code release recommendations](https://github.com/paperswithcode/releasing-research-code).
