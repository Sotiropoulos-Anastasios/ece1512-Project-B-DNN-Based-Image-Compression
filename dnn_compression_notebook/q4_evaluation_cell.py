# QUESTION 4: DECODABLE BITSTREAM + JPEG TEST EVALUATION
# Insert just after the existing Step 8 compare_jpeg cell.
import csv
from collections import defaultdict
from codec import compress, decompress, payload_size
from comparison import jpeg_roundtrip

Q4_DIR = RUN_DIR / 'q4_ablation_results'
Q4_DIR.mkdir(parents=True, exist_ok=True)
rate_runs = json.loads((RUN_DIR / 'validation_sweep.json').read_text())
codebook_runs = json.loads((RUN_DIR / 'codebook_sweep.json').read_text())

# Evaluate the saved baseline + all independently trained ablation checkpoints.
experiments = [dict(label='Baseline', ablation='Baseline',
                    k=MODEL_CONFIG['codebook_size'],
                    rate_weight=TRAIN_CONFIG['rate_weight'],
                    checkpoint=str(RUN_DIR / 'best.pt'))]
experiments += [dict(label=f'lambda={r["rate_weight"]:g}', ablation='Rate weight',
                     k=MODEL_CONFIG['codebook_size'], rate_weight=r['rate_weight'],
                     checkpoint=r['checkpoint']) for r in rate_runs]
experiments += [dict(label=f'K={r["codebook_size"]}', ablation='Codebook size',
                     k=r['codebook_size'], rate_weight=r['rate_weight'],
                     checkpoint=r['checkpoint']) for r in codebook_runs]

# Freeze the exact same held-out images for ALL variants and JPEG.
test_images = [t.cpu() for batch in loaders['test'] for t in batch]
assert test_images, 'Test loader is empty'
assert len({e['label'] for e in experiments}) == len(experiments)
jpeg_qualities = (1, 5, 10, 15, 20, 25, 30, 40, 50, 70, 90)
examples_to_save = (0, 1)
rows = []
example_images = {}

def record(label, ablation, index, nbytes, npayload, reference, recovered):
    h, w = reference.shape[-2:]
    rows.append(dict(label=label, ablation=ablation, image=index,
                     pixels=h*w, file_bytes=nbytes, payload_bytes=npayload,
                     psnr=float(psnr_per_image(recovered[None], reference[None])[0]),
                     ssim=float(ssim_per_image(recovered[None], reference[None])[0])))
    if index in examples_to_save:
        example_images[(label, index)] = recovered.permute(1, 2, 0).numpy()

# JPEG is encoded once per quality on the same images, with fixed settings.
for i, original in enumerate(test_images):
    image_array = original.permute(1, 2, 0).numpy()
    for q in jpeg_qualities:
        jpg_bytes, jpg_decoded = jpeg_roundtrip(image_array, q, optimize=False)
        jpg_tensor = torch.from_numpy(jpg_decoded.copy()).permute(2, 0, 1)
        record(f'JPEG Q{q}', 'JPEG', i, len(jpg_bytes), len(jpg_bytes),
               original, jpg_tensor)

# Load each saved model and decode the actual serialized stream.
for exp in experiments:
    name = exp['label']
    net, _ = load_checkpoint(exp['checkpoint'], soft_quantize, DEVICE)
    assert net.config['codebook_size'] == exp['k']
    net.eval()
    with torch.no_grad():
        for i, original in enumerate(test_images):
            stream = compress(net, original[None].to(DEVICE))
            decoded = decompress(net, stream)[0].cpu()
            if i == 0:  # A bitstream round-trip consistency check
                forward = net(original[None].to(DEVICE))['reconstruction'][0].cpu()
                torch.testing.assert_close(decoded, forward, atol=1e-6, rtol=1e-5)
            decoded_8bit = (decoded.clamp(0, 1) * 255).round() / 255
            record(name, exp['ablation'], i, len(stream), payload_size(stream),
                   original, decoded_8bit)
    print('Evaluated', name, 'on', len(test_images), 'test images')
    del net

