from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime
import urllib.request
import urllib.error
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- DEVELOPER INFO (FOOTER ONLY) ---
developer_info = {
    "name": "Arpit Ramesan",
    "linkedin": "https://www.linkedin.com/in/arpitramesan",
    "github": "https://github.com/arktrek"
}

# --- STATIC MOCK FALLBACKS ---
# Used if the external NESO API is offline or slow
MOCK_NATIONAL_INTENSITY = {
    "data": [
        {
            "from": "2026-06-21T15:00Z",
            "to": "2026-06-21T15:30Z",
            "intensity": {
                "forecast": 142,
                "actual": 138,
                "index": "moderate"
            }
        }
    ]
}

MOCK_NATIONAL_GENERATION = {
    "data": {
        "from": "2026-06-21T15:00Z",
        "to": "2026-06-21T15:30Z",
        "generationmix": [
            {"fuel": "gas", "perc": 34.2},
            {"fuel": "wind", "perc": 28.5},
            {"fuel": "nuclear", "perc": 16.3},
            {"fuel": "biomass", "perc": 6.8},
            {"fuel": "solar", "perc": 5.2},
            {"fuel": "hydro", "perc": 2.4},
            {"fuel": "imports", "perc": 6.1},
            {"fuel": "coal", "perc": 0.5},
            {"fuel": "other", "perc": 0.0}
        ]
    }
}

MOCK_REGIONAL_DATA = {
    "data": [
        {
            "from": "2026-06-21T15:00Z",
            "to": "2026-06-21T15:30Z",
            "regions": [
                {
                    "regionid": 1,
                    "dnoregion": "Scottish Hydro Electric Power Distribution",
                    "shortname": "North Scotland",
                    "intensity": {"forecast": 25, "index": "very low"},
                    "generationmix": [{"fuel": "wind", "perc": 85.0}, {"fuel": "hydro", "perc": 10.0}, {"fuel": "gas", "perc": 5.0}]
                },
                {
                    "regionid": 2,
                    "dnoregion": "SP Distribution",
                    "shortname": "South Scotland",
                    "intensity": {"forecast": 42, "index": "low"},
                    "generationmix": [{"fuel": "wind", "perc": 70.0}, {"fuel": "nuclear", "perc": 25.0}, {"fuel": "gas", "perc": 5.0}]
                },
                {
                    "regionid": 3,
                    "dnoregion": "Electricity North West",
                    "shortname": "North West England",
                    "intensity": {"forecast": 112, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 45.0}, {"fuel": "wind", "perc": 35.0}, {"fuel": "nuclear", "perc": 20.0}]
                },
                {
                    "regionid": 4,
                    "dnoregion": "Northern Powergrid (Northeast)",
                    "shortname": "North East England",
                    "intensity": {"forecast": 95, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 40.0}, {"fuel": "wind", "perc": 30.0}, {"fuel": "nuclear", "perc": 30.0}]
                },
                {
                    "regionid": 5,
                    "dnoregion": "Northern Powergrid (Yorkshire)",
                    "shortname": "Yorkshire",
                    "intensity": {"forecast": 165, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 55.0}, {"fuel": "biomass", "perc": 25.0}, {"fuel": "wind", "perc": 20.0}]
                },
                {
                    "regionid": 6,
                    "dnoregion": "SP Manweb",
                    "shortname": "North Wales & Merseyside",
                    "intensity": {"forecast": 88, "index": "low"},
                    "generationmix": [{"fuel": "wind", "perc": 50.0}, {"fuel": "nuclear", "perc": 30.0}, {"fuel": "gas", "perc": 20.0}]
                },
                {
                    "regionid": 7,
                    "dnoregion": "Western Power Distribution (South Wales)",
                    "shortname": "South Wales",
                    "intensity": {"forecast": 185, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 70.0}, {"fuel": "wind", "perc": 20.0}, {"fuel": "solar", "perc": 10.0}]
                },
                {
                    "regionid": 8,
                    "dnoregion": "Western Power Distribution (West Midlands)",
                    "shortname": "West Midlands",
                    "intensity": {"forecast": 210, "index": "high"},
                    "generationmix": [{"fuel": "gas", "perc": 80.0}, {"fuel": "imports", "perc": 10.0}, {"fuel": "solar", "perc": 10.0}]
                },
                {
                    "regionid": 9,
                    "dnoregion": "Western Power Distribution (East Midlands)",
                    "shortname": "East Midlands",
                    "intensity": {"forecast": 178, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 65.0}, {"fuel": "solar", "perc": 15.0}, {"fuel": "wind", "perc": 20.0}]
                },
                {
                    "regionid": 10,
                    "dnoregion": "UK Power Networks (Eastern)",
                    "shortname": "East England",
                    "intensity": {"forecast": 130, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 45.0}, {"fuel": "wind", "perc": 40.0}, {"fuel": "solar", "perc": 15.0}]
                },
                {
                    "regionid": 11,
                    "dnoregion": "Western Power Distribution (South West)",
                    "shortname": "South West England",
                    "intensity": {"forecast": 75, "index": "low"},
                    "generationmix": [{"fuel": "solar", "perc": 45.0}, {"fuel": "wind", "perc": 35.0}, {"fuel": "gas", "perc": 20.0}]
                },
                {
                    "regionid": 12,
                    "dnoregion": "UK Power Networks (South Eastern)",
                    "shortname": "South East England",
                    "intensity": {"forecast": 120, "index": "moderate"},
                    "generationmix": [{"fuel": "imports", "perc": 40.0}, {"fuel": "gas", "perc": 30.0}, {"fuel": "wind", "perc": 30.0}]
                },
                {
                    "regionid": 13,
                    "dnoregion": "UK Power Networks (London)",
                    "shortname": "London",
                    "intensity": {"forecast": 240, "index": "high"},
                    "generationmix": [{"fuel": "gas", "perc": 90.0}, {"fuel": "imports", "perc": 10.0}]
                },
                {
                    "regionid": 14,
                    "dnoregion": "Scottish & Southern Energy (Southern)",
                    "shortname": "Southern England",
                    "intensity": {"forecast": 145, "index": "moderate"},
                    "generationmix": [{"fuel": "gas", "perc": 50.0}, {"fuel": "solar", "perc": 25.0}, {"fuel": "wind", "perc": 25.0}]
                }
            ]
        }
    ]
}


