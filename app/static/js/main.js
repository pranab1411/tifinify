/**
 * Tifinify Core Frontend Script
 * Handles Google Maps JS API, Leaflet Fallback Engine, Places Autocomplete,
 * Geolocation Auto-Fix, Review Trust Charts, and Live Google Places Sync.
 */

document.addEventListener("DOMContentLoaded", () => {
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
        (err) => {
          console.warn("Auto-geolocation skipped:", err.message);
        },
        { timeout: 6000 }
      );
    }
  }
}

/**
 * Handle "Use Current Location" button clicks
 */
function initGeolocationButtons() {
  const geoBtns = document.querySelectorAll(".btn-use-location");
  geoBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser. Please enter your locality manually.");
        return;
      }

      const originalHtml = btn.innerHTML;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Locating...';
      btn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;

          sessionStorage.setItem("user_lat", lat);
          sessionStorage.setItem("user_lng", lng);

          const form = btn.closest("form");
          if (form) {
            let latInput = form.querySelector('input[name="lat"]');
            let lngInput = form.querySelector('input[name="lng"]');
            let locInput = form.querySelector('input[name="location"]');

            if (!latInput) {
              latInput = document.createElement("input");
              latInput.type = "hidden";
              latInput.name = "lat";
              form.appendChild(latInput);
            }
            if (!lngInput) {
              lngInput = document.createElement("input");
              lngInput.type = "hidden";
              lngInput.name = "lng";
              form.appendChild(lngInput);
            }

            latInput.value = lat;
            lngInput.value = lng;
            if (locInput) {
              locInput.value = "Current Location (GPS)";
            }
            form.submit();
          } else {
            window.location.href = `/providers/discovery?lat=${lat}&lng=${lng}&location=Current+Location+(GPS)`;
          }
        },
        (err) => {
          btn.innerHTML = originalHtml;
          btn.disabled = false;
          alert(`Location access was denied or timed out (${err.message}). Using manual search.`);
        },
        { timeout: 8000 }
      );
    });
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

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          data: [positivePct, neutralPct, negativePct],
          backgroundColor: ["#10B981", "#94A3B8", "#EF4444"],
          borderWidth: 2,
          borderColor: "#FFFFFF",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 12, padding: 15, font: { size: 12, weight: 600 } },
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
 * Wire Gemini AI Discovery button to /api/v1/sync/gemini-places
 */