with (Q4_DIR / 'per_image.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

# Aggregate bpp by TOTAL bytes / TOTAL pixels, metrics by mean per-image score.
summary = []
for exp in experiments + [dict(label=f'JPEG Q{q}', ablation='JPEG',
                               k='', rate_weight='', checkpoint='') for q in jpeg_qualities]:
    group = [r for r in rows if r['label'] == exp['label']]
    summary.append(dict(label=exp['label'], ablation=exp['ablation'],
                        k=exp.get('k', ''), rate_weight=exp.get('rate_weight', ''),
                        checkpoint=exp.get('checkpoint', ''), images=len(group),
                        file_bpp=8*sum(r['file_bytes'] for r in group)/sum(r['pixels'] for r in group),
                        payload_bpp=8*sum(r['payload_bytes'] for r in group)/sum(r['pixels'] for r in group),
                        psnr=float(np.mean([r['psnr'] for r in group])),
                        ssim=float(np.mean([r['ssim'] for r in group]))))
with (Q4_DIR / 'summary.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

lookup = {r['label']: r for r in summary}
for item in summary:
    print(f'{item["label"]:12s} file BPP={item["file_bpp"]:.3f} | '
          f'payload BPP={item["payload_bpp"]:.3f} | '
          f'PSNR={item["psnr"]:.2f} | SSIM={item["ssim"]:.4f}')

# Two rate-distortion plots. Both axes use measured complete-stream rates.
jpeg_points = sorted((r for r in summary if r['ablation'] == 'JPEG'),
                     key=lambda r: r['file_bpp'])
for metric, title in [('psnr', 'PSNR (dB)'), ('ssim', 'RGB SSIM')]:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot([r['file_bpp'] for r in jpeg_points], [r[metric] for r in jpeg_points],
            'o-', label='JPEG')
    for tag, labels, marker in [
        ('Codebook K', ['K=64', 'K=128', 'Baseline'], 's--'),
        ('Rate weight', ['lambda=0', 'Baseline', 'lambda=0.001', 'lambda=0.01'], '^--')
    ]:
        points = sorted([lookup[label] for label in labels if label in lookup],
                        key=lambda r: r['file_bpp'])
        ax.plot([r['file_bpp'] for r in points], [r[metric] for r in points],
                marker, label=tag)
        for p in points:
            ax.annotate(p['label'], (p['file_bpp'], p[metric]),
                        xytext=(4, 5), textcoords='offset points', fontsize=8)
    ax.set(xlabel='Actual full-file bits per pixel', ylabel=title)
    ax.grid(alpha=.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(Q4_DIR / f'rate_distortion_{metric}.png', dpi=180)
    plt.show()

# The JPEG example closest to the baseline's AGGREGATE full-file bpp.
matching_jpeg = min(jpeg_points,
                    key=lambda r: abs(r['file_bpp'] - lookup['Baseline']['file_bpp']))
columns = ['Original', matching_jpeg['label']] + [exp['label'] for exp in experiments]
for i in examples_to_save:
    if i >= len(test_images):
        continue
    fig, axes = plt.subplots(1, len(columns), figsize=(2.5*len(columns), 3.2))
    for ax, label in zip(axes, columns):
        image = (test_images[i].permute(1, 2, 0).numpy() if label == 'Original'
                 else example_images[(label, i)])
        ax.imshow(np.clip(image, 0, 1))
        ax.set_title(label, fontsize=10)
        ax.axis('off')
    fig.suptitle(f'Test image {i} | JPEG match rate gap: '
                 f'{abs(matching_jpeg["file_bpp"] - lookup["Baseline"]["file_bpp"]):.3f} bpp',
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(Q4_DIR / f'reconstructions_image_{i}.png', dpi=180)
    plt.show()
print('Question 4 results saved in:', Q4_DIR.resolve())