# --- HELPER: FETCH FROM API ---
def fetch_api(url):
    import ssl
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url, 
            headers={'Accept': 'application/json', 'User-Agent': 'CarbonFootprintAwarenessPlatform/1.0'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logging.warning(f"Error fetching API {url}: {e}")
        return None


# --- GLOBAL CONTEXT INJECTION ---
@app.context_processor
def inject_global_data():
    return dict(developer=developer_info)


# --- SECURITY & CSP HEADERS ---
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    
    # CSP: Allow Leaflet and Chart.js CDNs, CartoDB Map tiles, and Google Fonts
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' fonts.gstatic.com; "
        "img-src 'self' data: https://*.basemaps.cartocdn.com https://unpkg.com *; "
        "connect-src 'self' https://api.carbonintensity.org.uk;"
    )
    response.headers['Content-Security-Policy'] = csp
    return response


# --- SEO ENDPOINTS ---
@app.route('/robots.txt')
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_root}sitemap.xml"
    ]
    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/sitemap.xml')
def sitemap():
    pages = ['home', 'privacy', 'terms']
    base_url = request.url_root.rstrip('/')
    today = datetime.today().strftime('%Y-%m-%d')
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages:
        url = base_url + ('' if page == 'home' else f'/{page}')
        priority = "1.0" if page == "home" else "0.5"
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append(f'    <lastmod>{today}</lastmod>')
        xml.append(f'    <changefreq>weekly</changefreq>')
        xml.append(f'    <priority>{priority}</priority>')
        xml.append('  </url>')
    xml.append('</urlset>')
    response = make_response("\n".join(xml))
    response.headers["Content-Type"] = "application/xml"
    return response


# --- API PROXY ENDPOINTS ---
@app.route('/api/grid-data')
def get_grid_data():
    intensity_url = "https://api.carbonintensity.org.uk/intensity"
    generation_url = "https://api.carbonintensity.org.uk/generation"
    
    intensity = fetch_api(intensity_url)
    generation = fetch_api(generation_url)
    
    # Check fallback conditions
    if not intensity or "data" not in intensity or not intensity["data"]:
        logging.info("Using mock data for national carbon intensity")
        intensity = MOCK_NATIONAL_INTENSITY
        
    if not generation or "data" not in generation or "generationmix" not in generation["data"]:
        logging.info("Using mock data for national generation mix")
        generation = MOCK_NATIONAL_GENERATION
        
    return jsonify({
        "intensity": intensity["data"][0]["intensity"],
        "generationmix": generation["data"]["generationmix"],
        "period": {
            "from": intensity["data"][0]["from"],
            "to": intensity["data"][0]["to"]
        }
    })

