(function() {
  // Helper: get data attributes
  function getConfig() {
    const script = document.currentScript || (function() {
      const scripts = document.getElementsByTagName('script');
      return scripts[scripts.length - 1];
    })();
    return {
      campaignId: script.getAttribute('data-campaign'),
      offerId: script.getAttribute('data-offer'),
      style: script.getAttribute('data-style') || 'button',
              container: script.getAttribute('data-container') || 'hissaback-widget'
    };
  }

  // Helper: create element
  function el(tag, attrs, ...children) {
    const e = document.createElement(tag);
    if (attrs) for (let k in attrs) e[k] = attrs[k];
    for (let c of children) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    return e;
  }

  // Main widget logic
  async function renderWidget() {
    const cfg = getConfig();
    const container = document.getElementById(cfg.container);
    if (!container) return;
    // Fetch offer/campaign details
    let offer, campaign, link;
    try {
      const [offers, campaigns] = await Promise.all([
        fetch('/v1/offers').then(r => r.json()),
        fetch('/v1/campaigns').then(r => r.json())
      ]);
      offer = offers.find(o => o.offer_id == cfg.offerId);
      campaign = campaigns.campaigns.find(c => c.campaign_id == cfg.campaignId);
      // Find or create link
      let links = await fetch('/v1/links').then(r => r.json());
      link = links.links.find(l => l.campaign_id == cfg.campaignId && l.offer_id == offer.offer_id);
      if (!link) {
        // Create smart link
        const resp = await fetch('/v1/links', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ campaign_id: cfg.campaignId, offer_id: offer.offer_id })
        });
        link = await resp.json();
      }
    } catch (e) {
      container.textContent = 'Error loading cashback offer.';
      return;
    }
    // Render UI
    container.innerHTML = '';
            const btn = el('button', { className: 'hissaback-btn', style: 'padding:10px 20px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:1rem;' },
      `Get ₹${Math.round(offer.base_commission_pct * (campaign.share_pct / 100))} cashback on ${offer.brand}`
    );
    container.appendChild(btn);
    // Modal for phone/OTP
    const modal = el('div', { style: 'display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.4);z-index:9999;align-items:center;justify-content:center;' });
    const modalBox = el('div', { style: 'background:#fff;padding:2em 2em 1em 2em;border-radius:10px;max-width:350px;text-align:center;box-shadow:0 2px 16px #0002;' });
    const phoneInput = el('input', { type: 'tel', placeholder: 'Enter phone', style: 'width:90%;padding:8px;margin:10px 0;' });
    const sendOtpBtn = el('button', { style: 'padding:8px 16px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;margin-bottom:10px;' }, 'Send OTP');
    const otpInput = el('input', { type: 'text', placeholder: 'Enter OTP', style: 'width:90%;padding:8px;margin:10px 0;display:none;' });
    const verifyOtpBtn = el('button', { style: 'padding:8px 16px;background:#059669;color:#fff;border:none;border-radius:6px;cursor:pointer;display:none;' }, 'Verify OTP');
    const closeBtn = el('button', { style: 'position:absolute;top:10px;right:20px;background:none;border:none;font-size:1.5em;cursor:pointer;' }, '×');
    modalBox.appendChild(closeBtn);
    modalBox.appendChild(el('div', { style: 'font-weight:bold;font-size:1.1em;margin-bottom:10px;' }, `Claim your cashback on ${offer.brand}`));
    modalBox.appendChild(phoneInput);
    modalBox.appendChild(sendOtpBtn);
    modalBox.appendChild(otpInput);
    modalBox.appendChild(verifyOtpBtn);
    modal.appendChild(modalBox);
    document.body.appendChild(modal);
    // Button click: open modal
    btn.onclick = () => { modal.style.display = 'flex'; };
    closeBtn.onclick = () => { modal.style.display = 'none'; };
    // Send OTP
    sendOtpBtn.onclick = async () => {
      if (!phoneInput.value.match(/^\d{10,}$/)) { alert('Enter valid phone'); return; }
      sendOtpBtn.disabled = true;
      try {
        const resp = await fetch('/v1/auth/enduser/otp/request', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: phoneInput.value, link_id: link.link_id })
        });
        const data = await resp.json();
        if (resp.ok) {
          otpInput.style.display = 'block';
          verifyOtpBtn.style.display = 'inline-block';
          sendOtpBtn.style.display = 'none';
          phoneInput.disabled = true;
          verifyOtpBtn.dataset.requestId = data.request_id;
        } else {
          alert(data.detail || 'Failed to send OTP');
        }
      } finally { sendOtpBtn.disabled = false; }
    };
    // Verify OTP
    verifyOtpBtn.onclick = async () => {
      if (!otpInput.value.match(/^\d{6}$/)) { alert('Enter 6-digit OTP'); return; }
      verifyOtpBtn.disabled = true;
      try {
        const resp = await fetch('/v1/auth/enduser/otp/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request_id: verifyOtpBtn.dataset.requestId, code: otpInput.value, link_id: link.link_id })
        });
        const data = await resp.json();
        if (resp.ok && data.verified) {
          // Track click
          await fetch('/v1/events/click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link_id: link.link_id, user_id: phoneInput.value })
          });
          modalBox.innerHTML = `<div style='font-size:1.2em;margin:1em 0;'>Success! Redirecting...</div>`;
          setTimeout(() => { window.location.href = data.merchant_url; }, 1200);
        } else {
          alert(data.detail || 'Invalid OTP');
        }
      } finally { verifyOtpBtn.disabled = false; }
    };
  }

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderWidget);
  } else {
    renderWidget();
  }
})(); 