/**
 * Tifinify Core Frontend Script
 * Handles Google Maps JS API, Leaflet Fallback Engine, Places Autocomplete,
 * Geolocation Auto-Fix, Review Trust Charts, and Live Google Places Sync.
 */

document.addEventListener("DOMContentLoaded", () => {
  initThemeUI();
  checkAutoLocateOnLoad();
  initGeolocationButtons();
  initFavoriteToggles();
  initPlacesAutocompleteOnLoad();
  initGoogleSyncModal();
  initGeminiDiscoveryUI();
});

/**
 * Auto-detect GPS coordinates if query says "Current Location" but coordinates are missing
 */
function checkAutoLocateOnLoad() {
  const urlParams = new URLSearchParams(window.location.search);
  const loc = urlParams.get("location") || "";
  const lat = urlParams.get("lat");
  const lng = urlParams.get("lng");

  if (loc.toLowerCase().includes("current") && (!lat || !lng || lat.trim() === "" || lng.trim() === "")) {
    const cachedLat = sessionStorage.getItem("user_lat");
    const cachedLng = sessionStorage.getItem("user_lng");

    if (cachedLat && cachedLng) {
      urlParams.set("lat", cachedLat);
      urlParams.set("lng", cachedLng);
      window.location.replace(`${window.location.pathname}?${urlParams.toString()}`);
      return;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const uLat = pos.coords.latitude;
          const uLng = pos.coords.longitude;
          sessionStorage.setItem("user_lat", uLat);
          sessionStorage.setItem("user_lng", uLng);
          urlParams.set("lat", uLat);
          urlParams.set("lng", uLng);
          window.location.replace(`${window.location.pathname}?${urlParams.toString()}`);
        },
        async (err) => {
          console.warn("Auto-geolocation skipped:", err.message);
          try {
            const res = await fetch("/api/v1/geo/ip-locate");
            const data = await res.json();
            if (data && data.latitude && data.longitude) {
              urlParams.set("lat", data.latitude);
              urlParams.set("lng", data.longitude);
              window.location.replace(`${window.location.pathname}?${urlParams.toString()}`);
            }
          } catch (e) {}
        },
        { timeout: 2500, enableHighAccuracy: false }
      );
    }
  }
}

/**
 * Handle "Use Current Location" button clicks with browser GPS + automatic IP fallback.
 * Defined globally on window so inline onclick handlers and event listeners both work seamlessly.
 */