GLOBAL_REGIONS_DEFINITION = [
    # India (Country Code: IN, IP: 49.207.0.1)
    {
        "regionid": 101,
        "country": "India",
        "dnoregion": "Northern Grid, India",
        "shortname": "New Delhi, India",
        "ip": "49.207.0.1",
        "factor": 1.1,
        "default_intensity": 710,
        "generationmix": [
            {"fuel": "coal", "perc": 72.5}, {"fuel": "gas", "perc": 4.5}, {"fuel": "nuclear", "perc": 2.5},
            {"fuel": "hydro", "perc": 9.5}, {"fuel": "solar", "perc": 6.8}, {"fuel": "wind", "perc": 4.2}
        ]
    },
    {
        "regionid": 102,
        "country": "India",
        "dnoregion": "Western Grid, India",
        "shortname": "Mumbai, India",
        "ip": "49.207.0.1",
        "factor": 1.0,
        "default_intensity": 640,
        "generationmix": [
            {"fuel": "coal", "perc": 65.0}, {"fuel": "gas", "perc": 6.0}, {"fuel": "nuclear", "perc": 3.0},
            {"fuel": "hydro", "perc": 11.0}, {"fuel": "solar", "perc": 8.0}, {"fuel": "wind", "perc": 7.0}
        ]
    },
    {
        "regionid": 103,
        "country": "India",
        "dnoregion": "Southern Grid, India",
        "shortname": "Bengaluru, India",
        "ip": "49.207.0.1",
        "factor": 0.9,
        "default_intensity": 580,
        "generationmix": [
            {"fuel": "coal", "perc": 55.0}, {"fuel": "gas", "perc": 5.0}, {"fuel": "nuclear", "perc": 4.0},
            {"fuel": "hydro", "perc": 15.0}, {"fuel": "solar", "perc": 12.0}, {"fuel": "wind", "perc": 9.0}
        ]
    },
    {
        "regionid": 104,
        "country": "India",
        "dnoregion": "Eastern Grid, India",
        "shortname": "Kolkata, India",
        "ip": "49.207.0.1",
        "factor": 1.2,
        "default_intensity": 760,
        "generationmix": [
            {"fuel": "coal", "perc": 82.0}, {"fuel": "gas", "perc": 2.0}, {"fuel": "nuclear", "perc": 1.0},
            {"fuel": "hydro", "perc": 5.0}, {"fuel": "solar", "perc": 6.0}, {"fuel": "wind", "perc": 4.0}
        ]
    },
    # China (Country Code: CN, IP: 180.101.50.188)
    {
        "regionid": 105,
        "country": "China",
        "dnoregion": "Northern Grid, China",
        "shortname": "Beijing, China",
        "ip": "180.101.50.188",
        "factor": 1.2,
        "default_intensity": 650,
        "generationmix": [
            {"fuel": "coal", "perc": 70.0}, {"fuel": "gas", "perc": 3.0}, {"fuel": "nuclear", "perc": 3.0},
            {"fuel": "hydro", "perc": 10.0}, {"fuel": "solar", "perc": 8.0}, {"fuel": "wind", "perc": 6.0}
        ]
    },
    {
        "regionid": 106,
        "country": "China",
        "dnoregion": "Eastern Grid, China",
        "shortname": "Shanghai, China",
        "ip": "180.101.50.188",
        "factor": 1.0,
        "default_intensity": 548,
        "generationmix": [
            {"fuel": "coal", "perc": 61.2}, {"fuel": "gas", "perc": 3.8}, {"fuel": "nuclear", "perc": 4.8},
            {"fuel": "hydro", "perc": 15.4}, {"fuel": "solar", "perc": 8.5}, {"fuel": "wind", "perc": 6.3}
        ]
    },
    {
        "regionid": 107,
        "country": "China",
        "dnoregion": "Southern Grid, China",
        "shortname": "Guangzhou, China",
        "ip": "180.101.50.188",
        "factor": 0.85,
        "default_intensity": 465,
        "generationmix": [
            {"fuel": "coal", "perc": 45.0}, {"fuel": "gas", "perc": 5.0}, {"fuel": "nuclear", "perc": 12.0},
            {"fuel": "hydro", "perc": 25.0}, {"fuel": "solar", "perc": 7.0}, {"fuel": "wind", "perc": 6.0}
        ]
    },
    # USA (Country Code: US, IP: 8.8.8.8)
    {
        "regionid": 108,
        "country": "USA",
        "dnoregion": "PJM Interconnection, USA",
        "shortname": "Washington D.C., USA",
        "ip": "8.8.8.8",
        "factor": 1.0,
        "default_intensity": 378,
        "generationmix": [
            {"fuel": "gas", "perc": 41.5}, {"fuel": "coal", "perc": 21.3}, {"fuel": "nuclear", "perc": 19.8},
            {"fuel": "wind", "perc": 8.4}, {"fuel": "solar", "perc": 6.5}, {"fuel": "hydro", "perc": 2.5}
        ]
    },
    {
        "regionid": 109,
        "country": "USA",
        "dnoregion": "CAISO, USA",
        "shortname": "Los Angeles, USA",
        "ip": "8.8.8.8",
        "factor": 0.7,
        "default_intensity": 265,
        "generationmix": [
            {"fuel": "solar", "perc": 28.5}, {"fuel": "gas", "perc": 32.2}, {"fuel": "wind", "perc": 12.4},
            {"fuel": "hydro", "perc": 14.8}, {"fuel": "nuclear", "perc": 7.2}, {"fuel": "other", "perc": 4.9}
        ]
    },
    {
        "regionid": 110,
        "country": "USA",
        "dnoregion": "ERCOT, USA",
        "shortname": "Dallas, USA",
        "ip": "8.8.8.8",
        "factor": 1.05,
        "default_intensity": 395,
        "generationmix": [
            {"fuel": "gas", "perc": 46.2}, {"fuel": "wind", "perc": 25.4}, {"fuel": "solar", "perc": 12.5},
            {"fuel": "coal", "perc": 11.2}, {"fuel": "nuclear", "perc": 4.7}
        ]
    },
    {
        "regionid": 111,
        "country": "USA",
        "dnoregion": "MISO, USA",
        "shortname": "Chicago, USA",
        "ip": "8.8.8.8",
        "factor": 1.15,
        "default_intensity": 435,
        "generationmix": [
            {"fuel": "coal", "perc": 34.5}, {"fuel": "gas", "perc": 31.8}, {"fuel": "nuclear", "perc": 23.4},
            {"fuel": "wind", "perc": 8.5}, {"fuel": "solar", "perc": 1.8}
        ]
    },
    # France (Country Code: FR, IP: 212.27.48.10)
    {
        "regionid": 112,
        "country": "France",
        "dnoregion": "RTE IDF, France",
        "shortname": "Paris, France",
        "ip": "212.27.48.10",
        "factor": 1.0,
        "default_intensity": 67,
        "generationmix": [
            {"fuel": "nuclear", "perc": 68.5}, {"fuel": "hydro", "perc": 11.2}, {"fuel": "wind", "perc": 12.3},
            {"fuel": "solar", "perc": 4.8}, {"fuel": "gas", "perc": 3.2}
        ]
    },
    {
        "regionid": 113,
        "country": "France",
        "dnoregion": "RTE PACA, France",
        "shortname": "Marseille, France",
        "ip": "212.27.48.10",
        "factor": 0.9,
        "default_intensity": 60,
        "generationmix": [
            {"fuel": "nuclear", "perc": 62.0}, {"fuel": "solar", "perc": 12.5}, {"fuel": "hydro", "perc": 14.2},
            {"fuel": "wind", "perc": 9.3}, {"fuel": "gas", "perc": 2.0}
        ]
    },
    {
        "regionid": 114,
        "country": "France",
        "dnoregion": "RTE ARA, France",
        "shortname": "Lyon, France",
        "ip": "212.27.48.10",
        "factor": 0.95,
        "default_intensity": 63,
        "generationmix": [
            {"fuel": "nuclear", "perc": 65.2}, {"fuel": "hydro", "perc": 18.4}, {"fuel": "wind", "perc": 10.1},
            {"fuel": "solar", "perc": 4.2}, {"fuel": "gas", "perc": 2.1}
        ]
    },
    # Germany (Country Code: DE, IP: 194.25.134.146)
    {
        "regionid": 115,
        "country": "Germany",
        "dnoregion": "50Hertz, Germany",
        "shortname": "Berlin, Germany",
        "ip": "194.25.134.146",
        "factor": 1.1,
        "default_intensity": 403,
        "generationmix": [
            {"fuel": "wind", "perc": 42.5}, {"fuel": "coal", "perc": 30.5}, {"fuel": "gas", "perc": 12.8},
            {"fuel": "solar", "perc": 10.2}, {"fuel": "biomass", "perc": 4.0}
        ]
    },
    {
        "regionid": 116,
        "country": "Germany",
        "dnoregion": "TenneT, Germany",
        "shortname": "Munich, Germany",
        "ip": "194.25.134.146",
        "factor": 0.9,
        "default_intensity": 330,
        "generationmix": [
            {"fuel": "solar", "perc": 22.4}, {"fuel": "wind", "perc": 32.5}, {"fuel": "gas", "perc": 18.8},
            {"fuel": "hydro", "perc": 12.5}, {"fuel": "coal", "perc": 13.8}
        ]
    },
    {
        "regionid": 117,
        "country": "Germany",
        "dnoregion": "Amprion, Germany",
        "shortname": "Frankfurt, Germany",
        "ip": "194.25.134.146",
        "factor": 1.0,
        "default_intensity": 367,
        "generationmix": [
            {"fuel": "coal", "perc": 28.5}, {"fuel": "gas", "perc": 24.8}, {"fuel": "wind", "perc": 28.2},
            {"fuel": "solar", "perc": 10.5}, {"fuel": "biomass", "perc": 8.0}
        ]
    },
    # Brazil (Country Code: BR, IP: 200.147.67.142)
    {
        "regionid": 118,
        "country": "Brazil",
        "dnoregion": "SIN Southeast, Brazil",
        "shortname": "Brasilia, Brazil",
        "ip": "200.147.67.142",
        "factor": 1.0,
        "default_intensity": 144,
        "generationmix": [
            {"fuel": "hydro", "perc": 62.8}, {"fuel": "wind", "perc": 18.2}, {"fuel": "biomass", "perc": 9.4},
            {"fuel": "solar", "perc": 5.8}, {"fuel": "gas", "perc": 3.8}
        ]
    },
    {
        "regionid": 119,
        "country": "Brazil",
        "dnoregion": "SIN South, Brazil",
        "shortname": "Sao Paulo, Brazil",
        "ip": "200.147.67.142",
        "factor": 0.95,
        "default_intensity": 137,
        "generationmix": [
            {"fuel": "hydro", "perc": 65.5}, {"fuel": "wind", "perc": 19.8}, {"fuel": "biomass", "perc": 7.4},
            {"fuel": "solar", "perc": 4.8}, {"fuel": "gas", "perc": 2.5}
        ]
    },
    {
        "regionid": 120,
        "country": "Brazil",
        "dnoregion": "SIN Northeast, Brazil",
        "shortname": "Recife, Brazil",
        "ip": "200.147.67.142",
        "factor": 0.9,
        "default_intensity": 130,
        "generationmix": [
            {"fuel": "wind", "perc": 48.2}, {"fuel": "hydro", "perc": 35.4}, {"fuel": "solar", "perc": 10.2},
            {"fuel": "biomass", "perc": 4.2}, {"fuel": "gas", "perc": 2.0}
        ]
    },
    # Japan (Country Code: JP, IP: 182.22.59.229)
    {
        "regionid": 121,
        "country": "Japan",
        "dnoregion": "TEPCO, Japan",
        "shortname": "Tokyo, Japan",
        "ip": "182.22.59.229",
        "factor": 1.0,
        "default_intensity": 462,
        "generationmix": [
            {"fuel": "gas", "perc": 37.8}, {"fuel": "coal", "perc": 28.5}, {"fuel": "nuclear", "perc": 8.4},
            {"fuel": "solar", "perc": 11.2}, {"fuel": "hydro", "perc": 8.2}, {"fuel": "biomass", "perc": 5.9}
        ]
    },
    {
        "regionid": 122,
        "country": "Japan",
        "dnoregion": "KEPCO, Japan",
        "shortname": "Osaka, Japan",
        "ip": "182.22.59.229",
        "factor": 0.9,
        "default_intensity": 415,
        "generationmix": [
            {"fuel": "nuclear", "perc": 25.4}, {"fuel": "gas", "perc": 32.2}, {"fuel": "coal", "perc": 20.2},
            {"fuel": "solar", "perc": 11.8}, {"fuel": "hydro", "perc": 7.4}, {"fuel": "biomass", "perc": 3.0}
        ]
    },
    {
        "regionid": 123,
        "country": "Japan",
        "dnoregion": "HEPCO, Japan",
        "shortname": "Sapporo, Japan",
        "ip": "182.22.59.229",
        "factor": 1.15,
        "default_intensity": 531,
        "generationmix": [
            {"fuel": "coal", "perc": 42.5}, {"fuel": "gas", "perc": 25.4}, {"fuel": "hydro", "perc": 14.8},
            {"fuel": "wind", "perc": 6.8}, {"fuel": "solar", "perc": 5.5}, {"fuel": "biomass", "perc": 5.0}
        ]
    },
    # Australia (Country Code: AU, IP: 139.130.4.5)
    {
        "regionid": 124,
        "country": "Australia",
        "dnoregion": "AEMO NSW, Australia",
        "shortname": "Sydney, Australia",
        "ip": "139.130.4.5",
        "factor": 1.0,
        "default_intensity": 531,
        "generationmix": [
            {"fuel": "coal", "perc": 53.4}, {"fuel": "gas", "perc": 16.2}, {"fuel": "solar", "perc": 16.5},
            {"fuel": "wind", "perc": 10.4}, {"fuel": "hydro", "perc": 3.5}
        ]
    },
    {
        "regionid": 125,
        "country": "Australia",
        "dnoregion": "AEMO VIC, Australia",
        "shortname": "Melbourne, Australia",
        "ip": "139.130.4.5",
        "factor": 1.1,
        "default_intensity": 584,
        "generationmix": [
            {"fuel": "coal", "perc": 64.5}, {"fuel": "wind", "perc": 16.2}, {"fuel": "solar", "perc": 11.5},
            {"fuel": "gas", "perc": 4.8}, {"fuel": "hydro", "perc": 3.0}
        ]
    },
    {
        "regionid": 126,
        "country": "Australia",
        "dnoregion": "AEMO QLD, Australia",
        "shortname": "Brisbane, Australia",
        "ip": "139.130.4.5",
        "factor": 1.05,
        "default_intensity": 558,
        "generationmix": [
            {"fuel": "coal", "perc": 58.2}, {"fuel": "gas", "perc": 15.4}, {"fuel": "solar", "perc": 18.2},
            {"fuel": "wind", "perc": 6.2}, {"fuel": "hydro", "perc": 2.0}
        ]
    },
    # Nigeria (Country Code: NG, IP: 197.210.8.1)
    {
        "regionid": 127,
        "country": "Nigeria",
        "dnoregion": "TCN North, Nigeria",
        "shortname": "Abuja, Nigeria",
        "ip": "197.210.8.1",
        "factor": 1.0,
        "default_intensity": 395,
        "generationmix": [
            {"fuel": "gas", "perc": 78.4}, {"fuel": "hydro", "perc": 20.8}, {"fuel": "solar", "perc": 0.8}
        ]
    },
    {
        "regionid": 128,
        "country": "Nigeria",
        "dnoregion": "TCN West, Nigeria",
        "shortname": "Lagos, Nigeria",
        "ip": "197.210.8.1",
        "factor": 1.05,
        "default_intensity": 415,
        "generationmix": [
            {"fuel": "gas", "perc": 92.5}, {"fuel": "hydro", "perc": 6.8}, {"fuel": "solar", "perc": 0.7}
        ]
    },
    {
        "regionid": 129,
        "country": "Nigeria",
        "dnoregion": "TCN South, Nigeria",
        "shortname": "Port Harcourt, Nigeria",
        "ip": "197.210.8.1",
        "factor": 1.1,
        "default_intensity": 435,
        "generationmix": [
            {"fuel": "gas", "perc": 96.2}, {"fuel": "hydro", "perc": 3.0}, {"fuel": "solar", "perc": 0.8}
        ]
    },
    # Egypt (Country Code: EG, IP: 196.218.0.1)
    {
        "regionid": 130,
        "country": "Egypt",
        "dnoregion": "EEHC Cairo, Egypt",
        "shortname": "Cairo, Egypt",
        "ip": "196.218.0.1",
        "factor": 1.0,
        "default_intensity": 466,
        "generationmix": [
            {"fuel": "gas", "perc": 82.5}, {"fuel": "hydro", "perc": 8.4}, {"fuel": "solar", "perc": 5.3},
            {"fuel": "wind", "perc": 3.8}
        ]
    },
    {
        "regionid": 131,
        "country": "Egypt",
        "dnoregion": "EEHC Delta, Egypt",
        "shortname": "Alexandria, Egypt",
        "ip": "196.218.0.1",
        "factor": 1.05,
        "default_intensity": 489,
        "generationmix": [
            {"fuel": "gas", "perc": 84.2}, {"fuel": "wind", "perc": 7.4}, {"fuel": "solar", "perc": 4.8},
            {"fuel": "hydro", "perc": 3.6}
        ]
    },
    {
        "regionid": 132,
        "country": "Egypt",
        "dnoregion": "EEHC Aswan, Egypt",
        "shortname": "Aswan, Egypt",
        "ip": "196.218.0.1",
        "factor": 0.5,
        "default_intensity": 233,
        "generationmix": [
            {"fuel": "hydro", "perc": 78.5}, {"fuel": "solar", "perc": 12.4}, {"fuel": "gas", "perc": 9.1}
        ]
    }
]