function initGeminiDiscoveryUI() {
  const geminiBtns = document.querySelectorAll("#btnGeminiDiscover, .btn-gemini-discover");
  if (!geminiBtns || geminiBtns.length === 0) return;

  geminiBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Scanning with Gemini AI...`;

      const hiddenLat = document.getElementById("hiddenLat") ? document.getElementById("hiddenLat").value : null;
      const hiddenLng = document.getElementById("hiddenLng") ? document.getElementById("hiddenLng").value : null;
      const filterLocation = document.getElementById("filterLocation") ? document.getElementById("filterLocation").value : "";

      const urlParams = new URLSearchParams(window.location.search);
      const lat = hiddenLat || urlParams.get("lat") || sessionStorage.getItem("user_lat") || "28.6139";
      const lng = hiddenLng || urlParams.get("lng") || sessionStorage.getItem("user_lng") || "77.2090";
      const locationName = filterLocation || urlParams.get("location") || "Current Location";

      try {
        const payload = {
          lat: parseFloat(lat),
          lng: parseFloat(lng),
          location_name: locationName,
          count: 5,
        };

        const res = await fetch("/api/v1/sync/gemini-places", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const result = await res.json();
        if (result.status === "success") {
          btn.classList.remove("btn-success");
          btn.classList.add("btn-outline-success");
          btn.innerHTML = `<i class="bi bi-check2-circle me-1"></i> ${result.count || 5} Places Discovered!`;

          setTimeout(() => {
            window.location.reload();
          }, 800);
        } else {
          alert(result.message || "Could not discover places with Gemini.");
          btn.disabled = false;
          btn.innerHTML = originalHtml;
        }
      } catch (err) {
        console.error("Gemini discovery error:", err);
        alert("Network error while connecting to Gemini place discovery.");
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      }
    });
  });
}

/**
 * Handle Google Places Sync Modal & live ingestion
 */
function initGoogleSyncModal() {
  const syncBtn = document.getElementById("btnTriggerGoogleSync");
  const saveKeyBtn = document.getElementById("btnSaveGoogleKey");
  const keyInput = document.getElementById("inputGoogleApiKey");

  if (saveKeyBtn && keyInput) {
    saveKeyBtn.addEventListener("click", async () => {
      const key = keyInput.value.trim();
      saveKeyBtn.disabled = true;
      saveKeyBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';

      try {
        const res = await fetch("/api/v1/config/google-maps-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ api_key: key }),
        });
        const data = await res.json();
        if (data.status === "success") {
          window.location.reload();
        } else {
          alert(data.message || "Failed to save API key.");
          saveKeyBtn.disabled = false;
          saveKeyBtn.innerHTML = "Save Key";
        }
      } catch (err) {
        alert("Network error while saving API key.");
        saveKeyBtn.disabled = false;
        saveKeyBtn.innerHTML = "Save Key";
      }
    });
  }

  if (syncBtn) {
    syncBtn.addEventListener("click", async () => {
      const originalText = syncBtn.innerHTML;
      const statusDiv = document.getElementById("googleSyncStatus");
      const filterLocation = document.getElementById("filterLocation") ? document.getElementById("filterLocation").value : "";
      const customKey = keyInput ? keyInput.value.trim() : "";

      const urlParams = new URLSearchParams(window.location.search);
      const lat = urlParams.get("lat") || sessionStorage.getItem("user_lat") || "23.1815";
      const lng = urlParams.get("lng") || sessionStorage.getItem("user_lng") || "79.9864";
      const locationName = filterLocation || urlParams.get("location") || "Local Area";

      syncBtn.disabled = true;
      syncBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Discovering with Gemini AI...';
      if (statusDiv) {
        statusDiv.classList.remove("d-none", "alert-danger", "alert-success");
        statusDiv.classList.add("alert-info");
        statusDiv.innerHTML = '<i class="bi bi-arrow-repeat spin me-2"></i> Querying Gemini AI Place Intelligence and computing AI Trust Scores...';
      }

      try {
        let endpoint = "/api/v1/sync/gemini-places";
        let payload = {
          lat: parseFloat(lat),
          lng: parseFloat(lng),
          location_name: locationName,
          count: 5,
        };

        if (customKey && customKey.length > 10) {
          endpoint = "/api/v1/sync/google-places";
          payload = { lat: parseFloat(lat), lng: parseFloat(lng), query: locationName, api_key: customKey };
        }

        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const result = await res.json();
        if (result.status === "success") {
          if (statusDiv) {
            statusDiv.classList.remove("alert-info");
            statusDiv.classList.add("alert-success");
            statusDiv.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${result.message || "Places discovered successfully!"} Reloading...`;
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
          syncBtn.disabled = false;
          syncBtn.innerHTML = originalText;
        }
      } catch (err) {
        if (statusDiv) {
          statusDiv.classList.remove("alert-info");
          statusDiv.classList.add("alert-danger");
          statusDiv.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> Failed to communicate with discovery endpoint.`;
        }
        syncBtn.disabled = false;
        syncBtn.innerHTML = originalText;
      }
    });
  }

  const quickSyncBtn = document.getElementById("btnQuickSyncNearby");
  if (quickSyncBtn) {
    quickSyncBtn.addEventListener("click", async () => {
      const originalHtml = quickSyncBtn.innerHTML;
      quickSyncBtn.disabled = true;
      quickSyncBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> AI Discovering...';

      const filterLocation = document.getElementById("filterLocation") ? document.getElementById("filterLocation").value : "";
      const urlParams = new URLSearchParams(window.location.search);
      const lat = urlParams.get("lat") || sessionStorage.getItem("user_lat") || "23.1815";
      const lng = urlParams.get("lng") || sessionStorage.getItem("user_lng") || "79.9864";
      const locationName = filterLocation || urlParams.get("location") || "Local Area";

      try {
        const payload = {
          lat: parseFloat(lat),
          lng: parseFloat(lng),
          location_name: locationName,
          count: 5,
        };

        const res = await fetch("/api/v1/sync/gemini-places", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const result = await res.json();
        if (result.status === "success") {
          quickSyncBtn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Places Discovered!';
          setTimeout(() => {
            window.location.reload();
          }, 700);
        } else {
          alert(result.message || "Could not discover places.");
          quickSyncBtn.disabled = false;
          quickSyncBtn.innerHTML = originalHtml;
        }
      } catch (err) {
        alert("Network error while discovering places.");
        quickSyncBtn.disabled = false;
        quickSyncBtn.innerHTML = originalHtml;
      }
    });
  }
}