window.fetchAndApplyCurrentLocation = async function (btn) {
  if (!btn) btn = document.querySelector(".btn-use-location");

  // Find associated form and inputs
  const form = btn ? btn.closest("form") : document.getElementById("filterForm");
  const locInput =
    (form ? form.querySelector('input[name="location"]') : null) ||
    document.getElementById("filterLocation") ||
    document.getElementById("homeLocation") ||
    document.querySelector('input[name="location"]');
  const latInput =
    (form ? form.querySelector('input[name="lat"]') : null) ||
    document.getElementById("hiddenLat") ||
    document.getElementById("homeLat");
  const lngInput =
    (form ? form.querySelector('input[name="lng"]') : null) ||
    document.getElementById("hiddenLng") ||
    document.getElementById("homeLng");

  // Visual feedback: Spin button icon & update placeholder
  const originalHtml = btn ? btn.innerHTML : '<i class="bi bi-crosshair"></i>';
  if (btn) {
    btn.innerHTML = '<span class="spinner-border spinner-border-sm text-success" role="status" aria-hidden="true"></span>';
    btn.disabled = true;
  }
  if (locInput) {
    locInput.dataset.previousValue = locInput.value;
    locInput.placeholder = "Detecting your location...";
  }

  let isDone = false;

  const applyAndNavigate = (lat, lng, label) => {
    if (isDone) return;
    isDone = true;

    sessionStorage.setItem("user_lat", lat);
    sessionStorage.setItem("user_lng", lng);
    sessionStorage.setItem("user_location", label || "Current Location");

    if (locInput) {
      locInput.value = label || "Current Location";
      locInput.placeholder = "Area or locality";
    }
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;

    // Navigate to discovery page with resolved coordinates
    const targetUrl = `/providers/discovery?lat=${lat}&lng=${lng}&location=${encodeURIComponent(label || "Current Location")}`;
    window.location.href = targetUrl;
  };

  // 1. Kick off IP geolocation immediately in parallel (typically completes in 200-300ms)
  const ipFetchPromise = fetch("/api/v1/geo/ip-locate")
    .then((r) => r.json())
    .catch((err) => {
      console.warn("IP geolocation fetch error:", err);
      return null;
    });

  // 2. Try browser GPS with low accuracy (fast network triangulation) and 2000ms max timeout
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const uLat = pos.coords.latitude;
        const uLng = pos.coords.longitude;
        applyAndNavigate(uLat, uLng, "Current Location (GPS)");
      },
      async (err) => {
        console.warn("Browser GPS unavailable/declined (" + err.message + "). Using network IP fallback...");
        const ipData = await ipFetchPromise;
        if (ipData && ipData.latitude && ipData.longitude) {
          const locName = ipData.city ? `Current Location (${ipData.city})` : "Current Location";
          applyAndNavigate(ipData.latitude, ipData.longitude, locName);
        } else {
          // Default fallback
          applyAndNavigate(23.1815, 79.9864, "Current Location (Jabalpur)");
        }
      },
      { timeout: 2000, enableHighAccuracy: false, maximumAge: 60000 }
    );
  } else {
    // No browser geolocation support - await IP fetch directly
    const ipData = await ipFetchPromise;
    if (ipData && ipData.latitude && ipData.longitude) {
      const locName = ipData.city ? `Current Location (${ipData.city})` : "Current Location";
      applyAndNavigate(ipData.latitude, ipData.longitude, locName);
    } else {
      applyAndNavigate(23.1815, 79.9864, "Current Location (Jabalpur)");
    }
  }

  // Safety timer: If after 2.5 seconds neither GPS nor IP callback resolved, complete using IP promise
  setTimeout(async () => {
    if (isDone) return;
    const ipData = await ipFetchPromise;
    if (ipData && ipData.latitude && ipData.longitude) {
      const locName = ipData.city ? `Current Location (${ipData.city})` : "Current Location";
      applyAndNavigate(ipData.latitude, ipData.longitude, locName);
    } else {
      applyAndNavigate(23.1815, 79.9864, "Current Location (Jabalpur)");
    }
  }, 2500);
};

function initGeolocationButtons() {
  const geoBtns = document.querySelectorAll(".btn-use-location");
  geoBtns.forEach((btn) => {
    btn.onclick = (e) => {
      e.preventDefault();
      window.fetchAndApplyCurrentLocation(btn);
    };
  });
}

/**
 * Toggle favorite bookmark via AJAX
 */
function initFavoriteToggles() {
  const favBtns = document.querySelectorAll(".favorite-toggle-btn");
  favBtns.forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const providerId = btn.getAttribute("data-provider-id");
      if (!providerId) return;

      try {
        const res = await fetch(`/api/v1/favorites/${providerId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        if (res.status === 401) {
          window.location.href = "/auth/login";
          return;
        }

        const data = await res.json();
        if (data.status === "success") {
          if (data.is_favorite) {
            btn.classList.add("active");
            btn.innerHTML = '<i class="bi bi-heart-fill"></i>';
          } else {
            btn.classList.remove("active");
            btn.innerHTML = '<i class="bi bi-heart"></i>';
          }
        }
      } catch (err) {
        console.error("Failed to toggle favorite:", err);
      }
    });
  });
}

/**
 * Initialize sentiment chart with Chart.js
 */
function renderSentimentChart(canvasId, positivePct, neutralPct, negativePct) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || typeof Chart === "undefined") return;

  const isDark = document.documentElement.getAttribute("data-bs-theme") === "dark";
  const textColor = isDark ? "#cbd5e1" : "#475569";
  const borderColor = isDark ? "#131b2e" : "#ffffff";

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          data: [positivePct, neutralPct, negativePct],
          backgroundColor: ["#10B981", "#94A3B8", "#EF4444"],
          borderWidth: 2,
          borderColor: borderColor,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            boxWidth: 12,
            padding: 15,
            color: textColor,
            font: { size: 12, weight: 600 },
          },
        },
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.label}: ${item.raw}%`,
          },
        },
      },
      cutout: "68%",
    },
  });
}

/**
 * Google Places Autocomplete on search input
 */