import threading
import time
import os
import json
import urllib.request
import ssl
import xml.etree.ElementTree as ET

class GlobalDataCache:
    def __init__(self):
        self.cache_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'atmosync_cache.json')
        self.lock = threading.Lock()
        
    def _read_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Error reading cache file: {e}")
        return {}
        
    def _write_cache(self, data):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.warning(f"Error writing cache file: {e}")

    def get_country_intensity(self, country, ip, default_val):
        with self.lock:
            current_time = time.time()
            cache_data = self._read_cache()
            
            # Check if file cache is valid
            file_mtime = 0
            if os.path.exists(self.cache_file):
                file_mtime = os.path.getmtime(self.cache_file)
                
            intensities = cache_data.get("intensities", {})
            
            # If cache is valid (less than 1 hour old), return from it
            if country in intensities and (current_time - file_mtime < 3600):
                return intensities[country]
                
            # Seed default if not in intensities
            if country not in intensities:
                if "intensities" not in cache_data:
                    cache_data["intensities"] = {}
                cache_data["intensities"][country] = default_val
                self._write_cache(cache_data)
                
        # If cache is stale, trigger background update
        if current_time - file_mtime >= 3600:
            try:
                # Touch the file to update its mtime immediately, preventing other processes from double-fetching
                os.utime(self.cache_file, (current_time, current_time))
            except Exception:
                pass
            threading.Thread(target=self._fetch_all_data_background).start()
            
        return cache_data.get("intensities", {}).get(country, default_val)

    def get_global_co2_data(self):
        cache_data = self._read_cache()
        return cache_data.get("global_co2")

    def get_climate_news_data(self):
        cache_data = self._read_cache()
        return cache_data.get("climate_news")

    def _fetch_all_data_background(self):
        # Prevent parallel background updates in the same process
        with self.lock:
            logging.info("Starting background updates for carbon intensity, global CO2, and climate news...")
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # 1. Fetch Carbon Intensities
            unique_countries = {
                "India": ("49.207.0.1", 632),
                "China": ("180.101.50.188", 548),
                "USA": ("8.8.8.8", 378),
                "France": ("212.27.48.10", 67),
                "Germany": ("194.25.134.146", 367),
                "Brazil": ("200.147.67.142", 144),
                "Japan": ("182.22.59.229", 462),
                "Australia": ("139.130.4.5", 531),
                "Nigeria": ("197.210.8.1", 395),
                "Egypt": ("196.218.0.1", 466)
            }
            
            new_intensities = {}
            for country, (ip, default) in unique_countries.items():
                url = f"https://api.thegreenwebfoundation.org/api/v3/ip-to-co2intensity/{ip}"
                try:
                    req = urllib.request.Request(
                        url, 
                        headers={'Accept': 'application/json', 'User-Agent': 'AtmoSync/1.0'}
                    )
                    with urllib.request.urlopen(req, context=ctx, timeout=3.0) as response:
                        res_json = json.loads(response.read().decode('utf-8'))
                        intensity = res_json.get("carbon_intensity")
                        if intensity:
                            new_intensities[country] = float(intensity)
                            logging.info(f"Background fetch success for {country}: {intensity} gCO2e/kWh")
                        else:
                            new_intensities[country] = default
                except Exception as e:
                    logging.warning(f"Background fetch failed for {country}: {e}")
                    new_intensities[country] = default

            # 2. Fetch Global CO2
            new_co2 = None
            co2_url = "https://climateobservatory.org/api/co2/current"
            try:
                req = urllib.request.Request(
                    co2_url, 
                    headers={'Accept': 'application/json', 'User-Agent': 'AtmoSync/1.0'}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=3.0) as response:
                    new_co2 = json.loads(response.read().decode('utf-8'))
                    logging.info("Background global CO2 fetch success.")
            except Exception as e:
                logging.warning(f"Background global CO2 fetch failed: {e}")

            # 3. Fetch Climate News
            new_news = None
            news_url = "https://grist.org/feed/"
            try:
                req = urllib.request.Request(
                    news_url, 
                    headers={'Accept': 'application/xml, text/xml', 'User-Agent': 'AtmoSync/1.0'}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=4.0) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    news_items = []
                    for item in root.findall('.//item')[:5]:
                        title = item.find('title').text if item.find('title') is not None else "Climate Report"
                        link = item.find('link').text if item.find('link') is not None else "#"
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                        if pub_date:
                            pub_date = pub_date[:16]
                        news_items.append({
                            "title": title.strip(),
                            "link": link.strip(),
                            "date": pub_date.strip()
                        })
                    new_news = news_items
                    logging.info("Background climate news fetch success.")
            except Exception as e:
                logging.warning(f"Background climate news fetch failed: {e}")

            # Save everything to the cache file
            cache_data = self._read_cache()
            
            if "intensities" not in cache_data:
                cache_data["intensities"] = {}
            cache_data["intensities"].update(new_intensities)
            
            if new_co2:
                cache_data["global_co2"] = new_co2
                
            if new_news:
                cache_data["climate_news"] = new_news
                
            self._write_cache(cache_data)
            logging.info("Background data cache refresh complete.")

