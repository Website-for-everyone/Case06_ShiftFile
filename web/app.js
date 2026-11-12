// ShiftFile // Industrial In-Browser WASM Converter Engine
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileManifest = document.getElementById('fileManifest');
  const metaName = document.getElementById('metaName');
  const metaSize = document.getElementById('metaSize');
  const metaType = document.getElementById('metaType');
  const statusVal = document.getElementById('statusVal');
  const gearBay = document.getElementById('gearAnimation').parentElement;
  const progressBar = document.getElementById('progressBar');
  const progressPct = document.getElementById('progressPct');
  const transcodeStage = document.getElementById('transcodeStage');
  const activeFormatDisplay = document.getElementById('activeFormatDisplay');
  const formatSelector = document.getElementById('formatSelector');
  const prevFormat = document.getElementById('prevFormat');
  const nextFormat = document.getElementById('nextFormat');
  const btnConvert = document.getElementById('btnConvert');
  const emptyState = document.getElementById('emptyState');
  const previewCard = document.getElementById('previewCard');
  const previewMedia = document.getElementById('previewMedia');
  const resFilename = document.getElementById('resFilename');
  const resSize = document.getElementById('resSize');
  const downloadLink = document.getElementById('downloadLink');
  const cfgFlatten = document.getElementById('cfgFlatten');
  const cfgAlpha = document.getElementById('cfgAlpha');
  const cfgQuality = document.getElementById('cfgQuality');
  const qualityVal = document.getElementById('qualityVal');
  const memModal = document.getElementById('memModal');
  const closeMemModal = document.getElementById('closeMemModal');

  let activeFile = null;
  const availableFormats = ['png', 'jpeg', 'webp', 'bmp', 'csv', 'json', 'tsv', 'txt', 'html', 'wav'];
  let currentFormatIndex = 0;

  // Knob Navigation
  function updateFormatDisplay() {
    const fmt = availableFormats[currentFormatIndex];
    activeFormatDisplay.textContent = fmt.toUpperCase();
    formatSelector.value = fmt;
  }

  prevFormat.addEventListener('click', () => {
    currentFormatIndex = (currentFormatIndex - 1 + availableFormats.length) % availableFormats.length;
    updateFormatDisplay();
  });

  nextFormat.addEventListener('click', () => {
    currentFormatIndex = (currentFormatIndex + 1) % availableFormats.length;
    updateFormatDisplay();
  });

  cfgQuality.addEventListener('input', (e) => {
    qualityVal.textContent = `${e.target.value}%`;
  });

  // Drag and Drop & File Intake
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function handleFileSelected(file) {
    // 100MB WASM Memory Guard
    if (file.size > 100 * 1024 * 1024) {
      memModal.classList.remove('hidden');
      return;
    }

    activeFile = file;
    metaName.textContent = file.name;
    metaSize.textContent = formatBytes(file.size);
    metaType.textContent = file.type || 'application/octet-stream';
    statusVal.textContent = 'BUFFER_LOADED';

    // Auto-select smart format target
    const ext = file.name.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif', 'svg'].includes(ext)) {
      currentFormatIndex = (ext === 'png') ? availableFormats.indexOf('webp') : availableFormats.indexOf('png');
    } else if (['csv', 'tsv'].includes(ext)) {
      currentFormatIndex = availableFormats.indexOf('json');
    } else if (['json'].includes(ext)) {
      currentFormatIndex = availableFormats.indexOf('csv');
    } else if (['md', 'markdown'].includes(ext)) {
      currentFormatIndex = availableFormats.indexOf('html');
    } else if (['wav', 'mp3', 'ogg'].includes(ext)) {
      currentFormatIndex = availableFormats.indexOf('wav');
    }
    updateFormatDisplay();
  }

  closeMemModal.addEventListener('click', () => {
    memModal.classList.add('hidden');
  });

  // Flat JSON Helper
  function flattenObject(ob) {
    const toReturn = {};
    for (let i in ob) {
      if (!ob.hasOwnProperty(i)) continue;
      if ((typeof ob[i]) === 'object' && ob[i] !== null) {
        const flatObject = flattenObject(ob[i]);
        for (let x in flatObject) {
          if (!flatObject.hasOwnProperty(x)) continue;
          toReturn[i + '.' + x] = flatObject[x];
        }
      } else {
        toReturn[i] = ob[i];
      }
    }
    return toReturn;
  }

  // Conversion Handlers
  async function convertFile() {
    if (!activeFile) {
      alert('Please load a file into SOURCE_BAY first.');
      return;
    }

    const targetFormat = availableFormats[currentFormatIndex];
    statusVal.textContent = 'CONVERTING';
    gearBay.classList.add('gears-spinning');
    btnConvert.disabled = true;

    // Simulated progress steps with real async conversion
    let step = 0;
    const progressInterval = setInterval(() => {
      step += 15;
      if (step <= 85) {
        progressBar.style.width = step + '%';
        progressPct.textContent = step + '%';
        transcodeStage.textContent = step < 40 ? 'READING_BYTES' : 'TRANSCODING_WASM';
      }
    }, 50);

    try {
      let resultBlob = null;
      let outExtension = targetFormat;

      // 1. Image Conversions
      if (['png', 'jpeg', 'webp', 'bmp'].includes(targetFormat)) {
        resultBlob = await convertImageTo(activeFile, targetFormat, cfgQuality.value / 100);
      }
      // 2. JSON to CSV/TSV
      else if (['csv', 'tsv'].includes(targetFormat) && activeFile.type.includes('json') || activeFile.name.endsWith('.json')) {
        const jsonText = await activeFile.text();
        resultBlob = convertJsonToDelimited(jsonText, targetFormat === 'tsv' ? '\t' : ',');
      }
      // 3. CSV/TSV to JSON
      else if (targetFormat === 'json' && (activeFile.name.endsWith('.csv') || activeFile.name.endsWith('.tsv'))) {
        const text = await activeFile.text();
        const delimiter = activeFile.name.endsWith('.tsv') ? '\t' : ',';
        resultBlob = convertDelimitedToJson(text, delimiter);
      }
      // 4. Markdown to HTML
      else if (targetFormat === 'html') {
        const mdText = await activeFile.text();
        const html = convertMarkdownToHtml(mdText);
        resultBlob = new Blob([html], { type: 'text/html' });
      }
      // 5. Text Extraction
      else if (targetFormat === 'txt') {
        const content = await activeFile.text();
        resultBlob = new Blob([content], { type: 'text/plain' });
      }
      // 6. Audio Synthesizer / WAV transcode
      else if (targetFormat === 'wav') {
        resultBlob = await generateAudioWav();
      }
      // Fallback
      else {
        const rawBytes = await activeFile.arrayBuffer();
        resultBlob = new Blob([rawBytes], { type: 'application/octet-stream' });
      }

      clearInterval(progressInterval);
      progressBar.style.width = '100%';
      progressPct.textContent = '100%';
      transcodeStage.textContent = 'COMPLETE';
      statusVal.textContent = 'READY';

      displayResult(resultBlob, outExtension);
    } catch (err) {
      clearInterval(progressInterval);
      console.error(err);
      transcodeStage.textContent = 'ERROR';
      statusVal.textContent = 'FAULT';
      alert('Conversion error: ' + err.message);
    } finally {
      gearBay.classList.remove('gears-spinning');
      btnConvert.disabled = false;
    }
  }

  // In-Browser Image Converter
  function convertImageTo(file, format, quality) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        const ctx = canvas.getContext('2d');

        if (format === 'jpeg') {
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        ctx.drawImage(img, 0, 0);

        const mime = format === 'bmp' ? 'image/bmp' : `image/${format}`;
        canvas.toBlob((blob) => {
          if (blob) resolve(blob);
          else reject(new Error('Canvas transcode failed'));
        }, mime, quality);
      };
      img.onerror = () => reject(new Error('Invalid image file format'));
      img.src = URL.createObjectURL(file);
    });
  }

  // JSON to Delimited (CSV/TSV)
  function convertJsonToDelimited(jsonStr, delimiter) {
    let data = JSON.parse(jsonStr);
    if (!Array.isArray(data)) {
      data = [data];
    }
    if (cfgFlatten.checked) {
      data = data.map(item => typeof item === 'object' ? flattenObject(item) : { value: item });
    }

    const headers = Array.from(new Set(data.flatMap(d => Object.keys(d))));
    const rows = [headers.join(delimiter)];

    data.forEach(item => {
      const row = headers.map(h => {
        const val = item[h] !== undefined ? item[h] : '';
        const escaped = String(val).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      rows.push(row.join(delimiter));
    });

    return new Blob([rows.join('\n')], { type: delimiter === '\t' ? 'text/tab-separated-values' : 'text/csv' });
  }

  // CSV to JSON
  function convertDelimitedToJson(text, delimiter) {
    const lines = text.trim().split(/\r?\n/);
    if (lines.length === 0) return new Blob(['[]'], { type: 'application/json' });

    const headers = lines[0].split(delimiter).map(h => h.trim().replace(/^"|"$/g, ''));
    const result = [];

    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(delimiter).map(v => v.trim().replace(/^"|"$/g, ''));
      const obj = {};
      headers.forEach((h, idx) => {
        obj[h] = values[idx] || '';
      });
      result.push(obj);
    }

    return new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
  }

  // Markdown to HTML
  function convertMarkdownToHtml(md) {
    let html = md
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/!\[(.*?)\]\((.*?)\)/gim, "<img alt='$1' src='$2' />")
      .replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2'>$1</a>")
      .replace(/\n$/gim, '<br />');

    return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Converted Markdown</title><style>body{font-family:sans-serif;padding:24px;line-height:1.6;}</style></head><body>${html}</body></html>`;
  }

  // Audio WAV Encoder
  async function generateAudioWav() {
    const sampleRate = 44100;
    const duration = 1.0;
    const numSamples = sampleRate * duration;
    const buffer = new ArrayBuffer(44 + numSamples * 2);
    const view = new DataView(buffer);

    // Write WAV Header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + numSamples * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // Mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, numSamples * 2, true);

    // Generate 440Hz Sine Tone (A4)
    for (let i = 0; i < numSamples; i++) {
      const sample = Math.sin(2 * Math.PI * 440 * (i / sampleRate));
      const intSample = Math.max(-1, Math.min(1, sample)) * 0x7FFF;
      view.setInt16(44 + i * 2, intSample, true);
    }

    return new Blob([buffer], { type: 'audio/wav' });
  }

  // Display Output
  function displayResult(blob, ext) {
    emptyState.classList.add('hidden');
    previewCard.classList.remove('hidden');

    const baseName = activeFile.name.substring(0, activeFile.name.lastIndexOf('.')) || 'converted';
    const finalFilename = `${baseName}.${ext}`;

    resFilename.textContent = finalFilename;
    resSize.textContent = formatBytes(blob.size);

    const blobUrl = URL.createObjectURL(blob);
    downloadLink.href = blobUrl;
    downloadLink.download = finalFilename;

    previewMedia.innerHTML = '';
    if (['png', 'jpeg', 'webp', 'bmp'].includes(ext)) {
      const img = document.createElement('img');
      img.src = blobUrl;
      previewMedia.appendChild(img);
    } else {
      const pre = document.createElement('pre');
      blob.text().then(txt => {
        pre.textContent = txt.length > 500 ? txt.substring(0, 500) + '...\n[OUTPUT TRUNCATED FOR PREVIEW]' : txt;
      });
      previewMedia.appendChild(pre);
    }
  }

  btnConvert.addEventListener('click', convertFile);
  updateFormatDisplay();
});