function initPlacesAutocompleteOnLoad() {
  const setup = () => {
    const input = document.getElementById("filterLocation");
    if (!input || !window.google || !window.google.maps || !google.maps.places) return;

    try {
      const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ["geocode", "establishment"],
        componentRestrictions: { country: "in" },
      });

      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) return;

        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();

        const hiddenLat = document.getElementById("hiddenLat");
        const hiddenLng = document.getElementById("hiddenLng");
        if (hiddenLat) hiddenLat.value = lat;
        if (hiddenLng) hiddenLng.value = lng;

        const form = input.closest("form");
        if (form) form.submit();
      });
    } catch (e) {
      console.warn("Places autocomplete init note:", e);
    }
  };

  if (window.google && window.google.maps && google.maps.places) {
    setup();
  } else {
    window.addEventListener("google-maps-ready", setup);
  }
}

/**
 * Initialize OpenMap (Leaflet + OpenStreetMap) for Discovery or Single Provider views.
 * 100% free, zero billing, zero API keys required.
 */
function initOpenMap(containerId, centerLat, centerLng, providers, options = {}) {
  const mapContainer = document.getElementById(containerId);
  if (!mapContainer) return;

  // If Leaflet script is still initializing, retry automatically
  if (typeof L === "undefined") {
    console.warn("Leaflet library not ready yet; queuing initOpenMap for:", containerId);
    setTimeout(() => {
      initOpenMap(containerId, centerLat, centerLng, providers, options);
    }, 150);
    return;
  }

  // Ensure local images directory path for Leaflet icons
  if (L.Icon && L.Icon.Default) {
    L.Icon.Default.imagePath = "/static/vendor/leaflet/images/";
  }

  // Clean existing Leaflet instance if already attached
  if (mapContainer._leaflet_id) {
    mapContainer._leaflet_id = null;
  }
  mapContainer.innerHTML = "";

  const cLat = Number(centerLat) || 28.6139;
  const cLng = Number(centerLng) || 77.2090;
  const initialZoom = options.zoom || 13;

  const map = L.map(containerId, {
    scrollWheelZoom: false,
  }).setView([cLat, cLng], initialZoom);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© <a href='https://openstreetmap.org' target='_blank'>OpenStreetMap</a> contributors | Tifinify",
  }).addTo(map);

  // Search Center Pulse Marker
  const centerIcon = L.divIcon({
    className: "custom-map-center-pin",
    html: `<div style="width: 24px; height: 24px; border-radius: 50%; background: #2563EB; border: 3px solid #FFFFFF; box-shadow: 0 0 12px rgba(37,99,235,0.7); display: flex; align-items: center; justify-content: center; color: white; font-size: 11px;">📍</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  L.marker([cLat, cLng], { icon: centerIcon })
    .addTo(map)
    .bindPopup("<b>📍 Search Center</b><br>Your selected search location.");

  // Support single provider object or list of providers
  let providerList = [];
  if (Array.isArray(providers)) {
    providerList = providers;
  } else if (providers && typeof providers === "object") {
    providerList = [providers];
  }

  const bounds = L.latLngBounds([[cLat, cLng]]);

  providerList.forEach((p) => {
    if (!p.latitude || !p.longitude) return;

    const pLat = Number(p.latitude);
    const pLng = Number(p.longitude);
    bounds.extend([pLat, pLng]);

    const trustScore = p.review_trust_score || 80;
    const pinColor = trustScore >= 80 ? "#10B981" : trustScore >= 50 ? "#F59E0B" : "#EF4444";
    const trustBadgeClass = trustScore >= 80 ? "text-success" : trustScore >= 50 ? "text-warning" : "text-danger";

    // Custom SVG Pin Icon
    const customPin = L.divIcon({
      className: "custom-tifinify-pin",
      html: `
        <svg width="28" height="36" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); cursor: pointer;">
          <path d="M12 0C5.37 0 0 5.37 0 12c0 9 12 20 12 20s12-11 12-20c0-6.63-5.37-12-12-12z" fill="${pinColor}"/>
          <circle cx="12" cy="11" r="5" fill="#FFFFFF"/>
          <text x="12" y="14" font-size="7" font-weight="bold" fill="${pinColor}" text-anchor="middle">🍲</text>
        </svg>
      `,
      iconSize: [28, 36],
      iconAnchor: [14, 36],
      popupAnchor: [0, -32],
    });

    const popupHtml = `
      <div style="min-width: 190px; padding: 4px; font-family: system-ui, -apple-system, sans-serif;">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #059669; margin-bottom: 2px;">
          ${p.category ? p.category.toUpperCase() : "TIFFIN SERVICE"}
        </div>
        <h6 style="margin: 0 0 4px; font-weight: 700; color: #1e293b; font-size: 0.95rem;">${p.name}</h6>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 6px;">${p.address || p.locality || ""}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
            ⭐ ${p.source_rating || "4.2"} / 5
          </span>
          <span style="font-size: 0.75rem; font-weight: 700;" class="${trustBadgeClass}">
            🛡 Trust: ${trustScore}/100
          </span>
        </div>
        <a href="/providers/${p.id}" class="btn btn-sm btn-success w-100" style="font-size: 0.75rem; padding: 4px 8px; text-decoration: none; display: block; text-align: center; border-radius: 6px; background-color: #059669; color: white; font-weight: 600;">
          View AI Trust Analysis
        </a>
      </div>
    `;

    const marker = L.marker([pLat, pLng], { icon: customPin }).addTo(map);
    marker.bindPopup(popupHtml);
  });

  if (providerList.length > 1) {
    map.fitBounds(bounds, { padding: [40, 40] });
  }

  // Force map to re-calculate container dimensions after layout settles
  setTimeout(() => { map.invalidateSize(); }, 150);
  setTimeout(() => { map.invalidateSize(); }, 500);

  return map;
}

// Global window assignments for backward compatibility and inline script access
window.initOpenMap = initOpenMap;
window.initGoogleMap = initOpenMap;
window.initInteractiveMap = initOpenMap;

/**
 * Trigger Real Places Discovery via Google Web Search or Gemini AI
 */
async function triggerPlaceDiscovery(buttonEl, mode = "auto") {
  const originalHtml = buttonEl ? buttonEl.innerHTML : "";
  if (buttonEl) {
    buttonEl.disabled = true;
    buttonEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Searching...';
  }

  const statusDiv = document.getElementById("googleSyncStatus");
  if (statusDiv) {
    statusDiv.classList.remove("d-none", "alert-danger", "alert-success");
    statusDiv.classList.add("alert-info");
    statusDiv.innerHTML = `<i class="bi bi-arrow-repeat spin me-2"></i> Searching live ${mode === "google_web" ? "Google / Web Search" : "Google & Gemini AI"} for real establishments...`;
  }

  const filterLocation = document.getElementById("filterLocation") ? document.getElementById("filterLocation").value : "";
  const hiddenLat = document.getElementById("hiddenLat") ? document.getElementById("hiddenLat").value : "";
  const hiddenLng = document.getElementById("hiddenLng") ? document.getElementById("hiddenLng").value : "";

  const urlParams = new URLSearchParams(window.location.search);
  const lat = hiddenLat || urlParams.get("lat") || sessionStorage.getItem("user_lat") || "23.1815";
  const lng = hiddenLng || urlParams.get("lng") || sessionStorage.getItem("user_lng") || "79.9864";
  const locationName = filterLocation || urlParams.get("location") || "Local Area";

  try {
    const payload = {
      lat: parseFloat(lat),
      lng: parseFloat(lng),
      location_name: locationName,
      mode: mode,
      count: 6,
    };

    const res = await fetch("/api/v1/sync/real-places", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await res.json();
    if (result.status === "success") {
      if (buttonEl) {
        buttonEl.innerHTML = `<i class="bi bi-check2-circle me-1"></i> ${result.count || 0} Real Places Found!`;
      }
      if (statusDiv) {
        statusDiv.classList.remove("alert-info");
        statusDiv.classList.add("alert-success");
        statusDiv.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${result.message} Reloading...`;
      }
      setTimeout(() => {
        window.location.reload();
      }, 900);
    } else {
      if (statusDiv) {
        statusDiv.classList.remove("alert-info");
        statusDiv.classList.add("alert-danger");
        statusDiv.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> ${result.message || "Discovery failed."}`;
      }
      alert(result.message || "Could not discover places.");
      if (buttonEl) {
        buttonEl.disabled = false;
        buttonEl.innerHTML = originalHtml;
      }
    }
  } catch (err) {
    console.error("Discovery error:", err);
    if (statusDiv) {
      statusDiv.classList.remove("alert-info");
      statusDiv.classList.add("alert-danger");
      statusDiv.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> Network error connecting to discovery engine.`;
    }
    alert("Network error connecting to place discovery.");
    if (buttonEl) {
      buttonEl.disabled = false;
      buttonEl.innerHTML = originalHtml;
    }
  }
}