global_cache = GlobalDataCache()

@app.route('/api/regional')
def get_regional_data():
    regional_url = "https://api.carbonintensity.org.uk/regional"
    regional = fetch_api(regional_url)
    
    if not regional or "data" not in regional or not regional["data"] or "regions" not in regional["data"][0]:
        logging.info("Using mock data for regional grid intensity")
        regional = MOCK_REGIONAL_DATA
        
    data_dict = regional["data"][0]
    regions_list = list(data_dict["regions"])
    
    dynamic_global_regions = []
    for r in GLOBAL_REGIONS_DEFINITION:
        base_intensity = global_cache.get_country_intensity(r["country"], r["ip"], r["default_intensity"])
        scaled_intensity = int(base_intensity * r["factor"])
        
        if scaled_intensity < 100:
            index_str = "very low"
        elif scaled_intensity < 150:
            index_str = "low"
        elif scaled_intensity < 250:
            index_str = "moderate"
        elif scaled_intensity < 400:
            index_str = "high"
        else:
            index_str = "very high"
            
        dynamic_global_regions.append({
            "regionid": r["regionid"],
            "dnoregion": r["dnoregion"],
            "shortname": r["shortname"],
            "intensity": {
                "forecast": scaled_intensity,
                "index": index_str
            },
            "generationmix": r["generationmix"]
        })
        
    regions_list.extend(dynamic_global_regions)
    data_dict["regions"] = regions_list
    
    return jsonify(data_dict)


