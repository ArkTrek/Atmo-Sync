document.addEventListener('DOMContentLoaded', () => {
    // --- MAP INITIALIZATION ---
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Center map globally to show all populous regions
    const map = L.map('map', {
        center: [20, 12],
        zoom: 2.2,
        zoomControl: true,
        scrollWheelZoom: false,
        minZoom: 1.5
    });

    // Dark tiles (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Coordinate mappings for DNO (1-14) and Global Populous Regions (101-110)
    const regionCoordinates = {
        // Great Britain DNO Zones
        1: [57.5, -4.5],      // North Scotland
        2: [55.5, -3.5],      // South Scotland
        3: [54.3, -2.7],      // North West England
        4: [54.8, -1.6],      // North East England
        5: [53.9, -1.2],      // Yorkshire
        6: [53.2, -3.0],      // North Wales & Merseyside
        7: [51.8, -3.7],      // South Wales
        8: [52.5, -2.2],      // West Midlands
        9: [52.8, -1.0],      // East Midlands
        10: [52.4, 0.8],      // East England
        11: [50.8, -3.8],     // South West England
        12: [51.2, 0.5],      // South East England
        13: [51.5074, -0.1278], // London
        14: [51.0, -1.3],     // Southern England
        
        // Global Populous Hubs
        // India (101-104)
        101: [28.6139, 77.2090],  // New Delhi
        102: [19.0760, 72.8777],  // Mumbai
        103: [12.9716, 77.5946],  // Bengaluru
        104: [22.5726, 88.3639],  // Kolkata
        // China (105-107)
        105: [39.9042, 116.4074], // Beijing
        106: [31.2304, 121.4737], // Shanghai
        107: [23.1291, 113.2644], // Guangzhou
        // USA (108-111)
        108: [38.9072, -77.0369], // Washington D.C.
        109: [34.0522, -118.2437], // Los Angeles
        110: [32.7767, -96.7970],  // Dallas
        111: [41.8781, -87.6298],  // Chicago
        // France (112-114)
        112: [48.8566, 2.3522],   // Paris
        113: [43.2965, 5.3698],   // Marseille
        114: [45.7640, 4.8357],   // Lyon
        // Germany (115-117)
        115: [52.5200, 13.4050],  // Berlin
        116: [48.1351, 11.5820],  // Munich
        117: [50.1109, 8.6821],   // Frankfurt
        // Brazil (118-120)
        118: [-15.7938, -47.8828], // Brasilia
        119: [-23.5505, -46.6333], // Sao Paulo
        120: [-8.0539, -34.8811],  // Recife
        // Japan (121-123)
        121: [35.6762, 139.6503], // Tokyo
        122: [34.6937, 135.5023], // Osaka
        123: [43.0618, 141.3545], // Sapporo
        // Australia (124-126)
        124: [-33.8688, 151.2093], // Sydney
        125: [-37.8136, 144.9631], // Melbourne
        126: [-27.4698, 153.0251], // Brisbane
        // Nigeria (127-129)
        127: [9.0765, 7.3986],     // Abuja
        128: [6.5244, 3.3792],     // Lagos
        129: [4.8156, 7.0498],     // Port Harcourt
        // Egypt (130-132)
        130: [30.0444, 31.2357],   // Cairo
        131: [31.2001, 29.9187],   // Alexandria
        132: [24.0889, 32.8998]    // Aswan
    };

    // Index to color mapper
    function getIntensityColor(index) {
        switch(index) {
            case 'very low':
            case 'low':
                return '#34d399'; // Mint Green
            case 'moderate':
                return '#fbbf24'; // Amber Yellow
            case 'high':
            case 'very high':
                return '#f87171'; // Soft Red
            default:
                return '#64748b'; // Slate Grey
        }
    }

    // Keep track of active markers to update them dynamically without duplicating
    const activeMarkers = {};

    function fetchMapData() {
        fetch('/api/regional')
            .then(response => {
                if (!response.ok) throw new Error("API network error");
                return response.json();
            })
            .then(data => {
                // Remove loading indicator
                const loader = document.getElementById('map-loader');
                if (loader) loader.style.display = 'none';

                if (!data || !data.regions) return;

                data.regions.forEach(region => {
                    const regionId = region.regionid;
                    const coords = regionCoordinates[regionId];

                    if (coords) {
                        const intensity = region.intensity;
                        const forecast = intensity.forecast;
                        const index = intensity.index;
                        const color = getIntensityColor(index);
                        const genMix = region.generationmix || [];

                        // Adjust size based on intensity (min 8, max 25)
                        const radius = Math.min(25, Math.max(8, 8 + (forecast * 0.04)));

                        // Create popup content
                        let popupHTML = `
                            <div class="popup-title">${region.shortname}</div>
                            <div class="popup-intensity">
                                Carbon Intensity: <span style="color: ${color}; font-family: 'Plus Jakarta Sans', sans-serif;">${forecast} gCO₂/kWh</span>
                                <span class="intensity-badge ${index === 'very low' ? 'low' : (index === 'very high' ? 'high' : index)}" 
                                      style="padding: 0.15rem 0.5rem; font-size: 0.65rem; display: inline-block; vertical-align: middle; margin-left: 0.25rem;">
                                    ${index}
                                </span>
                            </div>
                            <div style="font-weight: 700; font-size: 0.75rem; margin-bottom: 0.35rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.4rem; color: var(--text-secondary);">
                                Electricity Generation Mix:
                            </div>
                            <div class="popup-mix-grid">
                        `;

                        // Sort fuel mix by percentage descending
                        const sortedGenMix = [...genMix].sort((a, b) => b.perc - a.perc);

                        sortedGenMix.forEach(item => {
                            if (item.perc > 0) {
                                const percentStr = item.perc.toFixed(1);
                                popupHTML += `
                                    <div class="mix-fuel-name">${item.fuel}</div>
                                    <div class="mix-fuel-bar-container">
                                        <div class="mix-fuel-bar">
                                            <div class="mix-fuel-fill" style="width: ${percentStr}%; background: ${color};"></div>
                                        </div>
                                        <div class="mix-fuel-val">${percentStr}%</div>
                                    </div>
                                `;
                            }
                        });

                        popupHTML += `
                            </div>
                            <div style="font-size: 0.65rem; color: var(--text-muted); text-align: right; margin-top: 0.6rem;">
                                Network ID: ${regionId > 100 ? 'Global Grid Node' : 'UK DNO ' + region.dnoregion}
                            </div>
                        `;

                        if (activeMarkers[regionId]) {
                            // Update existing marker style and popup content in place
                            const marker = activeMarkers[regionId];
                            marker.setStyle({
                                fillColor: color
                            });
                            marker.setRadius(radius);
                            marker.setPopupContent(popupHTML);
                        } else {
                            // Create circle marker
                            const marker = L.circleMarker(coords, {
                                radius: radius,
                                fillColor: color,
                                color: '#020617', // Match slate background border
                                weight: 2,
                                opacity: 0.9,
                                fillOpacity: 0.65
                            }).addTo(map);

                            marker.bindPopup(popupHTML);

                            // Add interaction listeners
                            marker.on('mouseover', function(e) {
                                this.openPopup();
                                this.setStyle({ fillOpacity: 0.9, weight: 3, color: '#f8fafc' });
                            });
                            
                            marker.on('mouseout', function(e) {
                                this.setStyle({ fillOpacity: 0.65, weight: 2, color: '#020617' });
                            });

                            activeMarkers[regionId] = marker;
                        }
                    }
                });
            })
            .catch(err => {
                console.error("Failed to render regional global map: ", err);
                const loader = document.getElementById('map-loader');
                // Only replace loader text if it's the first load (loader is still visible)
                if (loader && loader.style.display !== 'none') {
                    loader.innerHTML = `
                        <div style="color: #f87171; font-weight: 700; padding: 2rem; text-align: center;">
                            ❌ Failed to load live regional carbon intensity data.
                            <br><span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: normal;">Please check your internet connection or reload the dashboard.</span>
                        </div>
                    `;
                }
            });
    }

    // Trigger initial load
    fetchMapData();

    // Periodically refresh map marker data in background every 30 seconds
    setInterval(fetchMapData, 30000);

    // Invalidate map size when tab changes to redraw Leaflet tiles correctly
    document.addEventListener('tabChanged', () => {
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
    });
});