function initGeminiDiscoveryUI() {
  const geminiBtns = document.querySelectorAll("#btnGeminiDiscover, .btn-gemini-discover");
  geminiBtns.forEach((btn) => {
    btn.onclick = (e) => {
      e.preventDefault();
      triggerPlaceDiscovery(btn, "gemini");
    };
  });

  const webSearchBtn = document.getElementById("btnWebSearchDiscover");
  if (webSearchBtn) {
    webSearchBtn.onclick = (e) => {
      e.preventDefault();
      triggerPlaceDiscovery(webSearchBtn, "google_web");
    };
  }
}

/**
 * Handle Real Places Sync Modal & live ingestion
 */
function initGoogleSyncModal() {
  const syncGeminiBtn = document.getElementById("btnTriggerGoogleSync");
  const syncWebBtn = document.getElementById("btnTriggerWebSync");
  const saveGeminiKeyBtn = document.getElementById("btnSaveGeminiKey");
  const geminiKeyInput = document.getElementById("inputGeminiApiKey");

  // Load existing Gemini key status
  if (geminiKeyInput) {
    fetch("/api/v1/config/gemini-key")
      .then((r) => r.json())
      .then((data) => {
        if (data && data.configured && data.masked_key) {
          geminiKeyInput.placeholder = `Active Key: ${data.masked_key}`;
        }
      })
      .catch(() => {});
  }

  if (saveGeminiKeyBtn && geminiKeyInput) {
    saveGeminiKeyBtn.addEventListener("click", async () => {
      const key = geminiKeyInput.value.trim();
      saveGeminiKeyBtn.disabled = true;
      saveGeminiKeyBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';

      try {
        const res = await fetch("/api/v1/config/gemini-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ api_key: key }),
        });
        const data = await res.json();
        if (data.status === "success") {
          alert(data.message || "Gemini API Key saved successfully!");
          window.location.reload();
        } else {
          alert(data.message || "Failed to save Gemini API key.");
          saveGeminiKeyBtn.disabled = false;
          saveGeminiKeyBtn.innerHTML = "Save Key";
        }
      } catch (err) {
        alert("Network error while saving Gemini key.");
        saveGeminiKeyBtn.disabled = false;
        saveGeminiKeyBtn.innerHTML = "Save Key";
      }
    });
  }

  if (syncWebBtn) {
    syncWebBtn.addEventListener("click", () => {
      triggerPlaceDiscovery(syncWebBtn, "google_web");
    });
  }

  if (syncGeminiBtn) {
    syncGeminiBtn.addEventListener("click", () => {
      triggerPlaceDiscovery(syncGeminiBtn, "gemini");
    });
  }
}