MOCK_CLIMATE_NEWS = [
    {"title": "Renewable Power Surges Globally to Meet Peak Heatwave Demands", "link": "https://grist.org/energy/renewable-energy-record-highs-climate-change-summer-heat/", "date": "Sun, 21 Jun 2026"},
    {"title": "New IPCC Audit Highlights Low-Cost Actions with the Highest Carbon Offsets", "link": "https://grist.org/climate-policy/ipcc-action-items-decarbonize-home-travel/", "date": "Sat, 20 Jun 2026"},
    {"title": "How Urban Centers are Shifting Energy Loads to Clean Grid Intervals", "link": "https://grist.org/grid-modernization/clean-grid-energy-shifting-peak-reduction/", "date": "Fri, 19 Jun 2026"},
    {"title": "Ember Energy Report: Wind and Solar Account for Record Share of European Power", "link": "https://grist.org/wind-solar-records-europe-grid-decarbonize/", "date": "Thu, 18 Jun 2026"},
    {"title": "Thermodynamics of Heat Pumps: Shifting Industrial Boilers to Electrified Cycles", "link": "https://grist.org/heat-pumps-thermodynamic-efficiency-home-heating/", "date": "Wed, 17 Jun 2026"}
]


@app.route('/api/climate-news')
def get_climate_news():
    news = global_cache.get_climate_news_data()
    if not news:
        logging.info("Using mock climate news")
        news = MOCK_CLIMATE_NEWS
    return jsonify(news)


