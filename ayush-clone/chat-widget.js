/* ============================================================
   chat-widget.js — handles fullscreen overlay chat + API calls
   ============================================================ */

(function () {
  const chatWindow = document.getElementById("chatWindow");
  const chatOverlay = document.getElementById("chatOverlay");
  const chatToggle = document.getElementById("chatToggle");
  const closeChat = document.getElementById("closeChat");
  const chatBody = document.getElementById("chatBody");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  function openChat() {
    chatWindow.classList.add("open");
    chatOverlay.classList.add("open");
    chatToggle.classList.add("hidden");
    chatInput.focus();
  }

  function closeChatFn() {
    chatWindow.classList.remove("open");
    chatOverlay.classList.remove("open");
    chatToggle.classList.remove("hidden");
  }

  chatToggle.addEventListener("click", openChat);
  closeChat.addEventListener("click", closeChatFn);
  chatOverlay.addEventListener("click", closeChatFn);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && chatWindow.classList.contains("open")) {
      closeChatFn();
    }
  });

  function clearBody() {
    chatBody.innerHTML = "";
  }

  function appendUserMsg(text) {
    const div = document.createElement("div");
    div.className = "msg user";
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return div;
  }

  function getJurisdiction() {
    const sel = document.getElementById("jurisdictionSelect");
    return sel ? sel.value : "all";
  }

  function makeSrcChip(src) {
    const chip = document.createElement("span");
    chip.className = "src-chip";
    chip.textContent = src.source + (src.category ? " (" + src.category + ")" : "");
    if (src.relevance_score !== undefined) {
      chip.title = "Relevance: " + (src.relevance_score * 100).toFixed(0) + "%";
    }
    return chip;
  }

  function makeSrcPanel(title, panelClass, sources) {
    if (!sources || sources.length === 0) return null;
    const panel = document.createElement("div");
    panel.className = "src-panel " + panelClass;
    const t = document.createElement("div");
    t.className = "src-panel-title";
    t.textContent = title;
    panel.appendChild(t);
    sources.forEach(function (s) { panel.appendChild(makeSrcChip(s)); });
    return panel;
  }

  function appendMeta(div, data) {
    // Confidence badge
    if (data.confidence) {
      const badge = document.createElement("span");
      badge.className = "meta-tag confidence " + data.confidence;
      badge.textContent = "Confidence: " + data.confidence;
      div.appendChild(badge);
    }
    if (data.demo_mode) {
      const demoTag = document.createElement("span");
      demoTag.className = "meta-tag demo";
      demoTag.textContent = "Demo mode";
      div.appendChild(demoTag);
    }

    // TKDL prior-art pointer
    if (data.tkdl_pointer) {
      const p = document.createElement("div");
      p.className = "tkdl-pointer";
      p.textContent = data.tkdl_pointer;
      div.appendChild(p);
    }

    // Legal disclaimer on every answer
    const disclaimerText = data.disclaimer ||
      "Disclaimer: IP-SAKTI provides general information for educational purposes only. It is not legal advice.";
    const d = document.createElement("div");
    d.className = "answer-disclaimer";
    d.textContent = disclaimerText;
    div.appendChild(d);
  }

  function appendMsg(text, type, isFinal, meta) {
    const div = document.createElement("div");
    div.className = "msg bot";
    if (isFinal) div.classList.add("final-answer");
    if (!text) return div;

    const lines = text.split("\n");
    const ul = document.createElement("ul");
    ul.className = "answer-list";

    let firstRealBullet = true;
    for (const raw of lines) {
      const line = raw.trim();
      if (!line) continue;

      const cleaned = line.replace(/^[\-\*\u2022\u25E6\u2023]\s*/, "");
      if (!cleaned) continue;

      const li = document.createElement("li");
      li.textContent = cleaned;
      ul.appendChild(li);
      firstRealBullet = false;
    }

    if (ul.children.length === 0) {
      div.textContent = text;
    } else {
      div.appendChild(ul);
    }

    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return div;
  }

  function setInputEnabled(enabled) {
    chatInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    chatInput.placeholder = enabled
      ? "Ask about Ayurvedic IPR, drug regulations, GIs..."
      : "Waiting for response...";
  }

  async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Show user message
    appendUserMsg(query);

    chatInput.value = "";
    setInputEnabled(false);

    const loading = appendMsg("Thinking...", "bot loading", false);

    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query, jurisdiction: getJurisdiction() })
      });

      if (!res.ok) {
        chatBody.removeChild(loading);
        appendMsg("Server error: " + res.status + ". Please try again.", false);
        setInputEnabled(true);
        chatInput.focus();
        return;
      }

      const data = await res.json();

      chatBody.removeChild(loading);
      const answerDiv = appendMsg(data.answer, "bot", true, null);
      appendMeta(answerDiv, data);
    } catch (err) {
      chatBody.removeChild(loading);
      appendMsg("Sorry, I couldn't reach the server. Please try again.", false);
    }

    setInputEnabled(true);
    chatInput.focus();
  }

  let activeAudio = null; // tracks currently playing audio for stop feature

  // ---- Voice recording overlay + mic capture ----
  const voiceBtn = document.getElementById("voiceBtn");
  let mediaRecorder = null;
  let audioChunks = [];
  let voiceLang = "auto";

  function buildVoiceOverlay() {
    const overlay = document.createElement("div");
    overlay.id = "voiceOverlay";
    overlay.innerHTML = `
      <div id="voicePanel" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;border:2px solid #005cbb;border-radius:16px;padding:24px 32px;max-width:440px;width:92%;box-shadow:0 20px 50px rgba(0,0,0,0.3);z-index:10000;font-family:sans-serif;animation:fadeIn 0.2s ease;box-sizing:border-box;">
        <h3 style="margin:0 0 8px;color:#005cbb;font-size:18px;">🎤 Voice Input</h3>
        <p style="margin:0 0 14px;color:#555;font-size:13px;">Click Start to record. Pick a language or leave on Auto-detect.<br><span style="color:#888;">Mic needs <b>localhost/127.0.0.1</b> or HTTPS.</span></p>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
          <label for="recLang" style="font-size:13px;color:#333;font-weight:600;">Language:</label>
          <select id="recLang" style="flex:1;padding:6px 8px;border:1px solid #bbb;border-radius:6px;font-size:13px;">
            <option value="auto">Auto-detect</option>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="mr">Marathi</option>
            <option value="sa">Sanskrit</option>
            <option value="bn">Bengali</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
            <option value="kn">Kannada</option>
            <option value="gu">Gujarati</option>
          </select>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:14px;">
          <button id="recStart" style="flex:1;padding:10px;background:#e53935;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;">● Start</button>
          <button id="recStop" disabled style="flex:1;padding:10px;background:#2e7d32;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;opacity:0.5;">■ Stop &amp; Send</button>
          <button id="recClose" style="padding:10px 14px;background:#777;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px;">✕</button>
        </div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
          <div id="recDot" style="width:14px;height:14px;border-radius:50%;background:#9e9e9e;transition:background 0.2s;"></div>
          <span id="recStatus" style="font-size:13px;color:#777;font-weight:600;">Idle</span>
          <span id="recTimer" style="margin-left:auto;font-size:13px;color:#555;font-variant-numeric:tabular-nums;">0.0s</span>
        </div>
        <p id="recError" style="display:none;margin:10px 0 0;font-size:12px;color:#c62828;background:#ffebee;padding:8px;border-radius:6px;"></p>
      </div>
      <div id="voiceBackdrop" style="position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9999;backdrop-filter:blur(4px);"></div>
      <style>@keyframes pulse{0%{opacity:1;transform:scale(1);}50%{opacity:0.4;transform:scale(1.25);}100%{opacity:1;transform:scale(1);}}</style>
    `;
    return overlay;
  }

  // No manual language selection — model auto-detects

  async function startRecording(overlay) {
    const errEl = overlay.querySelector("#recError");
    const statusEl = overlay.querySelector("#recStatus");
    errEl.style.display = "none";
    audioChunks = [];

    // Pre-check: mic API requires a secure context (HTTPS or localhost/127.0.0.1)
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      statusEl.textContent = "Microphone unavailable";
      errEl.innerHTML =
        "Microphone access requires a secure context.<br>" +
        "Open the app at <b>http://127.0.0.1:5000</b> or <b>http://localhost:5000</b> " +
        "in your browser (or serve it over HTTPS), then try again.";
      errEl.style.display = "block";
      return false;
    }
    if (typeof window.isSecureContext !== "undefined" && !window.isSecureContext) {
      statusEl.textContent = "Microphone blocked (insecure page)";
      errEl.innerHTML =
        "Your browser blocks microphone access on this address because it is not a secure context.<br>" +
        "Open the app at <b>http://127.0.0.1:5000</b> or <b>http://localhost:5000</b> instead " +
        "of the network IP address, or serve it over HTTPS.";
      errEl.style.display = "block";
      return false;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : (MediaRecorder.isTypeSupported("audio/mp4") ? "audio/mp4" : "");
      mediaRecorder = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream);
      mediaRecorder.ondataavailable = function (e) { if (e.data && e.data.size > 0) audioChunks.push(e.data); };
      mediaRecorder.onstop = function () { stream.getTracks().forEach(function (t) { t.stop(); }); };
      mediaRecorder.start();
      return true;
    } catch (err) {
      statusEl.textContent = "Microphone access denied";
      let hint = "";
      if (err && err.name === "NotAllowedError") {
        hint = "Click the microphone/lock icon in your browser's address bar, allow microphone access, then try again. " +
               "Also make sure you opened the page via <b>http://127.0.0.1:5000</b> or <b>http://localhost:5000</b> — " +
               "browsers block the mic on network-IP HTTP addresses.";
      } else if (err && err.name === "NotFoundError") {
        hint = "No microphone was found on this device. Connect a microphone and try again.";
      } else if (err && err.name === "NotReadableError") {
        hint = "Your microphone is in use by another application. Close it and try again.";
      }
      errEl.innerHTML = "Microphone error: " + (err && err.message ? err.message : err) +
        (hint ? "<br><br>" + hint : "");
      errEl.style.display = "block";
      return false;
    }
  }

  // Encode an AudioBuffer as 16-bit PCM WAV at 16 kHz mono.
  // Whisper/Sarvam models are trained on 16 kHz mono audio, so this
  // shrinks payloads ~4x (faster upload + faster STT) with no accuracy
  // loss versus sending 44.1/48 kHz stereo.
  const STT_SAMPLE_RATE = 16000;

  function encodeWav(audioBuffer) {
    // Mix down to mono
    const numFrames = audioBuffer.length;
    const inRate = audioBuffer.sampleRate;
    const channels = [];
    for (let c = 0; c < audioBuffer.numberOfChannels; c++) channels.push(audioBuffer.getChannelData(c));

    // Simple linear resample to 16 kHz
    const ratio = inRate / STT_SAMPLE_RATE;
    const outFrames = Math.max(1, Math.floor(numFrames / ratio));
    const mono = new Float32Array(outFrames);
    for (let i = 0; i < outFrames; i++) {
      const srcPos = i * ratio;
      const i0 = Math.floor(srcPos);
      const i1 = Math.min(i0 + 1, numFrames - 1);
      const frac = srcPos - i0;
      let sample = 0;
      for (let c = 0; c < channels.length; c++) {
        sample += channels[c][i0] * (1 - frac) + channels[c][i1] * frac;
      }
      mono[i] = sample / channels.length;
    }

    const bytesPerSample = 2;
    const dataSize = outFrames * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    function writeStr(offset, str) {
      for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    }

    writeStr(0, "RIFF");
    view.setUint32(4, 36 + dataSize, true);
    writeStr(8, "WAVE");
    writeStr(12, "fmt ");
    view.setUint32(16, 16, true);          // fmt chunk size
    view.setUint16(20, 1, true);           // PCM
    view.setUint16(22, 1, true);           // mono
    view.setUint32(24, STT_SAMPLE_RATE, true);
    view.setUint32(28, STT_SAMPLE_RATE * 2, true); // byte rate
    view.setUint16(32, 2, true);           // block align
    view.setUint16(34, 16, true);          // bits per sample
    writeStr(36, "data");
    view.setUint32(40, dataSize, true);

    let offset = 44;
    for (let i = 0; i < outFrames; i++) {
      const s = Math.max(-1, Math.min(1, mono[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      offset += 2;
    }
    return new Blob([buffer], { type: "audio/wav" });
  }

  async function recordingToWavBlob() {
    const raw = new Blob(audioChunks, { type: "audio/webm" });
    const arrayBuf = await raw.arrayBuffer();
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const decoded = await audioCtx.decodeAudioData(arrayBuf.slice(0));
    if (audioCtx.close) audioCtx.close();
    return encodeWav(decoded);
  }

  async function stopAndSend(overlay) {
    if (!mediaRecorder || mediaRecorder.state === "inactive") return;
    mediaRecorder.stop();
    // Wait a tick for the final dataavailable
    await new Promise(function (r) { setTimeout(r, 150); });

    const status = overlay.querySelector("#recStatus");
    const start = overlay.querySelector("#recStart");
    const stop = overlay.querySelector("#recStop");
    status.textContent = "Encoding audio...";
    start.disabled = true;
    stop.disabled = true;

    let base64;
    try {
      const wavBlob = await recordingToWavBlob();
      base64 = await blobToBase64(wavBlob);
    } catch (e) {
      status.textContent = "Encoding failed";
      const errEl = overlay.querySelector("#recError");
      errEl.textContent = "Could not encode the recording: " + e.message;
      errEl.style.display = "block";
      return;
    }

    status.textContent = "Transcribing & querying...";

    try {
      const langSelect = overlay.querySelector("#recLang");
      if (langSelect) voiceLang = langSelect.value;
      const res = await fetch("/query-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inputLanguage: voiceLang,
          outputLanguage: voiceLang,
          jurisdiction: getJurisdiction(),
          audioBase64: base64
        })
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        status.textContent = "Error: " + (data.error || res.status);
        return;
      }
      // Show user transcription
      if (data.user_text) {
        appendUserMsg(data.user_text);
      }
      // Show bot answer + stop button
      const msgDiv = appendMsg(data.answer || "No answer.", "bot", true, null);
      appendMeta(msgDiv, data);
      if (data.audio_base64) {
        const stopBtn = document.createElement("button");
        stopBtn.textContent = "⏹ Stop Speech";
        stopBtn.style.cssText = "margin-top:8px;padding:6px 14px;border:none;border-radius:6px;background:#c62828;color:#fff;font-size:13px;font-weight:600;cursor:pointer;";
        stopBtn.onclick = function () {
          if (activeAudio) { try { activeAudio.pause(); activeAudio.currentTime = 0; } catch (e) {} activeAudio = null; }
          stopBtn.textContent = "⏹ Stopped";
          stopBtn.style.opacity = "0.7";
          stopBtn.style.cursor = "default";
          stopBtn.disabled = true;
        };
        msgDiv.appendChild(stopBtn);
      }
      // Play audio reply if present
      if (data.audio_base64) {
        if (activeAudio) { try { activeAudio.pause(); } catch(e){} }
        activeAudio = new Audio("data:audio/mp3;base64," + data.audio_base64);
        activeAudio.play().catch(function () { /* autoplay blocked - ignore */ });
      }
      status.textContent = "Done";
      setTimeout(function () { const el = document.getElementById("voiceOverlay"); if (el) el.remove(); }, 600);
    } catch (err) {
      status.textContent = "Network error";
      const errEl = overlay.querySelector("#recError");
      errEl.textContent = "Could not reach /query-voice: " + err.message;
      errEl.style.display = "block";
    }
  }

  function blobToBase64(blob) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onloadend = function () { resolve(String(reader.result).split(",")[1]); };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  if (voiceBtn) {
    voiceBtn.addEventListener("click", function () {
      // Remove any existing overlay
      const existing = document.getElementById("voiceOverlay");
      if (existing) { existing.remove(); return; }

      const overlay = buildVoiceOverlay();
      document.body.appendChild(overlay);

      const dot = overlay.querySelector("#recDot");
      const status = overlay.querySelector("#recStatus");
      const timer = overlay.querySelector("#recTimer");
      const start = overlay.querySelector("#recStart");
      const stop = overlay.querySelector("#recStop");
      const close = overlay.querySelector("#recClose");
      const backdrop = overlay.querySelector("#voiceBackdrop");

      let timerInterval = null;
      let seconds = 0;

      function tickTimer() {
        seconds += 0.1;
        timer.textContent = seconds.toFixed(1) + "s";
      }

      start.addEventListener("click", async function () {
        const ok = await startRecording(overlay);
        if (!ok) return;
        dot.style.background = "#e53935";
        dot.style.animation = "pulse 1s infinite";
        status.textContent = "Recording...";
        status.style.color = "#c62828";
        start.disabled = true; start.style.opacity = "0.5";
        stop.disabled = false; stop.style.opacity = "1";
        seconds = 0; timer.textContent = "0.0s";
        timerInterval = setInterval(tickTimer, 100);
      });

      stop.addEventListener("click", function () {
        if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
        dot.style.background = "#1976d2";
        dot.style.animation = "none";
        status.textContent = "Processing...";
        stopAndSend(overlay);
      });

      function dismiss() { overlay.remove(); if (timerInterval) clearInterval(timerInterval); if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop(); }
      close.addEventListener("click", dismiss);
      backdrop.addEventListener("click", dismiss);
    });
  }

  sendBtn.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
  });

  // Show a welcome message when chat opens for the first time
  let welcomeShown = false;
  function showWelcome() {
    if (welcomeShown) return;
    welcomeShown = true;
    appendMsg(
      "Namaste! Welcome to IP-SAKTI Ayurveda IPR Assistant. I can help you with questions about:\n\n" +
      "  \u2022 Ayurvedic herbs & pharmacology\n" +
      "  \u2022 Patent rules for Ayurvedic products\n" +
      "  \u2022 Drug regulations (Drugs & Cosmetics Act)\n" +
      "  \u2022 Geographical Indications (GI)\n" +
      "  \u2022 Access & Benefit Sharing compliance\n" +
      "  \u2022 Case law (Turmeric, Neem, Basmati)\n\n" +
      "Use the Jurisdiction selector to filter answers, or try the Formulation Classifier and ABS Checklist tools above.",
      "bot", false, null
    );
    const note = document.createElement("div");
    note.className = "msg bot final-answer";
    note.textContent = "Note: IP-SAKTI gives information, not legal advice. Always consult a qualified IP attorney for legal decisions.";
    chatBody.appendChild(note);
  }

  chatToggle.addEventListener("click", showWelcome, { once: true });

  // ============================================================
  // Wizards: Formulation Classifier + ABS Checklist
  // ============================================================

  function openWizardPanel(title, subtitle) {
    const backdrop = document.createElement("div");
    backdrop.className = "wizard-backdrop";
    const panel = document.createElement("div");
    panel.className = "wizard-panel";
    panel.innerHTML = "<h3></h3><p class='wizard-sub'></p>";
    panel.querySelector("h3").textContent = title;
    panel.querySelector(".wizard-sub").textContent = subtitle;
    backdrop.appendChild(panel);
    backdrop.addEventListener("click", function (e) {
      if (e.target === backdrop) backdrop.remove();
    });
    document.body.appendChild(backdrop);
    document.addEventListener("keydown", function esc(e) {
      if (e.key === "Escape") { backdrop.remove(); document.removeEventListener("keydown", esc); }
    });
    return { backdrop: backdrop, panel: panel };
  }

  // ---- Formulation Classifier Wizard ----
  const formulationWizardBtn = document.getElementById("formulationWizardBtn");
  if (formulationWizardBtn) {
    formulationWizardBtn.addEventListener("click", async function () {
      const wiz = openWizardPanel("Formulation Classifier", "Classify your Ayurvedic product: Classical / PAM (New Drug) / Phytopharmaceutical / Food Supplement / Cosmetic.");
      const panel = wiz.panel;
      const answers = {};

      async function fetchSteps() {
        try {
          const res = await fetch("/formulation/questions");
          const data = await res.json();
          return data.steps || [];
        } catch (e) {
          return [];
        }
      }

      const steps = await fetchSteps();
      const useSteps = steps.length ? steps : [];
      if (!useSteps.length) {
        panel.innerHTML += "<p>Could not load wizard questions. Is the server running?</p>";
        return;
      }

      function renderStep(i) {
        const step = useSteps[i];
        panel.querySelectorAll(".wizard-question, .wizard-options, .wizard-progress").forEach(function (el) { el.remove(); });

        const prog = document.createElement("div");
        prog.className = "wizard-progress";
        prog.textContent = "Step " + (i + 1) + " of " + useSteps.length;
        panel.appendChild(prog);

        const q = document.createElement("div");
        q.className = "wizard-question";
        q.textContent = step.question;
        panel.appendChild(q);

        const opts = document.createElement("div");
        opts.className = "wizard-options";
        step.options.forEach(function (opt) {
          const btn = document.createElement("button");
          btn.textContent = opt.label;
          btn.onclick = async function () {
            answers[step.id] = opt.value;
            if (i + 1 < useSteps.length) {
              renderStep(i + 1);
            } else {
              await submitClassification();
            }
          };
          opts.appendChild(btn);
        });
        panel.appendChild(opts);
      }

      async function submitClassification() {
        panel.querySelectorAll(".wizard-question, .wizard-options, .wizard-progress").forEach(function (el) { el.remove(); });
        const loadingEl = document.createElement("p");
        loadingEl.textContent = "Classifying...";
        panel.appendChild(loadingEl);
        try {
          const res = await fetch("/formulation/classify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answers: answers })
          });
          const data = await res.json();
          loadingEl.remove();
          if (data.error) {
            panel.innerHTML += "<p class='wizard-result'>Error: " + data.error + "</p>";
            return;
          }
          const result = document.createElement("div");
          result.className = "wizard-result";
          result.innerHTML = "<h4></h4>";
          result.querySelector("h4").textContent = data.label;
          const rows = [
            ["What it is", data.description],
            ["Regulatory requirements", data.regulatory],
            ["IP protection", data.ip_note],
            ["ABS check", data.abs_check]
          ];
          if (data.note) rows.push(["Important", data.note]);
          rows.forEach(function (r) {
            const p = document.createElement("p");
            p.innerHTML = "<strong>" + r[0] + ":</strong> ";
            p.appendChild(document.createTextNode(r[1]));
            result.appendChild(p);
          });
          const disc = document.createElement("p");
          disc.className = "wiz-note";
          disc.textContent = data.disclaimer || "";
          result.appendChild(disc);
          panel.appendChild(result);

          const actions = document.createElement("div");
          actions.className = "wizard-actions";
          const closeBtn = document.createElement("button");
          closeBtn.className = "secondary";
          closeBtn.textContent = "Close";
          closeBtn.onclick = function () { wiz.backdrop.remove(); };
          const againBtn = document.createElement("button");
          againBtn.className = "primary";
          againBtn.textContent = "Start over";
          againBtn.onclick = function () { wiz.backdrop.remove(); formulationWizardBtn.click(); };
          actions.appendChild(closeBtn);
          actions.appendChild(againBtn);
          panel.appendChild(actions);
        } catch (e) {
          loadingEl.textContent = "Could not reach the server: " + e.message;
        }
      }

      renderStep(0);
    });
  }

  // ---- Escalate to Human panel ----
  const escalateBtn = document.getElementById("escalateBtn");
  if (escalateBtn) {
    escalateBtn.addEventListener("click", async function () {
      const wiz = openWizardPanel("Escalate to a Human IP Facilitator", "IP-SAKTI provides information, not legal advice. For these matters, contact a qualified professional.");
      const panel = wiz.panel;
      try {
        const res = await fetch("/escalation");
        const data = await res.json();
        const result = document.createElement("div");
        result.className = "wizard-result";
        const when = document.createElement("p");
        when.innerHTML = "<strong>Escalate for:</strong> " + (data.when_to_escalate || []).join(", ");
        result.appendChild(when);
        const ul = document.createElement("ul");
        (data.contacts || []).forEach(function (c) {
          const li = document.createElement("li");
          const a = document.createElement("a");
          a.href = c.url;
          a.target = "_blank";
          a.rel = "noopener";
          a.textContent = c.name;
          li.appendChild(a);
          if (c.detail) {
            li.appendChild(document.createTextNode(" — " + c.detail));
          }
          ul.appendChild(li);
        });
        result.appendChild(ul);
        const disc = document.createElement("p");
        disc.className = "wiz-note";
        disc.textContent = data.disclaimer || "";
        result.appendChild(disc);
        panel.appendChild(result);
        const actions = document.createElement("div");
        actions.className = "wizard-actions";
        const closeBtn = document.createElement("button");
        closeBtn.className = "secondary";
        closeBtn.textContent = "Close";
        closeBtn.onclick = function () { wiz.backdrop.remove(); };
        actions.appendChild(closeBtn);
        panel.appendChild(actions);
      } catch (e) {
        panel.innerHTML += "<p>Could not load escalation contacts. Is the server running?</p>";
      }
    });
  }

  // ---- ABS Checklist Wizard ----
  const absWizardBtn = document.getElementById("absWizardBtn");
  if (absWizardBtn) {
    absWizardBtn.addEventListener("click", async function () {
      const wiz = openWizardPanel("ABS Compliance Checklist", "Access & Benefit Sharing under the Biological Diversity Act: PIC → MAT → NBA approval.");
      const panel = wiz.panel;

      let steps = [];
      try {
        const res = await fetch("/abs/checklist");
        const data = await res.json();
        steps = data.steps || [];
      } catch (e) {
        panel.innerHTML += "<p>Could not load checklist. Is the server running?</p>";
        return;
      }
      if (!steps.length) return;

      const completed = new Set();

      const intro = document.createElement("div");
      intro.innerHTML =
        "<label style='display:block;margin:6px 0;font-size:14px;'><input type='checkbox' id='absForeign' style='width:auto;margin-right:8px;'> I am a foreign entity / transferring resources abroad (NBA approval mandatory)</label>" +
        "<label style='display:block;margin:6px 0 12px;font-size:14px;'><input type='checkbox' id='absExport' style='width:auto;margin-right:8px;'> I plan to export biological resources or products</label>" +
        "<div class='abs-progress-bar'><div id='absProgressBar' style='width:0%'></div></div>";
      panel.appendChild(intro);

      const list = document.createElement("div");
      panel.appendChild(list);

      function renderList() {
        list.innerHTML = "";
        let lastPhase = null;
        steps.forEach(function (step) {
          if (step.phase !== lastPhase) {
            const ph = document.createElement("div");
            ph.className = "abs-phase";
            ph.textContent = step.phase;
            list.appendChild(ph);
            lastPhase = step.phase;
          }
          const item = document.createElement("label");
          item.className = "abs-item";
          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.checked = completed.has(step.id);
          cb.onchange = function () {
            if (cb.checked) completed.add(step.id); else completed.delete(step.id);
            updateProgress();
          };
          const span = document.createElement("span");
          span.textContent = step.item;
          const auth = document.createElement("span");
          auth.className = "abs-authority";
          auth.textContent = "Authority: " + step.authority;
          item.appendChild(cb);
          item.appendChild(span);
          item.appendChild(auth);
          list.appendChild(item);
        });
      }

      function updateProgress() {
        const pctEl = panel.querySelector("#absProgressBar");
        if (pctEl) {
          pctEl.style.width = Math.round(100 * completed.size / steps.length) + "%";
        }
      }

      renderList();

      const actions = document.createElement("div");
      actions.className = "wizard-actions";

      const checkBtn = document.createElement("button");
      checkBtn.className = "primary";
      checkBtn.textContent = "Check compliance";
      checkBtn.onclick = async function () {
        try {
          const res = await fetch("/abs/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              completed: Array.from(completed),
              foreign_entity: panel.querySelector("#absForeign").checked,
              exports: panel.querySelector("#absExport").checked
            })
          });
          const data = await res.json();
          panel.querySelectorAll(".wizard-result").forEach(function (el) { el.remove(); });
          const result = document.createElement("div");
          result.className = "wizard-result";
          const h = document.createElement("h4");
          h.textContent = data.compliant
            ? "✓ ABS compliance steps complete"
            : "⚠ " + (data.missing_required ? data.missing_required.length : 0) + " required step(s) remaining";
          result.appendChild(h);
          const p = document.createElement("p");
          p.textContent = "Completion: " + (data.percent_complete || 0) + "%";
          result.appendChild(p);
          if (data.missing_required && data.missing_required.length) {
            const ul = document.createElement("ul");
            data.missing_required.forEach(function (m) {
              const li = document.createElement("li");
              li.textContent = m.phase + " — " + m.item;
              ul.appendChild(li);
            });
            result.appendChild(ul);
          }
          const tkdl = document.createElement("p");
          tkdl.className = "wiz-note";
          tkdl.textContent = data.disclaimer || "";
          result.appendChild(tkdl);
          panel.insertBefore(result, actions);
        } catch (e) {
          alert("Could not reach server: " + e.message);
        }
      };

      const closeBtn = document.createElement("button");
      closeBtn.className = "secondary";
      closeBtn.textContent = "Close";
      closeBtn.onclick = function () { wiz.backdrop.remove(); };

      actions.appendChild(closeBtn);
      actions.appendChild(checkBtn);
      panel.appendChild(actions);
    });
  }
})();