/**
 * Dark / Light Theme Management
 */
function getPreferredTheme() {
  const saved = localStorage.getItem("tifinify_theme");
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-bs-theme", theme);
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("tifinify_theme", theme);
  } catch (e) {}
  updateThemeIcons(theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-bs-theme") || "light";
  const target = current === "dark" ? "light" : "dark";
  setTheme(target);
}

function updateThemeIcons(theme) {
  const moonIcons = document.querySelectorAll(".theme-icon-moon");
  const sunIcons = document.querySelectorAll(".theme-icon-sun");
  const toggleBtn = document.getElementById("themeToggleBtn");

  if (theme === "dark") {
    moonIcons.forEach((el) => el.classList.add("d-none"));
    sunIcons.forEach((el) => el.classList.remove("d-none"));
    if (toggleBtn) toggleBtn.setAttribute("title", "Switch to Light Theme");
  } else {
    sunIcons.forEach((el) => el.classList.add("d-none"));
    moonIcons.forEach((el) => el.classList.remove("d-none"));
    if (toggleBtn) toggleBtn.setAttribute("title", "Switch to Dark Theme");
  }
}

function initThemeUI() {
  const theme = getPreferredTheme();
  setTheme(theme);

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("tifinify_theme")) {
        setTheme(e.matches ? "dark" : "light");
      }
    });
  }
}