@app.route('/api/global-co2')
def get_global_co2():
    co2_data = global_cache.get_global_co2_data()
    if co2_data:
        return jsonify(co2_data)
        
    # Fallback mock/defaults if cache file is empty
    return jsonify({
        "value": 431.71,
        "unit": "ppm",
        "date": "2026-06-13",
        "source": "NOAA Global Monitoring Laboratory (Mauna Loa)",
        "trend": {"direction": "increasing", "rate_per_year": 2.4}
    })


@app.route('/')
def home():
    meta = {
        "title": "Atmo Sync | Carbon Footprint & Real-Time Weather Simulator",
        "desc": "Track your carbon footprint, view real-time energy grid emissions, and simulate atmospheric weather changes dynamically."
    }
    return render_template('index.html', meta=meta)


@app.route('/privacy')
def privacy(): 
    meta = {
        "title": "Privacy Policy | Carbon Footprint Platform",
        "desc": "Privacy policy and data governance practices for the Carbon Footprint Awareness Platform. Your data stays entirely in the browser."
    }
    return render_template('privacy.html', meta=meta)

@app.route('/terms')
def terms(): 
    meta = {
        "title": "Terms of Service | Carbon Footprint Platform",
        "desc": "Terms and conditions of use for the Carbon Footprint Awareness Platform."
    }
    return render_template('terms.html', meta=meta)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)