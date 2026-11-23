\documentclass[conference]{IEEEtran}
% ECE1512 Project B: first 10-point question of Section 1 only.
% Compatible with Overleaf/pdfLaTeX. Add the remaining literature review,
% methods, and results above the bibliography as they are completed.
\usepackage[T1]{fontenc}
\usepackage{cite}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{hyperref}
\usepackage{url}
\hypersetup{colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue}

\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc}


% Optional figure commands retained for the rest of the project.
% Place your own figure files in the report_figures/ directory.
\newcommand{\resultfigure}[3]{%
\begin{figure}[!t]
\centering
\IfFileExists{report_figures/#1}{%
  \includegraphics[width=\columnwidth]{report_figures/#1}%
}{%
  \fbox{\parbox[c][1.22in][c]{0.90\columnwidth}{%
    \centering\footnotesize Upload \\ \texttt{\detokenize{#1}}
    \\ to \texttt{report\_figures/}%
  }}%
}
\caption{#2}\label{#3}
\end{figure}}

\newcommand{\resultwidefigure}[3]{%
\begin{figure*}[!t]
\centering
\IfFileExists{report_figures/#1}{%
  \includegraphics[width=0.91\textwidth]{report_figures/#1}%
}{%
  \fbox{\parbox[c][1.40in][c]{0.82\textwidth}{%
    \centering\footnotesize Upload \texttt{\detokenize{#1}}
    \\ to \texttt{report\_figures/}%
  }}%
}
\caption{#2}\label{#3}
\end{figure*}}

% Compression figures: copy the local run artifacts to this folder. Missing
% images generate honest placeholders rather than broken \includegraphics.
\newcommand{\CompressionFigureFolder}{DNN-Based Image Compression}
\newcommand{\CompressionImageFigure}[3]{%
\begin{figure}[!t]\centering
\IfFileExists{\CompressionFigureFolder/#1}{%
  \includegraphics[width=\columnwidth]{\CompressionFigureFolder/#1}%
}{\fbox{\parbox[c][1.08in][c]{0.91\columnwidth}{\centering\footnotesize
  Missing image\\\texttt{\detokenize{#1}}}}}%
\caption{#2}\label{#3}\end{figure}}
\newcommand{\CompressionWideFigure}[3]{%
\begin{figure*}[!t]\centering
\IfFileExists{\CompressionFigureFolder/#1}{%
  \includegraphics[width=0.88\textwidth]{\CompressionFigureFolder/#1}%
}{\fbox{\parbox[c][1.08in][c]{0.85\textwidth}{\centering\footnotesize
  Missing image\\\texttt{\detokenize{#1}}}}}%
\caption{#2}\label{#3}\end{figure*}}
\newcommand{\CompressionThumb}[2]{%
\begin{minipage}[t]{0.303\textwidth}\centering
\IfFileExists{\CompressionFigureFolder/#1}{%
  \includegraphics[width=0.95\linewidth,height=0.92in,keepaspectratio]{\CompressionFigureFolder/#1}%
}{\fbox{\parbox[c][0.86in][c]{0.89\linewidth}{\centering\scriptsize
  Original not uploaded}}}%
\\[-1pt]{\scriptsize #2}\end{minipage}\hfill}



\title{From Image Restoration to DNN-Based Image Compression: Project B}
\author{
\IEEEauthorblockN{Anastasios - Theocharis Sotiropoulos}
\IEEEauthorblockA{
ECE1512 -- Project B, Fall 2026 \\
University of Toronto \\
Toronto, Ontario, Canada \\
Student ID: 1013796741}
}

\begin{document}
\maketitle

% Add the full-project abstract here after all experiments are complete.
% Add your Project B GitHub repository link once it is available.

\section{Introduction and Literature Review}
\subsection{Image Restoration and Classical JPEG Compression}

Image restoration aims to recover an estimate of an original image from an
observation that has been degraded. The degradation can come from noise, blur,
or the loss of information during compression. For a linear, shift-invariant degradation process with
additive noise, a common model is given by
\cite{gonzalez2008}:
\begin{equation}
g(x,y) = h(x,y) * f(x,y) + \eta(x,y),
\label{eq:degradation_model}
\end{equation}
where $f(x,y)$ is the original image, $h(x,y)$
represents the degradation function, $*$ denotes
convolution, $\eta(x,y)$ is additive noise and
$g(x,y)$ is the observed degraded image.

However, it is important to note that this model
does not describe every type of image degradation.
In particular, JPEG compression cannot be represented
exactly by a single linear convolution and additive
noise. Although the discrete cosine transform (DCT)
used in JPEG is linear, the subsequent quantization
step is nonlinear and results in information loss
\cite{gonzalez2008,wallace1992}.

  

Restoration is different from just making an image look more appealing. It attempts to account
for the process that degraded the original image
and reduce its effects \cite{gonzalez2008}. In this project, the degradation does not come from
sensor noise, motion blur or any other unknown source. More specifically, we consider the
problem of \emph{JPEG artifact removal}, where the
observed image is obtained by compressing and
decompressing an original image at a selected JPEG
quality factor $Q$:
\begin{equation}
g = \operatorname{JPEGDecode}
\left(\operatorname{JPEGEncode}(f,Q)\right).
\label{eq:jpeg_degradation}
\end{equation}
Our first goal is to improve the quality of a JPEG-decoded
image without modifying the original JPEG encoder or
compressed bitstream \cite{ye2026}. We then move beyond
image restoration and investigate learned image compression,
where neural networks are used to encode and decode images,
replacing the traditional handcrafted transforms with
learned representations.


% Figure 1: compact post-decoding restoration pipeline.
\begin{figure}[!t]
\centering
\begin{tikzpicture}[
  >=Latex,
  every node/.style={font=\footnotesize},
  unit/.style={draw=black!55,rounded corners=2pt,fill=black!2,
    text width=5.1cm,align=center,minimum height=6.5mm,inner sep=2.5pt},
  restored/.style={unit,fill=blue!9,draw=blue!50!black},
  link/.style={-Latex,semithick,draw=black!70}]
\node[unit] (original) at (0,0) {Original image $x$};
\node[unit] (encode) at (0,-0.93) {JPEG encoding (quality $Q$)};
\node[unit] (stream) at (0,-1.86) {Stored JPEG bitstream $b$};
\node[unit] (decode) at (0,-2.79) {JPEG decoding};
\node[unit] (observed) at (0,-3.72) {Degraded image $y$};
\node[restored] (residual) at (0,-4.65)
  {CNN post-processing: $\hat{x}=y+f_{\theta}(y)$};
\draw[link] (original.south) -- (encode.north);
\draw[link] (encode.south) -- (stream.north);
\draw[link] (stream.south) -- (decode.north);
\draw[link] (decode.south) -- (observed.north);
\draw[link] (observed.south) -- (residual.north);
\end{tikzpicture}
\caption{Post-decoding JPEG artifact removal. The CNN modifies
reconstructed pixels, not the original stored bitstream $b$.}
\label{fig:jpeg-restoration-pipeline}
\end{figure}

% Figure 2: full-width encoder with clean DC/AC branches and quality control.
\begin{figure*}[!t]
\centering
\begin{tikzpicture}[
  >=Latex,
  box/.style={draw=black!50,rounded corners=2pt,fill=black!2,
    align=center,text width=2.18cm,minimum height=1.06cm,
    inner sep=2.5pt,font=\footnotesize},
  smallbox/.style={box,text width=2.18cm,minimum height=0.72cm},
  loss/.style={box,fill=orange!12,draw=orange!55!black},
  quality/.style={box,fill=blue!7,draw=blue!45!black},
  product/.style={box,fill=blue!11,draw=blue!55!black},
  flow/.style={-Latex,semithick,draw=black!75},
  guide/.style={-Latex,semithick,dashed,draw=blue!60!black},
  section/.style={font=\scriptsize\bfseries,text=black!65}]
% Independent preparation and transform stages, left to right.
\node[box] (rgb) at (1.25,0) {RGB image};
\node[box] (cspace) at (4.1,0)
  {Color conversion\\$RGB\rightarrow YCbCr$};
\node[loss] (chroma) at (6.95,0)
  {Optional chroma\\subsampling (4:2:0)};
\node[box] (blocks) at (9.8,0)
  {$8\times8$ blocks\\and level shift};
\node[box] (transform) at (12.65,0)
  {2-D DCT\\coefficients $C_{u,v}$};
\node[loss] (quantizer) at (15.5,0)
  {Quantization\\$k=\mathrm{round}(C/T)$};
\draw[flow] (rgb.east) -- (cspace.west);
\draw[flow] (cspace.east) -- (chroma.west);
\draw[flow] (chroma.east) -- (blocks.west);
\draw[flow] (blocks.east) -- (transform.west);
\draw[flow] (transform.east) -- (quantizer.west);
% Table generation supplies steps to the quantizer from above.
\node[quality] (inputs) at (12.15,1.73)
  {Quality factor $Q$\\base tables $M^{Y},M^{C}$};
\node[quality] (scaled) at (15.5,1.73)
  {Scale $s(Q)M/100$\\round and clip $\rightarrow T(Q)$};
\draw[guide] (inputs.east) -- (scaled.west);
\draw[guide] (scaled.south) -- (quantizer.north);
% Entropy coding follows the transform/quantization stage.
\node[box] (scan) at (15.5,-2.10)
  {Zigzag scan\\DC and AC streams};
\node[smallbox] (dcdiff) at (12.65,-1.57)
  {DC difference\\(DPCM)};
\node[smallbox] (acrle) at (12.65,-2.68)
  {AC run-length\\coding};
\node[box] (huffman) at (9.8,-2.10)
  {Huffman symbols\\and value bits};
\node[box] (headers) at (6.95,-2.10)
  {Pack coded data\\with JPEG headers};
\node[product] (bitstream) at (4.1,-2.10)
  {Compressed JPEG\\bitstream};
\draw[flow] (quantizer.south) -- (scan.north);
\draw[flow] (scan.west) -- (14.1,-2.10) |- (dcdiff.east);
\draw[flow] (scan.west) -- (14.1,-2.10) |- (acrle.east);
\draw[flow] (dcdiff.west) -- (11.2,-1.57) |- (huffman.east);
\draw[flow] (acrle.west) -- (11.2,-2.68) |- (huffman.east);
\draw[flow] (huffman.west) -- (headers.east);
\draw[flow] (headers.west) -- (bitstream.east);
\node[section,anchor=west] at (0,0.79)
  {IMAGE DATA};
\node[section,anchor=west] at (0,-2.10)
  {SYMBOL CODING};
\end{tikzpicture}
\caption{DCT-based JPEG encoding. Orange boxes mark operations that
may discard image information (optional chroma subsampling and
DCT-coefficient quantization). Dashed blue arrows show how the JPEG
quality setting determines the quantization steps; the remaining
symbol-coding steps are reversible
\cite{wallace1992,plataniotisjpeg,ece1512jpeg2021}.}
\label{fig:jpeg-encoder-detail}
\end{figure*}

The goal of classical image compression is to reduce the number of bits needed to represent an image by exploiting coding, spatial, and psychovisual redundancies \cite{gonzalez2008}. JPEG achieves this through block-based transform coding \cite{wallace1992,plataniotisjpeg}. In its common baseline form, an RGB image is first converted to a luminance--chrominance space ($YC_bC_r$) and the chrominance channels ($C_b, C_r$) are typically subsampled (e.g., 4:2:0) to exploit the human visual system's lower spatial acuity for color than for brightness \cite{plataniotisjpeg,ece1512jpeg2021}. Each component is then partitioned into $8\times8$ blocks, level-shifted by subtracting $128$ so pixel values are centered around zero, and transformed independently using a two-dimensional discrete cosine transform (2-D DCT) \cite{gonzalez2008,ece1512jpeg2021}. Because neighboring pixels in natural images are strongly correlated, the 2-D DCT concentrates most block energy into a few low-frequency coefficients \cite{gonzalez2008,wallace1992,plataniotisjpeg}.


JPEG achieves much of its compression through \emph{quantization} of the
DCT coefficients. 
Not all DCT coefficients are quantized with the same
step size. The quantization step depends on the spatial
frequency represented by each coefficient. In general,
the human visual system is more sensitive to distortions
in low-frequency image content than to the loss of very
high-frequency details. For this reason, conventional
JPEG quantization tables usually assign smaller
quantization steps to low-frequency coefficients and
larger steps to high-frequency coefficients.

These step sizes are specified in an $8\times8$
normalization matrix, also called a quantization matrix.
This allows less perceptually important information to
be represented with lower precision, while preserving
more information in the visually important coefficients
\cite{gonzalez2008,wallace1992,ece1512jpeg2021}.
If $C_{u,v}$ denotes a transform coefficient and
$T_{u,v}$ the corresponding entry in the quantization table, the quantized
integer and its decoder-side approximation are
\begin{equation}
  k_{u,v}=\operatorname{round}\!\left(\frac{C_{u,v}}{T_{u,v}}\right),
  \qquad \widetilde C_{u,v}=T_{u,v}k_{u,v}.
  \label{eq:jpeg-quantization}
\end{equation}
The rounding step is irreversible in general since several different input
coefficients can map to the same integer. Larger quantization steps also
turn more small coefficients into zeros. JPEG exploits the resulting
sparsity by arranging the coefficients in zigzag order and uses run-length
coding for the AC coefficients and differential coding for the DC
coefficients, followed by entropy coding (like Huffman coding in JPEG) \cite{ece1512jpeg2021,plataniotisjpeg}. These coding steps further reduce the size of the
compressed representation without introducing additional
loss. The main irreversible distortion instead comes from
the earlier quantization step
\cite{wallace1992,plataniotisjpeg}.

The \emph{quality factor} $Q$ controls the strength of
quantization in common JPEG implementations. It typically
ranges from $1$ to $100$. A lower quality factor generally
produces larger quantization steps, reducing the number
of bits required but introducing more visible distortion.
A higher quality factor uses finer quantization, preserving
more image detail at the cost of a larger file.

In the Independent JPEG Group (IJG) implementation,
the quality factor is converted into a scaling percentage
$s(Q)$ according to \cite{libjpegquality}:
\begin{equation}
s(Q)=
\begin{cases}
5000/Q, & 1\leq Q<50,\\
200-2Q, & 50\leq Q\leq100.
\end{cases}
\label{eq:jpeg-quality}
\end{equation}
This scaling factor is applied to predefined luminance
and chrominance quantization tables. If
$T^{\mathrm{base}}_{u,v}$ denotes an entry in one of
these base tables, the quantization step used by the
encoder is
\begin{equation}
T_{u,v}(Q) =
\operatorname{clip}_{[1,255]}
\left(
\operatorname{round}
\left(
\frac{s(Q)T^{\mathrm{base}}_{u,v}}{100}
\right)
\right),
\label{eq:jpeg-scaled-table}
\end{equation}
where clipping restricts the quantization steps to
the range supported by baseline JPEG. The quality
factor therefore affects the quantization table entries
used in Eq.~\eqref{eq:jpeg-quantization}, controlling
the amount of information discarded during compression.

The loss from quantization is not always perceived as uniform noise. Since
JPEG transforms and quantizes neighboring $8\times8$ blocks independently,
strong compression can make their boundaries visible as a grid of
\emph{blocking artifacts}. Removing many high-frequency coefficients can
also produce \emph{ringing}, seen as faint oscillations near sharp edges,
and can suppress thin structures and fine textures. These effects explain
why a low-quality JPEG image may have the correct overall scene content
but noticeably poorer visual fidelity \cite{gonzalez2008,plataniotisjpeg,ye2026}.


During decoding, the coded symbols are recovered, DC
prediction and AC run-length coding are reversed, and
coefficients are returned to their block positions.
The decoder then multiplies the quantized coefficients
by the corresponding entries of the quantization table,
applies the inverse DCT, and, when needed, upsamples
the chroma components and converts the image back to
RGB \cite{wallace1992,plataniotisjpeg}.


A restoration network operates \emph{after} JPEG decompression. Adopting the notation of \cite{ye2026} (corresponding to $f$ and $g$ in Eq.~\eqref{eq:jpeg_degradation}), let $x$ be the original clean image, $b=E_{\mathrm{JPEG}}(x;Q)$ the compressed bitstream, and $y=D_{\mathrm{JPEG}}(b)$ the decoded observation. The residual CNN considered
in this project estimates a correction $f_\theta(y)$ and produces
\begin{equation}
  \hat{x}=y+f_\theta(y).
  \label{eq:residual-restoration}
\end{equation}
The restored image $\hat{x}$ may be closer to $x$ than the JPEG-decoded
image $y$, for example when measured by PSNR or SSIM, but the network
only changes the reconstructed pixels \cite{ye2026}. It does not rerun
the JPEG encoder, change the quantized DCT coefficients stored in $b$,
or write a new JPEG bitstream. For an image of width $W$ and height $H$,
its original coding rate is therefore still
\begin{equation}
  R_{\mathrm{JPEG}}=\frac{|b|_{\mathrm{bits}}}{WH}
  \quad\text{bits per pixel (bpp)}.
  \label{eq:jpeg-bpp}
\end{equation}
This distinction matters when comparing restoration results: better PSNR
or SSIM at the \emph{same input JPEG bpp} shows an improvement in decoded
image quality, not a reduction in the number of bits originally stored.
If the restored image is saved as a new JPEG, that separate encoding step
can produce a different bitrate. The unchanged-bitrate statement applies
to post-processing the original compressed image, with the CNN weights
assumed to be already available at the decoder.


\subsection{Learned Image Compression}

Unlike post-decoding JPEG restoration, learned image
compression optimizes the image representation itself
for both coding rate and reconstruction quality.
Ball\'{e} et al.~\cite{balle2016} proposed an
end-to-end optimized compression framework based
on nonlinear analysis and synthesis transforms.

The analysis transform $g_a$ maps an input image
$x$ to a latent representation $y=g_a(x)$,
which is quantized and entropy-coded into a
compressed bitstream. The synthesis transform
$g_s$ reconstructs the image from the quantized
latents $\hat{y}$:
\begin{equation}
\hat{x}=g_s(\hat{y}).
\end{equation}
Both transforms consist of three convolutional
stages with downsampling or upsampling.
Instead of conventional pointwise activations,
the model employs generalized divisive
normalization (GDN) and its approximate inverse
(IGDN). These nonlinearities provide a form
of adaptive gain control that helps reduce
statistical dependencies in the latent
representation \cite{balle2016}.

A central challenge is quantization. During actual
compression, the continuous latents are rounded
to integers. However, rounding has zero derivatives
almost everywhere, making direct gradient-based
optimization difficult. The authors address this
by replacing rounding with additive uniform noise
during training:
\begin{equation}
\tilde{y}=y+u,\qquad
u\sim\mathcal{U}(-1/2,1/2).
\label{eq:uniform-noise}
\end{equation}
This continuous approximation allows gradients
to propagate through the encoder while modeling
the uncertainty introduced by quantization.
During actual compression, hard rounding is used.

The probability distribution of the latent
representation is approximated by a factorized
model with learned marginal densities. This model
provides probability estimates for entropy coding.
The transforms and probability model are optimized
jointly using the rate--distortion objective
\begin{equation}
\mathcal{L}=\mathbb{E}_{x,u}\Big[
-\sum_i\log_2
p_{\tilde{y}_i}(\tilde{y}_i)
+\lambda d(x,g_s(\tilde{y}))
\Big],
\label{eq:rate-distortion}
\end{equation}
where the first term estimates coding cost,
$d$ measures reconstruction distortion using MSE,
and $\lambda$ controls the trade-off between
rate and distortion \cite{balle2016}.

\begin{figure*}[!t]
\centering
\begin{tikzpicture}[
    >=Latex,
    stage/.style={draw=black!55, fill=black!2, rounded corners=2pt,
        align=center, text width=2.12cm, minimum height=0.95cm,
        inner sep=2.5pt, font=\footnotesize},
    signal/.style={stage,fill=white,text width=1.85cm},
    network/.style={stage,fill=blue!8,draw=blue!55!black},
    lossy/.style={stage,fill=orange!12,draw=orange!65!black},
    coded/.style={stage,fill=green!9,draw=green!45!black},
    flow/.style={-Latex,semithick,draw=black!75},
    estimate/.style={-Latex,semithick,draw=blue!60!black},
    section/.style={font=\footnotesize\bfseries,anchor=west,text=black!75}
]
% (A) Deployment: actual lossily compressed bitstream and its decoding.
\node[section] at (0.05,1.10) {(a) Actual compression and decompression};
\node[signal]  (original) at (1.20,0) {Input image\\$x$};
\node[network] (analyzer) at (3.85,0) {Analysis $g_a$\\3$\times$ Conv, downsample, GDN};
\node[signal]  (latents) at (6.50,0) {Continuous latents\\$y=g_a(x)$};
\node[lossy]   (rounding) at (9.15,0) {Scalar rounding\\$q=\mathrm{round}(y)$};
\node[coded]   (enc) at (11.80,0) {Entropy encoder\\CABAC-based};
\node[signal]  (stream) at (14.45,0) {Compressed\\bitstream $b$};
\draw[flow] (original.east) -- (analyzer.west);
\draw[flow] (analyzer.east) -- (latents.west);
\draw[flow] (latents.east) -- (rounding.west);
\draw[flow] (rounding.east) -- (enc.west);
\draw[flow] (enc.east) -- (stream.west);
\node[coded]   (dec) at (14.45,-1.58) {Entropy decoder\\recover indices};
\node[signal]  (quantized) at (11.80,-1.58) {Recovered latents\\$\hat y=q$};
\node[network] (synth) at (9.15,-1.58) {Synthesis $g_s$\\3$\times$ IGDN, upsample, Conv};
\node[signal]  (recon) at (6.50,-1.58) {Reconstruction\\$\hat x=g_s(\hat y)$};
\draw[flow] (stream.south) -- (dec.north);
\draw[flow] (dec.west) -- (quantized.east);
\draw[flow] (quantized.west) -- (synth.east);
\draw[flow] (synth.west) -- (recon.east);
% separator between deployment and training
\draw[black!28,thin] (0.0,-2.58) -- (15.65,-2.58);
% (B) Training: differentiable proxy, which is not itself a coded bitstream.
\node[section] at (0.05,-3.06) {(b) Training-time differentiable approximation};
\node[signal]  (trainx) at (1.20,-4.05) {Input image\\$x$};
\node[network] (trainga) at (3.85,-4.05) {Analysis\\$y=g_a(x)$};
\node[lossy]   (noise) at (6.50,-4.05) {Uniform noise\\$u\sim\mathcal U(-\tfrac12,\tfrac12)$};
\node[signal]  (noisey) at (9.15,-4.05) {Relaxed latent\\$\tilde y=y+u$};
\node[network] (traings) at (11.80,-4.05) {Synthesis\\$g_s(\tilde y)$};
\node[signal]  (trainout) at (14.45,-4.05) {Reconstruction\\$\tilde x=g_s(\tilde y)$};
\draw[flow] (trainx.east) -- (trainga.west);
\draw[flow] (trainga.east) -- (noise.west);
\draw[flow] (noise.east) -- (noisey.west);
\draw[flow] (noisey.east) -- (traings.west);
\draw[flow] (traings.east) -- (trainout.west);
\node[coded,text width=3.0cm] (rate) at (9.15,-5.72)
  {Rate estimate $R$\\factorized $p_{\tilde y}$};
\node[coded,text width=3.0cm] (dist) at (14.45,-5.72)
  {Distortion $D$\\MSE$(x,\tilde x)$};
\node[signal,text width=3.1cm,fill=black!5] (objective) at (11.80,-7.16)
  {Joint objective\\$\mathcal L=R+\lambda D$};
\draw[estimate] (noisey.south) -- (rate.north);
\draw[estimate] (trainout.south) -- (dist.north);
\draw[estimate] (rate.south) -- (objective.north west);
\draw[estimate] (dist.south) -- (objective.north east);
\end{tikzpicture}
\caption{The end-to-end optimized image compression model of Ball\'{e}
\emph{et al.}~\cite{balle2016}, redrawn from the paper's nonlinear
transform-coding framework (Fig.~1) and optimization procedure (Secs.~2--3).
\emph{(a)} At test time, the three-stage analysis transform produces
latents, scalar rounding makes discrete indices, and arithmetic entropy
coding forms a bitstream; entropy decoding precedes synthesis.
\emph{(b)} During training, additive uniform noise replaces rounding and
provides a differentiable surrogate for the rate--distortion loss.
The training branch does not create a compressed bitstream.}
\label{fig:balle-architecture}
\end{figure*}

The authors evaluated their method against JPEG
and JPEG 2000 using actual compressed bitrates
and reported generally improved rate--distortion
performance, together with better MS-SSIM
scores on their tested images \cite{balle2016}.
However, fine textures can still be lost at
low bitrates, and separate models must be
trained for different rate--distortion settings.

A further limitation is the factorized entropy
model, which does not explicitly capture
dependencies between latent coefficients.
This motivates subsequent methods that
incorporate hierarchical and autoregressive
probability models.



\subsection{Joint Autoregressive and Hierarchical Priors}

Although the end-to-end framework of Ball\'{e}
\emph{et al.}~\cite{balle2016} learns a compressible
latent representation, its factorized entropy model
does not explicitly capture dependencies between
quantized coefficients. Minnen \emph{et al.}
~\cite{minnen2018} address this limitation by
combining a hierarchical hyperprior with an
autoregressive context model, building on the
scale-hyperprior approach of
Ball\'{e} \emph{et al.}~\cite{balle2018hyperprior}.

The analysis transform produces continuous latents
$y=g_a(x)$, which are scalar-quantized to $\hat y$.
A hyper-analysis transform generates $z=h_a(y)$,
whose quantized representation $\hat z$ is
entropy-coded using a learned factorized model and
transmitted as side information. At both the encoder
and decoder, a hyper-synthesis network extracts
statistical features from $\hat z$, while an
autoregressive context model uses previously
coded or decoded latents $\hat y_{<i}$. Their outputs
are combined to estimate the mean and scale of
a conditional Gaussian:
\begin{equation}
\begin{aligned}
\psi &= h_s(\hat z),\\
\phi_i &= g_{cm}(\hat y_{<i}),\\
(\mu_i,\sigma_i)&=g_{ep}(\psi,\phi_i).
\end{aligned}
\label{eq:minnen-parameters}
\end{equation}
Unlike the earlier scale-only hyperprior, the
joint model predicts both the expected latent value
and its uncertainty. A masked $5\times5$ convolution
ensures that the context model accesses only
previously available symbols. The predicted
probabilities are reproduced identically at the
encoder and decoder, enabling arithmetic coding
without explicitly transmitting the Gaussian
parameters.

Using the probability chain rule, the conditional
entropy model factorizes as
\begin{equation}
p(\hat y\mid\hat z)
=\prod_i p(\hat y_i\mid\hat z,\hat y_{<i}).
\label{eq:minnen-factorization}
\end{equation}
Unlike a fully factorized entropy model, this
decomposition explicitly captures dependencies
between latent symbols through causal conditioning.
The hyperprior provides additional transmitted side
information, whereas the autoregressive model
exploits previously decoded symbols without requiring
additional context bits.

Each symbol is modeled using a Gaussian convolved
with a unit-width uniform distribution. For an
integer symbol $k$, its probability mass is
\begin{equation}
p_i(k)={}
\Phi\left(\frac{k+1/2-\mu_i}{\sigma_i}\right)
-\Phi\left(\frac{k-1/2-\mu_i}{\sigma_i}\right),
\label{eq:minnen-gaussian-bins}
\end{equation}
where $\Phi$ is the standard Gaussian cumulative
distribution function. More accurate predictions
assign higher probabilities to the actual symbols,
reducing their expected arithmetic-coding cost.

Since both the main latents and hyper-latents must
be transmitted, the complete rate--distortion
objective is
\begin{equation}
\mathcal L=\mathbb E\big[
-\log_2 p(\hat y\mid\hat z)
-\log_2 p_{\hat z}(\hat z)
+\lambda d(x,\hat x)\big].
\label{eq:minnen-rate-distortion}
\end{equation}
The first two terms account for the coding rates
of the main representation and hyperprior side
information, respectively, while the final term
penalizes reconstruction distortion. The hyperprior
is beneficial when the reduction in main-latent
coding cost exceeds the overhead of transmitting
$\hat z$. During training, additive uniform noise
provides a differentiable approximation to
quantization.

Fig.~\ref{fig:minnen-prior} illustrates the complete
architecture, including both entropy-coding paths
and the joint probability estimation network.

On the Kodak dataset, the joint model achieved
a reported 15.8\% average rate reduction relative
to the earlier hierarchical baseline
\cite{minnen2018}. However, its masked spatial
context introduces sequential decoding dependencies,
limiting parallelization. The authors evaluated
autoregressive variants using estimated Shannon
code lengths rather than benchmarking a complete
autoregressive decoder. This computational
bottleneck motivates more efficient context
modeling approaches, including ELIC
\cite{he2022elic}.

\begin{figure*}[!t]
    \centering
    \includegraphics[width=0.92\textwidth]
        {Minnen2018_Figure1_original.png}
    \caption{Joint autoregressive and hierarchical
    image compression architecture, showing the
    main latent and hyperprior coding paths and
    their shared entropy-parameter network.
    Reproduced from Fig.~1 of
    Minnen et al.~\cite{minnen2018}.}
    \label{fig:minnen-prior}
\end{figure*}





\subsection{Efficient Learned Image Compression (ELIC)}
\label{subsec:elic}

Although Minnen \emph{et al.}~\cite{minnen2018} improve
entropy estimation using a hyperprior and spatial
autoregressive context, their decoder must evaluate
probabilities sequentially across spatial positions.
He \emph{et al.}~\cite{he2022elic} propose ELIC to improve
the rate--distortion--complexity trade-off by combining
uneven channel grouping with parallel spatial context.

The motivation is \emph{information compaction}: learned
latent channels have unequal energy and coding importance,
and under channel-conditional training the earlier groups
tend to be more informative. ELIC's analysis transform
produces $M=320$ latent channels and divides them into
five groups rather than the ten equally sized slices of
earlier channel-conditional methods~\cite{minnen2020channel}:
\begin{equation}
\begin{aligned}
\hat y &= [\hat y^{(1)},\ldots,\hat y^{(5)}],\\
(C_1,\ldots,C_5)&=(16,16,32,64,192).
\end{aligned}
\label{eq:elic-group-sizes}
\end{equation}
The groups are decoded in order, so group $k$ can use
$\hat y^{(<k)}$---all previously decoded groups---to
predict its symbol probabilities. Smaller early groups
permit finer conditioning where it is most useful; the
large final group reduces the number of sequential
channel-context evaluations. Grouping does not discard
any latent coefficients.

ELIC's \emph{space-channel context} (SCCTX) also exploits
spatial correlations within each group using a checkerboard
partition~\cite{he2021checkerboard}. In pass 1, all
\emph{anchor} positions $A$ are predicted using the
hyperprior $\hat z$ and previous channel groups. In pass 2,
\emph{non-anchor} positions $B$ are additionally conditioned
on the recovered anchors. With
$\mathcal C_k=(\hat z,\hat y^{(<k)})$, this gives
\begin{equation}
p(\hat y^{(k)}\mid\mathcal C_k)
={}p(\hat y_A^{(k)}\mid\mathcal C_k)
\times p(\hat y_B^{(k)}\mid\hat y_A^{(k)},\mathcal C_k).
\label{eq:elic-spatial-factorization}
\end{equation}
Within each pass, scalar-symbol probabilities are
conditionally factorized, allowing parallel neural
probability estimation. The entropy-parameter network
fuses hyperprior features, channel context, and available
spatial context to predict the Gaussian mean and scale
$(\mu_i,\sigma_i)$, as in
Eq.~\eqref{eq:minnen-gaussian-bins}.
Thus, five groups with two checkerboard passes each require
only $5\times2=10$ sequential main-latent
probability-estimation stages, rather than a raster scan
over $HW$ positions. These stages do not imply that
arithmetic decoding or total computation is fully parallel.
Fig.~\ref{fig:elic-scctx} illustrates the schedule.


% ============================================================
% ELIC: Uneven Channel Grouping and Checkerboard Context
% ============================================================

\begin{figure*}[!t]
\centering
\begin{tikzpicture}[
    >=Latex,
    font=\footnotesize,
    group/.style={
        draw=black!60,
        fill=blue!7,
        rounded corners=2pt,
        minimum width=2.2cm,
        minimum height=0.9cm,
        align=center
    },
    flow/.style={-Latex,semithick},
    context/.style={-Latex,semithick,green!45!black}
]

\node[group,minimum width=13.0cm] (latent)
    at (6,5.2)
    {Main latent representation $\hat{y}$:
    $320\times H\times W$};

\foreach \k/\c in {1/16,2/16,3/32,4/64,5/192}{

    \pgfmathsetmacro{\xx}{3*(\k-1)}

    \node[group] (g\k) at (\xx,3.9)
        {Group $\k$\\$C_\k=\c$};

    \draw[flow] (latent.south -| g\k.north)
        -- (g\k.north);

    % Anchor decoding pass
    \begin{scope}[shift={(\xx-0.6,2.1)}]
        \foreach \r in {0,...,3}{
            \foreach \s in {0,...,3}{
                \pgfmathtruncatemacro{\parity}
                    {mod(\r+\s,2)}
                \ifnum\parity=0
                    \filldraw[
                        fill=blue!50,
                        draw=white
                    ]
                    (\s*0.3,\r*0.3)
                    rectangle ++(0.3,0.3);
                \else
                    \filldraw[
                        fill=black!8,
                        draw=white
                    ]
                    (\s*0.3,\r*0.3)
                    rectangle ++(0.3,0.3);
                \fi
            }
        }
        \draw[black!40] (0,0) rectangle (1.2,1.2);
    \end{scope}

    \draw[flow] (g\k.south) -- (\xx,3.3);

    % Non-anchor decoding pass
    \begin{scope}[shift={(\xx-0.6,0.2)}]
        \foreach \r in {0,...,3}{
            \foreach \s in {0,...,3}{
                \pgfmathtruncatemacro{\parity}
                    {mod(\r+\s,2)}
                \ifnum\parity=0
                    \filldraw[
                        fill=blue!50,
                        draw=white
                    ]
                    (\s*0.3,\r*0.3)
                    rectangle ++(0.3,0.3);
                \else
                    \filldraw[
                        fill=green!50,
                        draw=white
                    ]
                    (\s*0.3,\r*0.3)
                    rectangle ++(0.3,0.3);
                \fi
            }
        }
        \draw[black!40] (0,0) rectangle (1.2,1.2);
    \end{scope}

    \draw[flow] (\xx,2.1) -- (\xx,1.4);

    \pgfmathtruncatemacro{\firststage}{2*\k-1}
    \pgfmathtruncatemacro{\secondstage}{2*\k}

    \node at (\xx,-0.15)
        {Stages $\firststage$--$\secondstage$};

    \ifnum\k<5
        \draw[context]
        (\xx+0.6,0.8)
        -- (\xx+1.5,0.8)
        -- (\xx+1.5,2.7)
        -- (\xx+2.4,2.7);
    \fi
}

\node[anchor=east,align=right] at (-0.85,2.7)
    {Pass 1:\\Anchors};

\node[anchor=east,align=right] at (-0.85,0.8)
    {Pass 2:\\Non-anchors};

\node[align=center,green!40!black] at (6,-0.65)
    {Decoded channel groups provide context
    for subsequent groups};

\filldraw[fill=blue!50,draw=black!30]
    (2.8,-1.15) rectangle ++(0.28,0.28);
\node[anchor=west] at (3.15,-1.01) {Anchor symbols};

\filldraw[fill=green!50,draw=black!30]
    (7.1,-1.15) rectangle ++(0.28,0.28);
\node[anchor=west] at (7.45,-1.01) {Non-anchor symbols};

\end{tikzpicture}

\caption{Uneven channel grouping and space-channel
contextual adaptive coding in ELIC. The 320 latent
channels are partitioned into groups of 16, 16, 32,
64, and 192 channels. Each group is decoded using
two checkerboard passes, requiring ten sequential
main-latent probability-estimation stages. Each
completed group becomes available as channel context
for subsequent groups, while the hyperprior is shared
across all groups. Conceptual illustration based on
\cite{he2022elic}.}
\label{fig:elic-scctx}
\end{figure*}


% ============================================================
% Main Transforms, Experimental Results, and Limitations
% ============================================================

In the main analysis and synthesis transforms, ELIC uses
stacks of residual bottleneck blocks in place of GDN/IGDN,
with attention modules in the full model. The smaller
ELIC-sm variant reduces transform complexity. ELIC retains
\emph{scalar} coding: its mean-centered quantizer transmits
$r_i=\operatorname{round}(y_i-\mu_i)$ and reconstructs
$\hat y_i=r_i+\mu_i$. Training still minimizes a
rate--distortion objective that includes both main-latent
and hyperprior bits, with differentiable approximations
to quantization. Early channel groups also support
progressive image previews~\cite{he2022elic}.

On Kodak, the authors report a $-7.88\%$ BD-rate relative
to their VVC YUV 4:4:4 baseline and $49.16$ ms neural
decoding latency. In the entropy-model ablation,
uneven grouping plus checkerboard context improves BD-rate
from $-5.02\%$ to $-5.63\%$ while reducing entropy-parameter
latency from $19.41$ to $10.10$ ms compared with equal
grouping plus checkerboard~\cite{he2022elic}.

A limitation is that group boundaries are hand-selected,
and SCCTX retains inter-group and two-pass dependencies.
The reported neural inference times also exclude the full
cost of bitstream coding. Unlike the vector quantization
used in RDVQ, ELIC groups channels for \emph{entropy
modeling} but continues to encode scalar residual symbols.



\subsection{Differentiable Vector Quantization for Rate--Distortion Optimization (RDVQ)}
\label{subsec:rdvq}

\subsubsection{Motivation and Architecture}

The preceding learned codecs use scalar quantization (SQ), in which
individual latent coefficients are rounded and entropy-coded. Jiang
\emph{et al.}~\cite{jiang2026rdvq} instead propose RDVQ, a generative
compression model based on \emph{vector quantization} (VQ). A vector
quantizer represents an entire latent feature vector by one entry of a
learned codebook, allowing joint channel-wise patterns to be captured.
However, the nearest-neighbor assignment is discrete: its index has
zero derivative almost everywhere with respect to the encoder output.
Consequently, the coding-rate objective cannot directly guide the
encoder to choose more predictable indices.

For an input image $x$, the encoder produces $y=g_a(x)$. Given a
codebook $\mathcal C=\{c_1,\ldots,c_K\}$, each latent vector $y_i$ is
quantized as
\begin{equation}
\begin{aligned}
 s_i&=\arg\min_{k}\|y_i-c_k\|_2^2,\\
 \hat y_i&=c_{s_i},\qquad \hat x=g_s(\hat y).
\end{aligned}
\label{eq:rdvq-hard-vq}
\end{equation}
The stored symbols are the \emph{integer indices} $s_i$, not the
floating-point codewords. RDVQ uses a VQ autoencoder adapted from
LlamaGen with attention removed and three latent scales at downsampling
factors $64$, $32$, and $16$. All scales share a $4096\times32$
codebook. For a $256\times256$ image, the scales give
$4^2+8^2+16^2=336$ indices. Uniform 12-bit storage would require
$336\times12/256^2\simeq0.0615$ bits per pixel (bpp), but learned
entropy coding can reduce the actual average cost.

A masked autoregressive Transformer estimates the conditional
probability $q_\psi(s_i\mid s_{\mathrm{pred}(i)})$ of each codebook index
from previously available tokens. Its backbone has 12 layers, eight
attention heads, and 768-dimensional embeddings. A coarse-to-fine
spatial ordering captures dependencies within and across latent scales,
with causal attention preventing access to undecoded indices. Unlike
ELIC's Gaussian model for scalar residuals, RDVQ predicts a
categorical distribution over $4096$ codebook entries.

\begin{figure}[!t]
\centering
\begin{tikzpicture}[
 >=Latex,
 every node/.style={font=\scriptsize},
 block/.style={draw=black!55,rounded corners=2pt,
  fill=black!3,align=center,text width=2.55cm,
  minimum height=0.58cm,inner sep=2pt},
 hard/.style={block,fill=blue!9,draw=blue!55!black},
 soft/.style={block,fill=green!9,draw=green!50!black},
 link/.style={-Latex,semithick,draw=black!70},
 grad/.style={-Latex,dashed,semithick,draw=green!45!black}]
\node[block] (x) at (0,0) {Input image $x$};
\node[block] (enc) at (0,-0.90) {Multiscale encoder $g_a$};
\node[hard] (vq) at (-1.72,-2.03)
 {Hard VQ indices $s_i$\\and embeddings $c_{s_i}$};
\node[soft] (p) at (1.72,-2.03)
 {Soft assignments\\$p_{i,k}$};
\node[hard] (dec) at (-1.72,-3.30)
 {Image decoder $g_s$\\distortion $\mathcal L_D$};
\node[soft] (ent) at (1.72,-3.30)
 {Masked Transformer\\probabilities $q_{i,k}$};
\node[soft] (rate) at (1.72,-4.45)
 {Cross-entropy rate\\$\mathcal L_R$};
\draw[link] (x) -- (enc);
\draw[link] (enc.south) -- ++(0,-0.28) -| (vq.north);
\draw[link] (enc.south) -- ++(0,-0.28) -| (p.north);
\draw[link] (vq) -- (dec);
\draw[link] (vq.east) -- ++(0.17,0) |- (ent.west);
\draw[link] (p.south) -- ++(0,-0.16) -| (rate.east);
\draw[link] (ent) -- (rate);
\draw[grad] (rate.south) -- (1.72,-5.01)
 -- (3.38,-5.01) -- (3.38,-0.90) -- (enc.east);
\node[anchor=west,text=green!40!black]
 at (1.78,-4.87) {rate gradient};
\end{tikzpicture}
\caption{RDVQ's two training branches. Hard codewords are used for
reconstruction and causal entropy context, while soft codebook
assignments provide differentiable rate feedback to the encoder.
Conceptual diagram based on Jiang \emph{et al.}~\cite{jiang2026rdvq}.}
\label{fig:rdvq-training-paths}
\end{figure}

\subsubsection{Differentiable Rate--Distortion Objective}

RDVQ keeps the hard assignments of Eq.~\eqref{eq:rdvq-hard-vq} for
reconstruction but introduces a \emph{soft distribution} over the
codebook for rate optimization. For each latent vector, it defines
\begin{equation}
 p_{i,k}=\frac{\exp(-\|y_i-c_k\|_2^2/\tau)}
 {\sum_{j=1}^{K}\exp(-\|y_i-c_j\|_2^2/\tau)},
 \label{eq:rdvq-soft-probability}
\end{equation}
where $\tau>0$ is a temperature parameter. As $\tau\to0^+$, the
probabilities approach a one-hot nearest-neighbor assignment whenever
the closest codeword is unique. For finite $\tau$, they remain
differentiable. Denoting the Transformer's predicted probability of
code $k$ at position $i$ by $q_{i,k}$, the relaxed rate loss is
\begin{equation}
 \mathcal L_R=-\frac{1}{L}\sum_{i=1}^{L}
 \sum_{k=1}^{K}p_{i,k}\log q_{i,k}.
 \label{eq:rdvq-soft-rate}
\end{equation}
Unlike the hard index cost $-\log_2 q_\psi(s_i\mid
s_{\mathrm{pred}(i)})$, this cross-entropy supplies an explicit
gradient to the encoder through $p_{i,k}$. In particular, holding
$q_{i,k}$ fixed and writing $\bar c_i=\sum_j p_{i,j}c_j$,
\begin{equation}
 \nabla_{y_i}p_{i,k}=\frac{2p_{i,k}}{\tau}
 (c_k-\bar c_i).
 \label{eq:rdvq-soft-gradient}
\end{equation}
Thus the rate loss can encourage the encoder to select codewords
that are easier for the entropy model to predict, while reconstruction
losses preserve image quality~\cite{jiang2026rdvq}.

The complete training objective is
\begin{equation}
\begin{aligned}
 \mathcal L&=\mathcal L_D+\lambda\mathcal L_R,\\
 \mathcal L_D&=\mathcal L_{\mathrm{codebook}}+\mathcal L_{\mathrm{MSE}}
 \quad+\mathcal L_{\mathrm{LPIPS}}
 +0.1\mathcal L_{\mathrm{GAN}}.
\end{aligned}
\label{eq:rdvq-overall-loss}
\end{equation}
The codebook loss aligns encoder features with their selected vectors;
MSE measures pixel error, LPIPS encourages perceptual similarity, and
the GAN term promotes realistic textures. \emph{Here $\lambda$ weights
the rate term}, unlike the $R+\lambda D$ convention used for the
earlier scalar-quantized codecs in this report.

\subsubsection{Training, Coding, and Evaluation}

Training has three stages: first, the autoencoder and codebook are
pretrained for reconstruction; second, the frozen tokenizer provides
indices to train the entropy model; finally, the encoder, decoder,
and entropy model are jointly optimized for rate and distortion while
the codebook remains fixed. The authors then fine-tune at higher
resolutions~\cite{jiang2026rdvq}.

The soft probabilities are used \emph{only during training} and are
never transmitted. At evaluation, hard nearest-neighbor indices are
entropy-coded using causal probabilities reproduced by the decoder.
The decoded indices retrieve the shared codewords and produce $\hat x$.
Keeping the reconstruction path hard during training reduces the
soft-to-hard mismatch, although the relaxed rate remains a surrogate
for the actual coding cost. The measured bitrate is
\begin{equation}
 R_{\mathrm{actual}}=\frac{|b|_{\mathrm{bits}}}{HW},
 \label{eq:rdvq-actual-bpp}
\end{equation}
for the serialized bitstream $b$ of an $H\times W$ image. It must not
be confused with the soft training loss or an entropy-based bitrate
estimate. The released implementation provides an actual rANS
bitstream path~\cite{rdvqcode2026}. RDVQ also supports limited
bitrate adjustment by transmitting a prefix of indices and predicting
the remaining ones autoregressively.

\subsubsection{Results and Limitations}

On Kodak, DIV2K validation, and CLIC2020 test, the authors report
strong perceptual rate--distortion performance at very low bitrates.
Their DIV2K ablation achieves DISTS $0.1005$ at $0.0247$ bpp, compared
with DISTS $0.1253$ for a K-means VQ alternative at the same bitrate.
Removing the differentiable relaxation worsens DISTS to $0.2147$,
but also changes the bitrate to $0.0464$ bpp, so that comparison is
not rate-matched~\cite{jiang2026rdvq}. These results support the
benefit of differentiable, entropy-aware codeword learning over
heuristic codebook-size control.

Compared with Ball\'{e} \emph{et al.}, Minnen \emph{et al.}, and ELIC,
RDVQ changes the quantization unit from individual scalar values to
learned vectors and predicts categorical codebook-index probabilities.
Its main limitation is that the soft rate loss approximates, rather
than equals, actual hard-index coding cost; autoregressive decoding
also retains causal dependencies. Moreover, perceptual gains do not
guarantee better PSNR or SSIM. Accordingly, our reproduction will
compare RDVQ with JPEG on identical images using actual bitstream bpp,
PSNR, SSIM, and checked entropy decoding.


\section{Comparative Analysis of Image Compression Approaches}
\label{sec:comparative-analysis}

The reviewed papers illustrate how image compression has evolved
from hand-designed transforms to learned representations and increasingly
expressive entropy models. The key distinction is between improving a
\emph{decoded image} and improving the \emph{compressed representation}.
JPEG artifact removal changes reconstructed pixels without modifying the
original JPEG bitstream; the other codecs determine which symbols are
stored and how those symbols are compressed. Table~\ref{tab:codec-comparison}
summarizes their main differences.

\begin{table*}[!t]
\centering
\caption{Technical progression of the reviewed approaches. CNN JPEG
restoration is a separate decoder-side task, not a new entropy codec.}
\label{tab:codec-comparison}
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.16}
\begin{tabular}{@{}p{2.18cm}p{3.05cm}p{5.35cm}p{5.45cm}@{}}
\toprule
Approach & Coding unit & Main contribution & Remaining limitation \\
\midrule
JPEG \cite{wallace1992} & Quantized $8\times8$ DCT coefficients
& Fixed transform, quantization tables, and symbol coding
& Strong quantization causes blocking, ringing, and lost detail \\
\addlinespace[2pt]
JPEG + CNN \cite{ye2026} & Unchanged JPEG bitstream
& Learns a post-decoding correction to reconstructed pixels
& Extra decoder inference; does not lower the original bitrate \\
\addlinespace[2pt]
Ball\'{e} \emph{et al.} \cite{balle2016} & Quantized scalar neural latents
& Learns analysis/synthesis transforms jointly with a rate--distortion objective
& Factorized prior does not explicitly model latent dependencies \\
\addlinespace[2pt]
Minnen \emph{et al.} \cite{minnen2018} & Scalar latents and hyper-latents
& Combines transmitted hyperprior information with causal spatial context
& More accurate probabilities require sequential context evaluation \\
\addlinespace[2pt]
ELIC \cite{he2022elic} & Scalar latents in uneven channel groups
& Combines channel context with two-pass checkerboard spatial prediction
& Group/pass dependencies remain, although probability estimation is more parallel \\
\addlinespace[2pt]
RDVQ \cite{jiang2026rdvq} & Vector-quantized codebook indices
& Uses differentiable index assignments to make the rate loss influence the encoder
& Soft rate is a surrogate; causal index decoding and perceptual trade-offs remain \\
\bottomrule
\end{tabular}
\end{table*}

\begin{figure*}[!t]
\centering
\begin{tikzpicture}[
 >=Latex,
 every node/.style={font=\footnotesize},
 box/.style={draw=black!55,rounded corners=2pt,align=center,
   fill=black!2,text width=2.62cm,minimum height=0.76cm,inner sep=3pt},
 fixed/.style={box,fill=blue!9,draw=blue!60!black},
 learned/.style={box,fill=green!8,draw=green!50!black},
 cod/.style={box,fill=orange!9,draw=orange!55!black},
 flow/.style={-Latex,semithick,draw=black!70},
 branch/.style={-Latex,semithick,draw=green!50!black}]
 \node[box] (x) at (0,0) {Source image $x$};
 % Existing JPEG bitstream branch
 \node[fixed] (j) at (3.25,1.45) {JPEG encode/decode\\fixed stored bits $b_J$};
 \node[fixed] (r) at (6.65,1.45) {CNN pixel restoration\\$\hat x_J=y+f_\theta(y)$};
 \node[box,text width=3.20cm] (jrate) at (10.85,1.45)
   {Input rate remains\\$R_J=|b_J|/(WH)$};
 \draw[flow] (x.east) -- (1.62,0) |- (j.west);
 \draw[flow] (j.east) -- (r.west);
 \draw[flow] (r.east) -- (jrate.west);
 % Learned encoder / vector or scalar branch
 \node[learned] (a) at (3.25,-1.45) {Learned analysis\\$y=g_a(x)$};
 \node[learned] (sq) at (6.65,-0.88) {Scalar-quantized latents\\Ball\'{e}, Minnen, ELIC};
 \node[learned] (vq) at (6.65,-2.05) {Vector codebook indices\\RDVQ};
 \node[cod,text width=3.20cm] (entropy) at (10.85,-1.45)
   {Entropy-coded learned bits\\rate depends on symbol model};
 \draw[flow] (x.east) -- (1.62,0) |- (a.west);
 \draw[branch] (a.east) -- (4.93,-1.45) |- (sq.west);
 \draw[branch] (a.east) -- (4.93,-1.45) |- (vq.west);
 \draw[flow] (sq.east) -- (8.34,-0.88) |- (entropy.west);
 \draw[flow] (vq.east) -- (8.34,-2.05) |- (entropy.west);
 \node[anchor=west,font=\scriptsize\bfseries,text=black!65]
   at (0,2.36) {(a) Fixed-bitstream restoration};
 \node[anchor=west,font=\scriptsize\bfseries,text=black!65]
   at (0,-2.82) {(b) Learned bitstream generation};
\end{tikzpicture}
\caption{Distinction between JPEG post-processing and learned compression.
The upper branch improves decoded pixels at the original input JPEG rate;
the lower branch creates a new compressed representation. Within the
learned-codec branch, scalar and vector quantization are different ways
of defining the symbols to be entropy-coded.}
\label{fig:comparison-taxonomy}
\end{figure*}

\emph{From fixed transforms to learned representations.}
Classical JPEG uses a predetermined blockwise DCT, quantization tables,
and entropy-coding rules \cite{wallace1992}. The transform is not adapted
end-to-end to a training distribution. Ball\'{e} \emph{et al.}
\cite{balle2016} changed this design by learning nonlinear analysis
and synthesis transforms, then jointly optimizing coding rate and
reconstruction distortion. Instead of transmitting quantized DCT
coefficients, the codec transmits quantized neural features. This
provides more flexibility than JPEG, but a factorized entropy model
still treats the latent coefficients as independent for coding purposes.
By contrast, the residual CNN used for JPEG artifact removal
\cite{ye2026} does not replace the JPEG transform or entropy coder:
it can improve the decoded image, but cannot reduce the bits already
stored. The upper and lower paths in Fig.~\ref{fig:comparison-taxonomy}
therefore address different problems.

\emph{From independent latents to conditional probability models.}
The next limitation was no longer only the transform but the entropy
model. Ball\'{e} \emph{et al.}'s scale-hyperprior work
\cite{balle2018hyperprior} introduced transmitted side information
that helps predict image-dependent latent statistics. Minnen
\emph{et al.}~\cite{minnen2018} combined this hierarchical information
with an autoregressive spatial context derived from previously decoded
symbols. Compared with the factorized Ball\'{e} model, their conditional
Gaussian predictions exploit more dependencies, potentially assigning
shorter codes to likely latent values. The improvement has a cost:
the hyperprior consumes extra bits, and a raster-scan context model
must wait for preceding symbols before estimating later ones.

\emph{From accurate context to efficient context.}
ELIC \cite{he2022elic} addresses the sequential bottleneck of
spatial autoregression without abandoning scalar quantization.
Rather than predicting each spatial location in a long raster scan,
it divides 320 latent channels into groups of $(16,16,32,64,192)$
and predicts checkerboard anchor positions before non-anchor positions
within each group. The resulting five groups and two passes yield ten
sequential main-latent probability-estimation stages, with parallel
prediction within each pass. Compared with Minnen's approach, ELIC
therefore changes \emph{when and how context is computed}, not the
basic type of symbol being coded. Its uneven grouping also reflects
the observation that early channel groups tend to carry more useful
information. ELIC is not fully parallel: later groups depend on earlier
ones, and the entropy coder still processes discrete symbols.

\emph{From scalar coefficients to discrete visual tokens.}
RDVQ \cite{jiang2026rdvq} follows a different direction. Unlike
Ball\'{e}, Minnen, and ELIC, which entropy-code quantized scalar
coefficients, RDVQ maps a latent \emph{vector} to a learned codeword
and transmits its index. Its autoregressive Transformer predicts a
categorical distribution over indices, rather than a Gaussian
probability for each scalar residual. The central challenge is that
hard nearest-neighbor codebook selection blocks useful gradients
from the rate term. RDVQ therefore uses soft assignments for a
differentiable rate loss while retaining hard codewords for
reconstruction. Compared with ELIC's emphasis on efficient conditional
coding, RDVQ emphasizes joint rate optimization of vector-quantized
representations and perceptual fidelity at very low bitrates. It does
not eliminate causal entropy-decoding dependencies, and better
perceptual quality need not imply better pixelwise fidelity.

Overall, the progression is \emph{fixed transform $\rightarrow$
learned transform $\rightarrow$ richer entropy priors $\rightarrow$
more efficient context modeling}, followed by a complementary shift
toward \emph{rate-aware vector quantization}. These methods should
not be treated as a single sequence in which each universally
outperforms its predecessor: they target different bottlenecks in
representation learning, probability modeling, computational cost,
and reconstruction quality.



\section{Implementation and Experiments}
\label{sec:implementation}
Our 2 implementation tasks investigate different ways of using learning methods to improve image coding. We first considered a restoration network, which receives an ordinary decoded JPEG image and attempts to recover information lost during compression. In this implementation the JPEG bitstream is kept fixed and only the reconstructed pixels change. Next, we considered learned compression. In learned compression the representation to be stored and sent is itself optimized. The following experiments establish the restoration baseline and examine its behaviour at different JPEG quality factors.

\subsection{DNN-Based Image Restoration}
\label{sec:dnn-restoration}
\textbf{
Report dataset identity and split policy, source image format, all preprocessing,
training qualities, crop sizes, architecture/parameter count, optimizer, epochs,
seed, and checkpoint-selection rule. Compare JPEG and the CNN on the same evaluation crops.
Suggested sections: Introduction, Method, Experimental Setup, Results, Analysis,
and Conclusion. Optional extensions include a tiny U-Net, L1 versus MSE, runtime analysis, and repeated seeds.}

We implement a residual CNN for JPEG artifact removal
and evaluate its reconstruction quality on held-out
test images across different compression levels.


\subsubsection{Dataset and Preprocessing}

The restoration experiments use the histopathology
image patches specified in the project notebook,
which directs users to the ADPPatches collection
and the local \texttt{data\_1um\_bicubic} directory.

We use the supplied \texttt{train}, \texttt{val},
and \texttt{test} directories, containing 12,616,
1,576 and 1,576 images, respectively, according
to the executed dataset check.

Source images are converted to RGB before processing.
The displayed test example originates from a PNG file,
although the dataset loader also supports other formats,
including JPEG and TIFF. We therefore use the decoded
source crop as the reference image without assuming that
every source file was originally lossless.
 
 
In this dataset,
images are represented as 3-channel RGB tensors
with their pixel intensities normalized to $[0,1]$.
Training uses random $256\times256$ crops, random
flips and randomly selected JPEG quality factors.
In contrast, validation and testing use deterministic
$256\times256$ center crops.
The pipeline also documents resizing images that are
smaller than the requested crop size.
JPEG corruption is generated \emph{after} cropping, by JPEG encoding and decoding the clean patch at a selected quality factor, with chroma subsampling disabled (4:4:4). This yields a paired input $y$ and clean target $x$ with exactly the same dimensions. A single model is trained with JPEG qualities $Q\in\{10,20,30,40,50\}$, randomly sampled during training. All methods are evaluated on the same held-out test crops and the same JPEG inputs, avoiding differences caused by image selection or crop location.

\subsubsection{Residual CNN and Training}
Instead of reconstructing the image directly, we use a residual convolutional neural network (CNN) to predict the correction to the decoded JPEG input:
\begin{equation}
    \hat{x}=\operatorname{clip}_{[0,1]}
    \!\left(y+f_{\theta}(y)\right),
    \label{eq:restoration-cnn-output}
\end{equation}
where $f_{\theta}$ is the learned correction. In this formulation, a zero residual leaves the JPEG decoded image unchanged. In contrast, a nonzero correction can reduce compression artifacts. 

As shown in Fig.~\ref{fig:restoration-cnn-architecture}, the network has five $3\times3$ convolutions. The stride is 1 and the padding is 1. The first layer maps three RGB channels to 32 feature channels, the next 3 layers maintain 32 channels and the final layer maps the features back to three RGB correction channels. ReLU is the non linear activation function for the first 4 convolutions. The last convolution is linear. The input is added to the 3-channel output of
the fifth convolution through an
identity skip connection. It is important to note that we clamp
to $[0,1]$ their sum. 
The model has 29,507 trainable parameters, computed as $896+3(9{,}248)+867$.

\begin{figure*}[!t]
\centering
\begin{tikzpicture}[
    >=Latex,
    data/.style={draw=black!60,rounded corners=2pt,fill=black!3,
        minimum width=1.65cm,minimum height=1.02cm,
        align=center,font=\scriptsize,inner sep=2pt},
    layer/.style={data,fill=blue!7,draw=blue!55!black},
    result/.style={data,fill=green!10,draw=green!50!black},
    flow/.style={-Latex,semithick,draw=black!80},
    shortcut/.style={-Latex,semithick,dashed,draw=blue!70!black}]
    \node[data]   (input) at (0,0) {Decoded JPEG\\$y\in\mathbb{R}^{H\times W\times3}$};
    \node[layer]  (c1) at (2.1,0) {Conv $3\!\times\!3$\\$3\!\to\!32$; ReLU};
    \node[layer]  (c2) at (4.2,0) {Conv $3\!\times\!3$\\$32\!\to\!32$; ReLU};
    \node[layer]  (c3) at (6.3,0) {Conv $3\!\times\!3$\\$32\!\to\!32$; ReLU};
    \node[layer]  (c4) at (8.4,0) {Conv $3\!\times\!3$\\$32\!\to\!32$; ReLU};
    \node[layer]  (c5) at (10.5,0) {Conv $3\!\times\!3$\\$32\!\to\!3$; linear};
    \node[draw,circle,minimum size=7mm,inner sep=0pt,font=\large] (add) at (12.4,0) {$+$};

\node[data] (clip) at (13.65,0)
    {Clamp\\$[0,1]$};
\node[result] (out) at (15.55,0)
    {Restored RGB\\$\hat{x}$};


    \draw[flow] (input.east) -- (c1.west);
    \draw[flow] (c1.east) -- (c2.west);
    \draw[flow] (c2.east) -- (c3.west);
    \draw[flow] (c3.east) -- (c4.west);
    \draw[flow] (c4.east) -- (c5.west);
    \draw[flow] (c5.east) -- (add.west);
    \draw[flow] (add.east) -- (clip.west);
    \draw[flow] (clip.east) -- (out.west);

    \draw[shortcut] (input.south) -- ++(0,-1.27) -| (add.south);
    \node[font=\scriptsize,fill=white,inner sep=2pt,text=blue!65!black] at (6.1,-1.27)
        {identity (skip) connection};
    \node[font=\scriptsize,text=black!65] at (7.25,0.84)
        {All convolutions: stride $1$, padding $1$; $29{,}507$ parameters};
\end{tikzpicture}

\caption{Five-layer residual CNN used for JPEG
artifact removal. The network predicts three-channel
correction values that are added to the decoded
input, then clipped to $[0,1]$. The JPEG encoding
and the stored bitstream are not modified.}

\label{fig:restoration-cnn-architecture}
\end{figure*}

The network minimizes the mean absolute error (L1 loss) between the restored and clean RGB crops:
\begin{equation}
    \mathcal{L}_{\mathrm{L1}}(\theta)
    =\frac{1}{3HW}\sum_{c=1}^{3}\sum_{i=1}^{H}\sum_{j=1}^{W}
    \left|\hat{x}_{i,j,c}-x_{i,j,c}\right|.
    \label{eq:restoration-l1}
\end{equation}
Optimization uses AdamW with learning rate $2\times10^{-4}$, weight decay $10^{-4}$, batch size 16 and a cosine annealing learning-rate schedule. The random seed is 42. Training ran on CUDA for three epochs, with 789 mini-batches per epoch. After each epoch, the model was evaluated on the validation split. 
The best model checkpoint was selected according to
the highest restored validation PSNR and saved as
\texttt{best.pt}. This checkpoint was subsequently
used for final test-set evaluation without further
training or checkpoint selection on the test images. Validation PSNR increased from 31.11 to 31.37 and then 31.42 dB over the three epochs, while the L1 training loss decreased from 0.02264 to 0.02038. Therefore, we can consider our experiments as a computationally limited baseline since the final epoch still improved the validation PSNR. Fig.~\ref{fig:restoration-learning-curves} illustrates this trend.

\subsubsection{Evaluation Protocol}
We assess fidelity using peak signal-to-noise ratio (PSNR) and structural similarity (SSIM). We compare either the JPEG-decoded image $y$ or its restored version $\hat{x}$ against the clean crop $x$. For an RGB image normalized to $[0,1]$, PSNR is given by the following expression:
\begin{equation}
    \operatorname{PSNR}(\hat{x},x)
    =10\log_{10}\!\left(\frac{1}{\operatorname{MSE}(\hat{x},x)}\right),
    \label{eq:restoration-psnr}
\end{equation}
where MSE averages squared pixel errors over the three channels. The notebook computes PSNR separately for each image and averages the resulting dB values. For numerical stability it uses $\max(\operatorname{MSE},10^{-10})$ in the PSNR denominator and this caps the score at 100 dB for a perfect match. 

SSIM compares the local brightness, contrast and structural relationships of the two images \cite{wang2004ssim}. The implemented form is
\begin{equation}
\operatorname{SSIM}(x,\hat{x})=
\frac{(2\mu_x\mu_{\hat{x}}+C_1)(2\sigma_{x\hat{x}}+C_2)}
     {(\mu_x^2+\mu_{\hat{x}}^2+C_1)(\sigma_x^2+\sigma_{\hat{x}}^2+C_2)},
\label{eq:restoration-ssim}
\end{equation}
where $\mu$ denotes local mean intensity, $\sigma^2$ denotes local variance, and $\sigma_{x\hat{x}}$ denotes local covariance. We compute these statistics separately in each RGB channel using an $11\times11$ Gaussian window with standard deviation $1.5$. Then we average the resulting values over channels and valid spatial positions. For our intensity range, $C_1=0.01^2$ and $C_2=0.03^2$ stabilize the expression. Higher PSNR and SSIM indicate better quality for the decoded image each one under their respective criteria.

\subsubsection{Quantitative Results}

\textbf{
How much does the CNN improve PSNR and SSIM over JPEG?}
Table~\ref{tab:restoration-results} summarizes the mean PSNR, RGB SSIM and measured JPEG bitrate over all 1,576 held-out test crops, at each of seven JPEG quality factors. The quality factors required by the assignment ($Q=10,15,20,25,30$) are included, along with $Q=40$ and $Q=50$. The bitrate listed in the table is the original JPEG bitrate and is unchanged by CNN post-processing.

\begin{table*}[!t]
\caption{Full-test-set performance (1,576 crops per quality). PSNR is in dB. BPP is the average input JPEG bits per pixel.}
\label{tab:restoration-results}
\centering
\setlength{\tabcolsep}{5pt}
\small
\begin{tabular}{@{}rrrrrrrr@{}}
\toprule
$Q$ & BPP & JPEG PSNR & CNN PSNR & $\Delta$PSNR & JPEG SSIM & CNN SSIM & $\Delta$SSIM\\
\midrule
10 & 0.6002 & 26.3657 & 28.2078 & +1.8422 & 0.7708 & 0.8298 & +0.0590\\
15$^{\dagger}$ & 0.7465 & 27.8539 & 29.8326 & +1.9787 & 0.8122 & 0.8668 & +0.0546\\
20 & 0.8787 & 28.8730 & 30.8611 & +1.9880 & 0.8378 & 0.8869 & +0.0491\\
25$^{\dagger}$ & 1.0040 & 29.6422 & 31.5748 & +1.9326 & 0.8553 & 0.8994 & +0.0440\\
30 & 1.1187 & 30.2382 & 32.0939 & +1.8557 & 0.8681 & 0.9078 & +0.0397\\
40 & 1.3186 & 31.1346 & 32.8180 & +1.6834 & 0.8858 & 0.9184 & +0.0326\\
50 & 1.5075 & 31.8450 & 33.3319 & +1.4869 & 0.8985 & 0.9252 & +0.0267\\
\bottomrule
\end{tabular}
\end{table*}

Relative to JPEG, the restoration CNN improves PSNR by an average of 1.824 dB and SSIM by 0.0437 when the seven per-quality gains are averaged equally. \textbf{Does the CNN help at low Q more than high Q?} The improvement is evident under relatively strong compression. Particularly, at $Q=10$, PSNR increases by 1.84 dB and SSIM by 0.0590, compared with 1.49 dB and 0.0267 at $Q=50$. Nonetheless, this trend is not perfectly monotonic. The largest PSNR gain (1.99 dB) occurs at $Q=20$, while the largest SSIM gain occurs at $Q=10$. At the lowest quality, some high-frequency information has already been irreversibly quantized away, limiting what a spatial post-filter can reconstruct.

\emph{Generalization to unseen quality factors.} The checkpoint was trained with $Q\in\{10,20,30,40,50\}$, whereas we also evaluate $Q=15$ and $Q=25$ without retraining. 3. \textbf{What happens at unseen \color{red}Q = 20 and 40 \color{black} relative to seen qualities?} These two settings are unseen \emph{compression levels}, although all test images are from a held-out directory regardless of $Q$. At $Q=15$, CNN restoration increases PSNR from 27.85 to 29.83 dB and SSIM from 0.8122 to 0.8668. At $Q=25$, it increases PSNR from 29.64 to 31.57 dB and SSIM from 0.8553 to 0.8994. Thus we observe successful interpolation to unseen JPEG settings on the held-out test images. 

\begin{figure*}[!t]
\centering
\includegraphics[width=0.90\textwidth]{2-DNN-Based Image Restoration-Results/quality_curves.png}
\caption{Mean PSNR and RGB SSIM on the held-out test split as functions of JPEG quality. The CNN outperforms JPEG at all seven tested qualities.}
\label{fig:restoration-quality-curves}
\end{figure*}

\subsubsection{Qualitative Analysis and Limitations}
Figures~\ref{fig:restoration-q10}--\ref{fig:restoration-q40} compare the clean reference, the JPEG-decoded observation and the CNN output for the \emph{same} crop at 3 quality factors. The bottom row in each figure magnifies a pale central tissue region. 
The CNN learns corrections from paired JPEG-degraded
and reference images, allowing its convolutional
filters to use neighboring pixel information to
reduce blocking artifacts and local distortions.
This can improve the continuity of tissue
boundaries and reduce artificial block patterns,
although details permanently lost through
quantization cannot be guaranteed to be recovered. At $Q=10$, the JPEG reconstruction is affected by pronounced block boundaries and suppressed texture. The CNN removes some of the block pattern and improves PSNR from 26.56 to 28.67 dB and SSIM from 0.7394 to 0.8324. At $Q=20$, the CNN improves this crop from 28.96 to 31.41 dB and from 0.8184 to 0.8992 SSIM. Notably, it gives more continuous tissue boundaries and fewer spurious rectangular transitions. At $Q=40$, where JPEG quality is already higher, restoration still improves PSNR from 31.06 to 33.41 dB and SSIM from 0.8655 to 0.9308. However, the differences between the JPEG decoded image and the CNN restored one are less conspicuous.

\begin{figure*}[!t]
\centering
\includegraphics[width=0.88\textwidth]{2-DNN-Based Image Restoration-Results/comparison_000_q10.png}
\caption{One held-out ADP crop at strong compression ($Q=10$). Clean target, JPEG and CNN restoration are shown across columns, with centre-detail enlargements below. Image-specific input rate: 0.5449 bpp.}
\label{fig:restoration-q10}
\end{figure*}

\begin{figure*}[!t]
\centering
\includegraphics[width=0.88\textwidth]{2-DNN-Based Image Restoration-Results/comparison_000_q20.png}
\caption{The same held-out crop at $Q=20$, with identical JPEG input for the baseline and CNN. In this image the CNN raises PSNR from 28.96 to 31.41 dB and SSIM from 0.8184 to 0.8992. Image-specific rate: 0.7988 bpp.}
\label{fig:restoration-q20}
\end{figure*}

\begin{figure*}[!t]
\centering
\includegraphics[width=0.88\textwidth]{2-DNN-Based Image Restoration-Results/comparison_000_q40.png}
\caption{The same held-out crop at $Q=40$. Compression artifacts are less prominent than at $Q=10$, but the CNN still improves the numerical fidelity. Image-specific input rate: 1.2115 bpp.}
\label{fig:restoration-q40}
\end{figure*}

\textbf{Where do PSNR/SSIM disagree with visible quality?}
Although PSNR and SSIM consistently favor CNN restoration,
the qualitative comparisons reveal limitations of these
metrics as indicators of visual fidelity. At $Q=10$,
the CNN substantially suppresses JPEG blocking artifacts,
but some fine cellular details remain blurred or softened
relative to the reference. At $Q=40$, the numerical
improvements are still considerable, whereas the visual
differences in the full-size image are less noticeable.

These observations show that higher PSNR and SSIM
do not necessarily imply uniform improvements in every
image structure. In particular, smoothing may reduce
pixelwise reconstruction errors while also suppressing
subtle textures or weak tissue boundaries. Nevertheless,
our displayed examples do not show a direct disagreement
between PSNR and SSIM. Both metrics consistently favor
the CNN over JPEG. We therefore interpret the results
as evidence of improved overall reconstruction fidelity.


\begin{figure*}[!t]
\centering
\includegraphics[width=0.88\textwidth]{2-DNN-Based Image Restoration-Results/training_curves.png}
\caption{Three-epoch optimization history. Training L1 loss decreases while restored validation PSNR and SSIM continue to improve through epoch 3.}
\label{fig:restoration-learning-curves}
\end{figure*}

% Keep the final restoration floats before the subsequent compression section.

% Optional extra qualitative figure: uncomment if space permits.
% \begin{figure*}[!t]
% \centering
% \includegraphics[width=0.49\textwidth]{report_figures/comparison_000_q10.png}\hfill
% \includegraphics[width=0.49\textwidth]{report_figures/comparison_000_q40.png}
% \caption{The same test crop at the low and high JPEG qualities $Q=10$ and $Q=40$.}
% \label{fig:restoration-q10-q40}
% \end{figure*}

% Optional training-curves figure: uncomment if space permits.
% \begin{figure*}[!t]
% \centering
% \includegraphics[width=0.93\textwidth]{report_figures/training_curves.png}
% \caption{Training L1 loss and validation PSNR/SSIM over the three training epochs.}
% \label{fig:restoration-learning-curves}
% \end{figure*}

\subsection{DNN-Based Image Compression}
\label{sec:experimental-compression}

\subsubsection{Scope and relationship to RDVQ}
Our experiment implements a compact, single-scale, RDVQ-inspired neural codec
that reproduces the central idea of differentiable vector quantization coupled
with a rate--distortion objective. It is \emph{not} a complete reproduction
of Jiang \emph{et al.}'s generative RDVQ system~\cite{jiang2026rdvq}.
The original RDVQ uses multi-scale representations and a masked-transformer
autoregressive entropy model, allowing context-dependent coding probabilities
and limited-range prefix completion. Our implementation instead uses a small
convolutional autoencoder and a single learned categorical prior over vector
indices. This distinction is essential when interpreting our experimental
numbers and comparing them with published RDVQ results.

\subsubsection{Architecture and conversion to stored indices}
The input $\mathbf{x}\in[0,1]^{B\times3\times H\times W}$ is mapped to a
latent grid $\mathbf{z}=g_a(\mathbf{x})\in\mathbb{R}^{B\times D\times h\times w}$.
For the selected configuration, the encoder starts with a $4\times4$
stride-two convolution (three RGB channels to 64 feature channels), followed
by SiLU activation, a residual convolutional block and a $1\times1$
projection to $D=16$ latent channels. One downsampling level produces a
$32\times32$ grid from each $64\times64$ input crop. The residual block
contains two $3\times3$ convolutions with an intervening SiLU activation
and an identity skip connection.

The decoder approximately reverses this transformation: a $1\times1$
projection from 16 to 64 channels, a residual block, nearest-neighbor
upsampling by two, a $3\times3$ convolution with SiLU and a final $3\times3$
convolution and sigmoid to produce normalized RGB values. The entire model
contains 195,987 trainable parameters, including the $K\times D=256\times16$
learned codebook and $K$ categorical-prior logits. Table~\ref{tab:comp-settings}
records the selected configuration.

\begin{table}[!t]
\caption{Settings of the reported single-scale compression experiment.}
\label{tab:comp-settings}
\centering\footnotesize
\begin{tabular}{@{}ll@{}}\toprule
Parameter & Selected value \\ \midrule
Input crop / batch & $64\times64$ RGB / 32 \\
Width / latent channels & 64 / 16 \\
Downsampling levels & 1 (factor $2$) \\
Codebook entries $K$ & 256 \\
Training quantization & Straight-through \\
Epochs / learning rate & 40 / $2\times10^{-4}$ \\
Rate weight $\lambda$ & $10^{-4}$ \\
Main-stage temperature & $0.030437\rightarrow0.006087$ \\
Seed & 1512 \\
Sample budgets (train/val/test) & 1024 / 128 / 256 \\
Total trainable parameters & 195,987 \\ \bottomrule
\end{tabular}
\end{table}

The latent grid is flattened into $N=Bhw$ vectors
$\mathbf{z}_i\in\mathbb{R}^{16}$ and compared with codebook vectors
$\mathbf{c}_k\in\mathbb{R}^{16}$. The hard index is
\begin{equation}
 k_i=\underset{k\in\{0,\ldots,K-1\}}{\arg\min}
 \left\|\mathbf{z}_i-\mathbf{c}_k\right\|_2^2.
 \label{eq:comp-hardindex}
\end{equation}
The $32\times32$ index grid contains 1,024 integer symbols per image.
Because $K=256$, each symbol requires eight bits in a fixed-length
representation. Accordingly, uncompressed fixed-length index packing would
require $1024\times8/(64\times64)=2$ bits per input pixel (bpp).

For actual files, the indices are packed into bytes and compressed with
zlib in a decodable \texttt{.ecvq} stream. The container also stores the
input/latent dimensions and a model fingerprint so that decoding can
recover the correct grid and verify the matching model. At decoding,
each integer index is replaced by its codebook vector and passed through
the synthesis transform. The saved compressed stream and the corresponding
hard-quantized forward reconstruction are explicitly checked for equality
by the comparison implementation. The model parameters are shared between
images and are \emph{not} embedded in every \texttt{.ecvq} stream.

\subsubsection{Differentiable quantization and rate--distortion objective}
The discrete $\arg\min$ operation in~\eqref{eq:comp-hardindex} cannot provide
 gradients through changes in the selected index. We therefore use
a temperature-dependent soft distribution
\begin{equation}
 d_{ik}=\left\|\mathbf{z}_i-\mathbf{c}_k\right\|_2^2
 \end{equation}
 
 \begin{equation}
 p_{ik}(\tau)=\frac{\exp(-d_{ik}/\tau)}
 {\sum_{j=0}^{K-1}\exp(-d_{ij}/\tau)}
 \label{eq:comp-soft}
\end{equation}
  
  \begin{equation}
 \widetilde{\mathbf{z}}_i=\sum_{k=0}^{K-1}p_{ik}(\tau)\mathbf{c}_k.
 \label{eq:comp-softz}
\end{equation}



This operation compares each latent vector against all codewords and
produces a differentiable weighted mixture. \textbf{Why does smaller temperature approach nearest-neighbor quantization?} A small positive $\tau$ makes
most of the mass concentrate on the closest codeword, approaching hard VQ
as $\tau\to0$. \textbf{ What happens for large temperature? } Conversely, large temperatures
produce softer, more nearly uniform assignments. \textbf{Why is a weighted average of codeword indices not the same as a weighted average of codeword vectors?} Averaging the numerical
\emph{indices} would not be equivalent as integer labels carry no geometric
meaning and cannot be averaged. On the other hand, the codebook embeddings are learned 16-dimensional vectors and can be averaged numerically.

Our implementation learns $K$ logits $a_k$, giving one global categorical
prior $r_k=\exp(a_k)/\sum_j\exp(a_j)$. Thus the differentiable expected
coding cost, normalized by the number of \emph{input} pixels, is
\begin{equation}
 R_{\mathrm{soft}}=
 \frac{1}{BHW}\sum_{i=1}^{Bhw}\sum_{k=0}^{K-1}
 p_{ik}(\tau)\left[-\log_2 r_k\right].
 \label{eq:comp-rsoft}
\end{equation}
The distortion is the mean squared error over all RGB samples,
\begin{equation}
 D(\mathbf{x},\hat{\mathbf{x}})=
 \frac{1}{3BHW}\left\|\mathbf{x}-\hat{\mathbf{x}}\right\|_2^2,
 \label{eq:comp-distortion}
\end{equation}
and the joint objective is
\begin{equation}
 \mathcal{L}=D(\mathbf{x},\hat{\mathbf{x}})
 +\lambda R_{\mathrm{soft}},\qquad \lambda=10^{-4}.
 \label{eq:comp-rd}
\end{equation}

\textbf{ Why does increasing the rate penalty tend to trade fidelity for predictability? }

The distortion term promotes faithful reconstructions. The rate term
penalizes improbable index assignments under the learned prior.
A larger $\lambda$ therefore generally pushes the representation toward
more predictable symbols, potentially increasing reconstruction error.
The precise trade-off depends on the optimizer, quantizer, and coding model.

Adam jointly optimizes encoder, decoder, codebook and prior parameters. \textbf{Which parameters receive gradients from reconstruction and rate?}
Reconstruction gradients reach the decoder and via the differentiable
quantization surrogate, the encoder and codebook.  The rate term supplies
gradients to the prior logits and through $p_{ik}$, to the encoder and
codebook. Notable, it does not directly update the decoder. The training procedure
geometrically anneals the quantization temperature and clips the total
gradient norm to 1. 

\subsubsection{Training--evaluation distinction}
The reported run has \texttt{straight\_through=True}. In its training
forward pass, the decoder therefore receives hard codebook vectors, while
gradients use the differentiable soft mixture. With $\mathbf{z}^{h}$
denoting hard embeddings and $\widetilde{\mathbf{z}}$ the soft mixture,
this is implemented as
\begin{equation}
 \mathbf{z}^{\mathrm{ST}}=\widetilde{\mathbf{z}}
 +\operatorname{stopgrad}\!\left(
 \mathbf{z}^{h}-\widetilde{\mathbf{z}}\right).
 \label{eq:comp-ste}
\end{equation}
Numerically, $\mathbf{z}^{\mathrm{ST}}=\mathbf{z}^{h}$ in the forward pass,
whereas its backward derivative follows the soft path. This narrows the
forward-pass train--test mismatch relative to fully soft decoding, though
the gradient remains a surrogate. \textbf{Why can soft-training quality differ from hard-evaluation quality?}
A soft assignment produces a weighted combination of several
codebook vectors, which generally differs from selecting a
single nearest-neighbor vector. Consequently, fully soft
training can produce reconstructions that differ from those
obtained with hard quantization at inference. In our
straight-through implementation, the forward pass already
uses hard codewords, reducing this discrepancy, while the
backward pass retains approximate gradients through the
soft assignments.
 By contrast, the optional
\texttt{straight\_through=False} mode trains with soft mixtures themselves
and can exhibit an additional discrepancy when evaluation switches to
nearest-neighbor vectors.

At validation and test time, the codec always selects hard nearest-neighbor
indices, then estimates their coding cost using the same learned prior:
\begin{equation}
 R_{\mathrm{hard}}=
 \frac{1}{BHW}\sum_{i=1}^{Bhw}\left[-\log_2 r_{k_i}\right].
 \label{eq:comp-rhard}
\end{equation}
The saved checkpoint minimizes the \emph{hard-validation} score
$D_{\mathrm{val}}+\lambda R_{\mathrm{hard,val}}$. This run selected epoch~40.
Per-image PSNR and RGB SSIM are computed on hard reconstructions and then
averaged. 

\textbf{What does a collapsed codebook look like?}
A potential failure of vector quantization is
codebook collapse, where the encoder repeatedly
selects only a small subset of the available
codewords. This can reduce the diversity of
the latent representation and limit
reconstruction fidelity.

The evaluation log reports that 218 out of
256 codewords were used across the test set,
indicating that complete codebook collapse
did not occur. However, the frequency
distribution provides further insight
into how these indices are utilized.

\CompressionImageFigure{codeword_histogram.png}
{Frequency of hard codebook assignments in the
displayed test batch. Codeword usage is highly
non-uniform, with a small number of frequently
selected indices and many rarely selected ones.}
{fig:comp-codeword-histogram}

As shown in Fig.~\ref{fig:comp-codeword-histogram},
the codeword distribution is strongly
non-uniform. One codeword near index 60
is selected approximately 640 times,
while many other entries have much
smaller counts.

This concentration suggests that the
encoder favors certain learned
representations. Although non-uniform
usage is compatible with entropy-aware
compression, it may also indicate
partial codebook underutilization.

The histogram alone cannot establish
whether the concentration improves
coding efficiency or reduces
reconstruction quality. Nevertheless,
it demonstrates that the quantizer
uses multiple discrete codewords
rather than collapsing to a single
representation.


\subsubsection{Observed reconstruction and rate}
Table~\ref{tab:comp-test} summarizes the selected model's test
scores. The mean test PSNR and SSIM are 31.7366~dB and 0.9113, respectively.
Mean test MSE is $8.9888\times10^{-4}$. The learned-prior rate estimate is
1.9375~bpp, whereas the separately logged zlib-compressed latent payload
is 1.2763~bpp.


\paragraph{Training and Reconstruction Analysis}
Figure~\ref{fig:comp-learning} shows that both the
soft-training and hard-validation rate--distortion
losses decrease throughout training. Hard-validation
PSNR increases from approximately 28 to 31.7~dB,
while the estimated rate decreases from about
2.00 to 1.94~bpp. This suggests that the model
improves reconstruction fidelity while learning
a more predictable distribution of codebook indices.

Figure~\ref{fig:comp-ssim} shows that validation
SSIM also improves, rising from approximately
0.86 to 0.91 over 40 epochs. The improvement in
both PSNR and SSIM indicates better pixel-level
accuracy and structural similarity. However,
the estimated rate is not equivalent to the
actual compressed bitstream size.

The examples in Fig.~\ref{fig:comp-reconstruction}
show that the model preserves the main cellular
structures, tissue shapes and overall staining
patterns after hard quantization. Nevertheless,
some fine boundaries and textures are smoother
than in the original images, illustrating the
loss of high-frequency information introduced
by lossy compression.


\begin{table}[!t]
\caption{Held-out results of the reported compression checkpoint.}
\label{tab:comp-test}
\centering\footnotesize
\begin{tabular}{@{}lr@{}}\toprule
Metric & Result \\ \midrule
Test images & 256 \\
Mean PSNR & 31.7366 dB \\
Mean RGB SSIM & 0.9113 \\
Mean MSE & 0.00089888 \\
Estimated hard-prior rate & 1.9375 bpp \\
Compressed latent-only payload & 1.2763 bpp \\
Codewords used (evaluation set) & 218/256 \\
Selected epoch & 40 \\ \bottomrule
\end{tabular}
\end{table}

\CompressionWideFigure{learning_curves.png}
{Training history for the 40-epoch run: soft training loss, hard-validation
rate--distortion loss, hard-validation PSNR, and learned-prior estimated bpp.
These are \emph{not} measured file-size rates.}{fig:comp-learning}
\CompressionImageFigure{validation_ssim.png}
{Hard-validation RGB SSIM versus epoch; evaluation always uses hard codebook
assignments.}{fig:comp-ssim}
\CompressionWideFigure{reconstructions.png}
{Four held-out original image crops (top row) and hard-codebook decoder
reconstructions (bottom row). This figure is from the uploaded run.}
{fig:comp-reconstruction}

\subsubsection{Comparison with earlier learned codecs and limitations}
Ball\'{e} \emph{et al.}~\cite{balle2016} optimized nonlinear transforms and
scalar quantization using a continuous training proxy. Minnen
\emph{et al.}~\cite{minnen2018} introduced an autoregressive and hierarchical
probability model to exploit latent dependencies. ELIC~\cite{he2022elic}
further improves contextual adaptive entropy coding through uneven
space--channel grouping. Unlike these scalar-quantized approaches, RDVQ's
main contribution is an entropy-aware, differentiable distribution over
\emph{vector} codebook assignments. The full RDVQ system also predicts
conditional index probabilities with a masked transformer, and uses these
predictions both for coding and for limited-range test-time completion
\cite{jiang2026rdvq}.

Our teaching model isolates soft VQ but omits RDVQ's multi-scale tokenizer,
autoregressive transformer, and generative/perceptual objectives. Its
single global prior ignores spatial correlations among indices; the actual
teaching bitstreams used zlib rather than the paper's learned entropy-coding
system. The numerical results therefore demonstrate the behavior of the
simplified implementation, \emph{not} reproduction of the original paper's
full rate--distortion benchmark. Carefully controlled codebook-size and
rate-weight ablations, with unchanged data splits, crop size, seed, sample
budgets, and epoch budget, are needed before attributing improvements to a
particular design choice.

% Figure macro: before the image is uploaded, show a readable placeholder.
\providecommand{\QFourFigureFolder}{question4_figures}
\newcommand{\QFourWideFig}[3]{%
  \begin{figure*}[!t]
    \centering
    \IfFileExists{\QFourFigureFolder/#1}{%
      \includegraphics[width=0.96\textwidth]{\QFourFigureFolder/#1}%
    }{%
      \fbox{\parbox[c][1.22in][c]{0.88\textwidth}{\centering\footnotesize
        Figure pending upload: \texttt{\detokenize{#1}}\\
        Folder: \texttt{question4\_figures/}}}%
    }%
    \caption{#2}\label{#3}
  \end{figure*}%
}

\subsection{Compression Evaluation and Ablation Study}
\label{sec:compression-evaluation}

\subsubsection{Experimental Protocol and Complete-File Bitrate}
The purpose of this evaluation is to assess the learned codec as an
\emph{encoder--bitstream--decoder} system, rather than only measuring the
reconstruction quality of its neural autoencoder. The experiment uses a
fixed seed of 1512, 1024 training crops, 128 validation crops and 256
held-out test crops. The spatial crop size is $64\times64$ RGB pixels.
The baseline has codebook size $K=256$, latent dimension 16 and rate
weight $\lambda=10^{-4}$, with 40 training epochs and an eight-epoch
training-only warm start. The model is selected using validation data.
The held-out test images are reserved for the final comparison. For the
ablation experiments, the split, preprocessing, seed, training budget,
model design (except the swept parameter) and hard-quantized evaluation
procedure remain fixed.

For an image of height $H$ and width $W$, we distinguish the actual
\emph{complete-file} rate
\begin{equation}
R_{\mathrm{file}}=\frac{8\,B_{\mathrm{file}}}{HW}
\quad\text{bpp},
\label{eq:q4-file-bpp}
\end{equation}
from the compressed latent-payload rate
$R_{\mathrm{payload}}=8B_{\mathrm{payload}}/(HW)$ and the learned-prior
estimated rate $R_{\mathrm{est}}$. Here $B$ denotes the respective
number of bytes. The complete-file rate counts the neural codec's
stored representation and its per-file container overhead. JPEG is
measured from the entire saved JPEG file under the same definition.
The supplied run records zlib-coded
latent payloads for all 256 baseline examples. 

The reconstructed RGB images are evaluated against the same clean
references using PSNR and SSIM, with pixel values normalized to
$[0,1]$. For peak intensity 1,
\begin{equation}
\mathrm{PSNR}=10\log_{10}\!\left(\frac{1}{\mathrm{MSE}}\right),
\label{eq:q4-psnr}
\end{equation}
where MSE is the RGB mean squared error. SSIM is computed on RGB
images with the notebook's $11\times11$ Gaussian window, standard
deviation 1.5 and data range 1. Both metrics are computed per image
and averaged over the 256 test crops. The two ablation studies use
\emph{validation} estimated bpp for model selection, whereas the final
rate--distortion comparison uses measured \emph{test} complete-file bpp.

\subsubsection{Fair Comparison with JPEG}
Table~\ref{tab:q4-jpeg-test} reports JPEG operating points evaluated on
exactly the same 256 test crops as the neural baseline. JPEG quality
factor $Q$ is varied to trace its rate--distortion curve. The measured
neural baseline achieves $31.63$~dB PSNR and $0.9109$ SSIM at
$1.517$ full-file bpp ($1.253$ payload bpp). At the nearest reported
JPEG operating point, $Q=1$ yields $21.11$~dB and $0.5599$ SSIM at
$1.501$ bpp, a rate difference of just $0.016$ bpp. At this
approximately equal \emph{measured} rate, the neural baseline has a
$10.52$~dB PSNR advantage and a $0.3510$ absolute SSIM advantage.


\begin{table}[!t]
\centering\footnotesize
\caption{Measured test-set comparison over 256 common $64\times64$
RGB crops. Every rate is complete-file bpp; neural model weights are
excluded. Higher PSNR and SSIM are better.}
\label{tab:q4-jpeg-test}
\begin{tabular}{@{}lrrr@{}}
\toprule
Codec / quality & File bpp & PSNR (dB) & SSIM \\
\midrule
Neural baseline ($K=256$) & 1.517 & 31.63 & 0.9109 \\
JPEG $Q=1$  & 1.501 & 21.11 & 0.5599 \\
JPEG $Q=10$ & 1.755 & 26.79 & 0.7651 \\
JPEG $Q=20$ & 2.039 & 29.48 & 0.8326 \\
JPEG $Q=30$ & 2.283 & 30.86 & 0.8640 \\
JPEG $Q=40$ & 2.488 & 31.75 & 0.8823 \\
JPEG $Q=50$ & 2.679 & 32.46 & 0.8954 \\
JPEG $Q=70$ & 3.197 & 34.12 & 0.9192 \\
JPEG $Q=90$ & 4.968 & 37.47 & 0.9563 \\
\bottomrule
\end{tabular}
\end{table}

For JPEG, higher $Q$ increases both file size and fidelity. JPEG
at $Q=40$ reaches a PSNR close to the neural baseline
($31.75$ versus $31.63$~dB) but requires $2.488$ versus $1.517$ bpp. Nonetheless, its SSIM remains lower ($0.8823$ versus $0.9109$). JPEG eventually
surpasses the neural baseline on both metrics at larger rates (e.g.,
$Q=70$), demonstrating that the comparison is dependent on the
operating point. PSNR and SSIM need not rank reconstructions identically.
JPEG at $Q=50$ has greater PSNR ($32.46$~dB) but lower SSIM
($0.8954$) than the neural baseline. The full rate--distortion curves
in Fig.~\ref{fig:q4-measured-overview} show both metrics without
restricting attention to a single JPEG quality factor.

\QFourWideFig{q4_measured_rate_distortion_overview.png}{%
Measured test-set rate--distortion curves for JPEG and the neural
codec. Both panels use the actual saved-file bitrate; (left) RGB PSNR
and (right) RGB SSIM. This full view is essential because the ablation
zoom clips the low-quality JPEG measurements. All curves use the same
256 held-out images.}{fig:q4-measured-overview}

\subsubsection{Controlled Ablation I: Codebook Size}
The first controlled experiment changes only codebook size
$K\in\{32,64,128\}$ relative to the $K=256$ baseline, leaving
$\lambda=10^{-4}$ fixed. The training protocol, random seed and
validation set are held constant. Figure~\ref{fig:q4-codebook-val}
plots hard-quantized validation PSNR and SSIM against the \emph{estimated}
latent rate. Increasing $K$ from 32 to 256 raises validation PSNR
from $29.76$ to approximately $31.66$~dB and SSIM from $0.8869$ to
approximately $0.9119$. The corresponding estimated rate increases
from $1.198$ to approximately $1.939$ bpp. A larger codebook therefore
improves representation fidelity, but increases the estimated coding
cost. This is the expected capacity--rate trade-off rather than an
unqualified gain from larger $K$.

\QFourWideFig{codebook_validation_rate_distortion.png}{%
Codebook-size ablation on the validation set. Hard-quantized PSNR
(left) and RGB SSIM (right) are plotted against \emph{estimated}
latent bpp for $K=32,64,128,256$; $K=256$ is the baseline.
The estimated values are not actual compressed-file sizes.}{fig:q4-codebook-val}

On the independent test set, the complete-file results in
Table~\ref{tab:q4-ablation-test} confirm improved quality as $K$
increases. However, the actual bitrate is not monotonic: the $K=128$
model reaches $31.11$~dB at $1.762$ bpp, while the $K=256$ baseline
reaches \emph{higher} PSNR ($31.63$~dB) and SSIM ($0.9109$) at a
\emph{lower} full-file rate ($1.517$ bpp). Thus, $K=128$ is dominated
by the baseline under these measured test results. This illustrates why
an estimated categorical rate is insufficient by itself to assess the
end-to-end compressed file.

\subsubsection{Controlled Ablation II: Rate Multiplier}
The second experiment fixes $K=256$ and changes only the training
rate weight $\lambda\in\{0,10^{-3},10^{-2}\}$ relative to the
$10^{-4}$ baseline. In this implementation, the optimized objective is
\begin{equation}
\mathcal{L}=\mathrm{MSE}(x,\hat{x})+\lambda R_{\mathrm{soft}},
\label{eq:q4-sweep-objective}
\end{equation}
where $R_{\mathrm{soft}}$ is a differentiable rate surrogate from the
learned codebook distribution and global categorical prior, not an
actual byte count. Figure~\ref{fig:q4-rate-val} shows the resulting
hard-validation trade-off. With $\lambda=0$, the estimated rate is
$2.000$ bpp and PSNR is $31.65$~dB. With $\lambda=10^{-3}$, it drops
to $1.922$ bpp and $31.55$~dB and with $\lambda=10^{-2}$, it drops to
$1.848$ bpp and $30.84$~dB. The corresponding SSIM values are
$0.9114$, $0.9096$ and $0.9019$. Stronger rate regularization reduces
the estimated coding cost, while eventually sacrificing image quality.

\QFourWideFig{validation_rate_sweep.png}{%
Rate-weight ablation on the validation set. Hard-quantized PSNR
(left) and RGB SSIM (right) versus \emph{estimated} bpp for
$\lambda=0,10^{-4},10^{-3},10^{-2}$, with $10^{-4}$ denoting the
baseline. All settings use the same architecture and training budget.
}{fig:q4-rate-val}

The measured test-file results show the same broad trend. Increasing
$\lambda$ from $10^{-4}$ to $10^{-2}$ reduces full-file rate from
$1.517$ to $1.180$ bpp, while reducing PSNR from $31.63$ to
$30.88$~dB and SSIM from $0.9109$ to $0.9017$. Removing the rate term
($\lambda=0$) does not improve the measured PSNR over baseline and
produces a slightly larger file.

\begin{table}[!t]
\centering\scriptsize
\caption{Measured complete-file test results for both controlled
ablations (256 common images). Payload excludes file-container bytes;
all models use hard quantization at evaluation.}
\label{tab:q4-ablation-test}
\begin{tabular}{@{}lrrrr@{}}
\toprule
Configuration & File bpp & Payload bpp & PSNR & SSIM \\
\midrule
Baseline $K=256$, $\lambda=10^{-4}$ & 1.517 & 1.253 & 31.63 & .9109 \\
\multicolumn{5}{@{}l}{\emph{Codebook-size sweep, fixed $\lambda=10^{-4}$}} \\
$K=32$  & 1.266 & 1.003 & 29.70 & .8881 \\
$K=64$  & 1.441 & 1.178 & 30.55 & .8981 \\
$K=128$ & 1.762 & 1.498 & 31.11 & .9041 \\
\multicolumn{5}{@{}l}{\emph{Rate-weight sweep, fixed $K=256$}} \\
$\lambda=0$       & 1.558 & 1.294 & 31.62 & .9109 \\
$\lambda=10^{-3}$ & 1.479 & 1.215 & 31.47 & .9084 \\
$\lambda=10^{-2}$ & 1.180 & 0.917 & 30.88 & .9017 \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{Measured Rate--Distortion and Reconstruction Examples}
Figure~\ref{fig:q4-measured-zoom} presents a closer view of the learned
operating points using the actual \emph{full-file} rate, rather than the
validation-time rate surrogate. The rate-weight sweep trades modest
changes in reconstruction fidelity for smaller files, while the
codebook-size sweep exhibits non-monotonic file-size behavior.

\QFourWideFig{q4_measured_rate_distortion_zoom.png}{%
Detailed measured rate--distortion view of the learned-codec
ablations on the common test set. Panels show PSNR and RGB SSIM
against complete-file bpp. This zoom is not a substitute for the
full JPEG comparison in Fig.~\ref{fig:q4-measured-overview}.}
{fig:q4-measured-zoom}

Figures~\ref{fig:q4-reconstruction-0} and
\ref{fig:q4-reconstruction-1} compare the original tissue crops with
an approximately rate-matched JPEG reconstruction and the learned
baseline and ablated reconstructions. In test image~0, the JPEG $Q=1$
reconstruction exhibits pronounced block boundaries and color
quantization, whereas the learned reconstructions retain the main
purple cell structures. In test image~1, JPEG $Q=1$ breaks the
relatively smooth magenta tissue into large uniform blocks, while
neural reconstructions retain the large-scale nuclei and tonal
variation. Nonetheless, reduced-codebook and heavily
rate-regularized reconstructions tend to smooth fine texture and
small boundaries.

\QFourWideFig{reconstructions_image_0.png}{%
Qualitative example, held-out test image 0: original RGB crop,
approximately rate-matched low-quality JPEG, neural baseline,
rate-weight variants and codebook-size variants. The high-contrast
cell structures reveal both JPEG blocking and neural smoothing.
}{fig:q4-reconstruction-0}

\QFourWideFig{reconstructions_image_1.png}{%
Qualitative example, held-out test image 1: original magenta tissue
crop, approximately rate-matched JPEG and all trained neural
configurations. Larger nuclei are generally retained by the learned
codec; some fine texture is smoothed by stronger rate constraints.
}{fig:q4-reconstruction-1}

\subsubsection{Limitations and Reproducibility}
The results should be interpreted within several limits. First, the
teaching model is a small single-scale VQ autoencoder with a global
categorical prior, not the full RDVQ architecture with multiscale
representations and a causal autoregressive Transformer
\cite{jiang2026rdvq}. It therefore tests the central rate--distortion
idea without reproducing the original paper's coding performance.
Second, warm-start initialization uses the same procedure for every run,
but the resulting data-dependent temperature can differ across codebooks.
The codebook sweep therefore holds the protocol constant without
forcing an identical numerical temperature schedule for each $K$.
Third, the soft prior's estimated bpp, the zlib-compressed latent
payload, and the serialized file length differ substantially. For the
baseline, the measured file rate is $1.517$ bpp, the payload rate is
$1.253$ bpp and the validation estimated rate is approximately $1.94$
bpp. Consequently, surrogate-rate improvements need not translate into
monotonic file-size reductions across codebook configurations.
Fourth, the neural decoder's shared checkpoint is not counted as a
transmitted cost; for deployments with many small images or frequent
model changes, this assumption may be optimistic. Fifth, the test
set comprises a particular collection of only $64\times64$ crops.
JPEG headers contribute a relatively large fraction of these files,
and the results may not generalize to larger images, other tissue types,
or natural photographs. Finally, PSNR and RGB SSIM describe distortion
but not all clinically details. Smoothing
small structures could matter despite favorable aggregate scores.


In summary, the strongest supported conclusion is that the small learned codec
achieves substantially better distortion than JPEG at approximately
$1.5$ bpp on this specific set of small tissue crops, while the
importance of quantization capacity, rate weight and accurate
bitstream accounting is demonstrated by the ablation results.



\appendix
\section{Supplementary Compression Figure Atlas}
\label{app:compression-atlas}

This appendix presents the saved image-compression
results for four held-out RGB crops. It includes
the original images, reconstructed outputs from
hard vector quantization, and JPEG reconstructions
at multiple quality factors.

The additional rate--distortion figures illustrate
the relationship between reconstruction quality
and compressed representation size. All image
examples are obtained from the same test crops,
enabling consistent qualitative comparisons.
The observed differences are discussed in
Section~\ref{sec:compression-evaluation}.


\CompressionWideFigure{rate_distortion.png}
{Recorded JPEG and DNN rate--distortion plot. The horizontal axis uses
measured payload-only bpp for the DNN and complete-file bpp for JPEG;
these accounting definitions differ.}{fig:atlas-rd-psnr}
\CompressionWideFigure{rate_ssim.png}
{Recorded JPEG and DNN rate versus RGB SSIM. Compare trends cautiously
because the DNN and JPEG rate-accounting conventions differ.}
{fig:atlas-rd-ssim}
\CompressionWideFigure{decoded_image_comparison.png}
{Comparison of a saved DNN bitstream reconstruction
with the original image and JPEG at Q10.
The center zoom and absolute RGB-error maps
highlight local reconstruction differences.}
{fig:atlas-decoded-comparison}

\CompressionImageFigure{decoded_image.png}
{Reconstructed RGB image obtained by decoding
the stored quantized DNN bitstream using the
shared codebook and neural decoder.}
{fig:atlas-decoded-image}

\begin{figure*}[!p]
\centering
\CompressionThumb{image_0_original.png}{Original}
\CompressionThumb{image_0_decoded.png}{Hard DNN reconstruction}
\CompressionThumb{image_0_jpeg_q1.jpg}{JPEG Q1}
\par\vspace{0.65em}
\CompressionThumb{image_0_jpeg_q10.jpg}{JPEG Q10}
\CompressionThumb{image_0_jpeg_q20.jpg}{JPEG Q20}
\CompressionThumb{image_0_jpeg_q30.jpg}{JPEG Q30}
\par\vspace{0.65em}
\CompressionThumb{image_0_jpeg_q50.jpg}{JPEG Q50}
\CompressionThumb{image_0_jpeg_q70.jpg}{JPEG Q70}
\CompressionThumb{image_0_jpeg_q90.jpg}{JPEG Q90}
\caption{Image 0: original crop, hard-quantized DNN reconstruction,
and JPEG reconstructions at quality factors 1, 10, 20, 30, 50, 70, and 90.
The original image files are required for final visual interpretation.}
\label{fig:atlas-sample-0}
\end{figure*}

\begin{figure*}[!p]
\centering
\CompressionThumb{image_1_original.png}{Original}
\CompressionThumb{image_1_decoded.png}{Hard DNN reconstruction}
\CompressionThumb{image_1_jpeg_q1.jpg}{JPEG Q1}
\par\vspace{0.65em}
\CompressionThumb{image_1_jpeg_q10.jpg}{JPEG Q10}
\CompressionThumb{image_1_jpeg_q20.jpg}{JPEG Q20}
\CompressionThumb{image_1_jpeg_q30.jpg}{JPEG Q30}
\par\vspace{0.65em}
\CompressionThumb{image_1_jpeg_q50.jpg}{JPEG Q50}
\CompressionThumb{image_1_jpeg_q70.jpg}{JPEG Q70}
\CompressionThumb{image_1_jpeg_q90.jpg}{JPEG Q90}
\caption{Image 1: original crop, hard-quantized DNN reconstruction,
and JPEG reconstructions at quality factors 1, 10, 20, 30, 50, 70, and 90.
The original image files are required for final visual interpretation.}
\label{fig:atlas-sample-1}
\end{figure*}

\begin{figure*}[!p]
\centering
\CompressionThumb{image_2_original.png}{Original}
\CompressionThumb{image_2_decoded.png}{Hard DNN reconstruction}
\CompressionThumb{image_2_jpeg_q1.jpg}{JPEG Q1}
\par\vspace{0.65em}
\CompressionThumb{image_2_jpeg_q10.jpg}{JPEG Q10}
\CompressionThumb{image_2_jpeg_q20.jpg}{JPEG Q20}
\CompressionThumb{image_2_jpeg_q30.jpg}{JPEG Q30}
\par\vspace{0.65em}
\CompressionThumb{image_2_jpeg_q50.jpg}{JPEG Q50}
\CompressionThumb{image_2_jpeg_q70.jpg}{JPEG Q70}
\CompressionThumb{image_2_jpeg_q90.jpg}{JPEG Q90}
\caption{Image 2: original crop, hard-quantized DNN reconstruction,
and JPEG reconstructions at quality factors 1, 10, 20, 30, 50, 70, and 90.
The original image files are required for final visual interpretation.}
\label{fig:atlas-sample-2}
\end{figure*}

\begin{figure*}[!p]
\centering
\CompressionThumb{image_3_original.png}{Original}
\CompressionThumb{image_3_decoded.png}{Hard DNN reconstruction}
\CompressionThumb{image_3_jpeg_q1.jpg}{JPEG Q1}
\par\vspace{0.65em}
\CompressionThumb{image_3_jpeg_q10.jpg}{JPEG Q10}
\CompressionThumb{image_3_jpeg_q20.jpg}{JPEG Q20}
\CompressionThumb{image_3_jpeg_q30.jpg}{JPEG Q30}
\par\vspace{0.65em}
\CompressionThumb{image_3_jpeg_q50.jpg}{JPEG Q50}
\CompressionThumb{image_3_jpeg_q70.jpg}{JPEG Q70}
\CompressionThumb{image_3_jpeg_q90.jpg}{JPEG Q90}
\caption{Image 3: original crop, hard-quantized DNN reconstruction,
and JPEG reconstructions at quality factors 1, 10, 20, 30, 50, 70, and 90.
The original image files are required for final visual interpretation.}
\label{fig:atlas-sample-3}
\end{figure*}




\subsection{Compression Evaluation and Ablation Study}






\begin{thebibliography}{99}
\bibitem{gonzalez2008}
R. C. Gonzalez and R. E. Woods, \emph{Digital Image Processing}, 3rd ed.
Upper Saddle River, NJ, USA: Pearson Prentice Hall, 2008,
ch. 5, sec. 5.1, and ch. 8, secs. 8.1 and 8.2.8.

\bibitem{wallace1992}
G. K. Wallace, ``The JPEG still picture compression standard,''
\emph{IEEE Trans. Consumer Electron.}, vol. 38, no. 1,
pp. xviii--xxxiv, Feb. 1992, doi: 10.1109/30.125072.

\bibitem{plataniotisjpeg}
K. N. Plataniotis, ``Introduction to JPEG Coding,''
ECE1512 Digital Image Processing and Applications,
University of Toronto, course lecture slides.

\bibitem{ece1512jpeg2021}
ECE1512 Course Materials, ``Lossy Image Compression: JPEG and JPEG 2000,''
course lecture slides, Mar. 22, 2021.

\bibitem{libjpegquality}
Independent JPEG Group / libjpeg-turbo, ``JPEG quantization-table quality
scaling,'' \texttt{jcparam.c}. [Online]. Available:
\url{https://github.com/libjpeg-turbo/libjpeg-turbo/blob/main/src/jcparam.c}

\bibitem{ye2026}
L. Ye, ``From DNN Image Restoration to Learned Image Compression,''
ECE1512 Project B lecture slides, University of Toronto, Nov. 2026.

\bibitem{balle2016}
J. Ball\'{e}, V. Laparra, and E. P. Simoncelli, ``End-to-end optimized
image compression,'' \emph{arXiv preprint arXiv:1611.01704}, 2016.

\bibitem{minnen2018}
D. Minnen, J. Ball\'{e}, and G. D. Toderici,
``Joint autoregressive and hierarchical priors for learned image
compression,'' in \emph{Advances in Neural Information Processing
Systems (NeurIPS)}, vol. 31, 2018.
[Online]. Available:
\url{https://proceedings.neurips.cc/paper/2018/hash/53edebc543333dfbf7c5933af792c9c4-Abstract.html}

\bibitem{balle2018hyperprior}
J. Ball\'{e}, D. Minnen, S. Singh, S. J. Hwang, and N. Johnston,
``Variational image compression with a scale hyperprior,''
\emph{International Conference on Learning Representations (ICLR)}, 2018.
[Online]. Available: \url{https://arxiv.org/abs/1802.01436}

\bibitem{he2022elic}
D. He, Z. Yang, W. Peng, R. Ma, H. Qin, and Y. Wang,
``ELIC: Efficient learned image compression with
unevenly grouped space-channel contextual adaptive
coding,'' in \emph{Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition
(CVPR)}, Jun. 2022, pp. 5718--5727.
doi: 10.1109/CVPR52688.2022.00563.

\bibitem{minnen2020channel}
D. Minnen and S. Singh,
``Channel-wise autoregressive entropy models for
learned image compression,'' in \emph{2020 IEEE
International Conference on Image Processing (ICIP)},
2020, pp. 3339--3343.
[Online]. Available:
\url{https://arxiv.org/abs/2007.08739}

\bibitem{he2021checkerboard}
D. He, Y. Zheng, B. Sun, Y. Wang, and H. Qin,
``Checkerboard context model for efficient learned
image compression,'' in \emph{Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR)}, 2021, pp. 14771--14780.

\bibitem{jiang2026rdvq}
S. Jiang, W. Long, M. Han, Z. Chen, C. Zhu, and S. Gu,
``Differentiable vector quantization for rate-distortion
optimization of generative image compression,'' in
\emph{Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition (CVPR)}, Jun. 2026, pp. 14440--14450.
[Online]. Available: \url{https://arxiv.org/abs/2604.10546}

\bibitem{rdvqcode2026}
S. Jiang \emph{et al.}, ``RDVQ: Official implementation,''
2026. [Online]. Available: \url{https://github.com/CVL-UESTC/RDVQ}

\bibitem{hosseini2019adp}
M. S. Hosseini \emph{et al.}, ``Atlas of Digital Pathology: A generalized
hierarchical histological tissue type-annotated database for deep learning,''
in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, 2019.
[Online]. Available: \url{https://openaccess.thecvf.com/content_CVPR_2019/html/Hosseini_Atlas_of_Digital_Pathology_A_Generalized_Hierarchical_Histological_Tissue_Type-Annotated_CVPR_2019_paper.html}

\bibitem{dong2015arcnn}
C. Dong, Y. Deng, C. C. Loy, and X. Tang,
``Compression artifacts reduction by a deep convolutional network,''
in \emph{Proc. IEEE Int. Conf. Comput. Vis. (ICCV)}, 2015,
pp. 576--584.
[Online]. Available: \url{https://openaccess.thecvf.com/content_iccv_2015/html/Dong_Compression_Artifacts_Reduction_ICCV_2015_paper.html}

\bibitem{wang2004ssim}
Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli,
``Image quality assessment: From error visibility to structural similarity,''
\emph{IEEE Trans. Image Process.}, vol. 13, no. 4,
pp. 600--612, Apr. 2004, doi: 10.1109/TIP.2003.819861.

\end{thebibliography}

\end{document}
