# APIx-India: High-Frequency Domestic Airfare Price Index & Real-Time Scrapy Engine

An econometric, high-frequency price index platform designed for retail inflation monitoring, high-frequency consumer transport analytics, and macroeconomic policy insights for India (aligned with MoSPI, RBI, and DGCA standards).

Powered by an asynchronous **Scrapy 2.18** crawler engine extracting real-world airfares across key Indian aviation trunk corridors with full multi-source web attribution and live price verification.

---

## ✈️ Key Features

- **Live Multi-Source Web Scraping (Scrapy)**:
  - Asynchronous Twisted/Epoll reactor crawling travel portals and aggregators.
  - Domestic trunk corridors: `DEL-BOM` (Delhi–Mumbai), `BLR-DEL` (Bengaluru–Delhi), `BOM-BLR` (Mumbai–Bengaluru).
  - Advance booking lead-time horizons: `T+1`, `T+7`, `T+15`, `T+30`, and `T+45` days.
  - Direct DOM parsing of real DGCA-registered flight numbers (`IndiGo`, `Air India`, `Akasa Air`, `SpiceJet`, `Air India Express`).
- **Transparent Source Attribution & Live Verification**:
  - Exact website name and domain recorded for every single observation (*Google Flights Aggregator*, *Akasa Air Portal*, *IndiGo Airways*, *Air India*, *SpiceJet*).
  - One-click direct link to verify the fare live on the source website in real time.
- **Jevons Geometric Mean Index Calculation**:
  - Internationally recognized unweighted geometric mean formula ($I = \prod (P_{i,t}/P_{i,0})^{1/N} \times 100$) ensuring transitiveness and time-reversal tests.
  - Real-time statutory DGCA tax separation (base fare vs. 5% GST, UDF, PSF, ASF).
- **Zero-Database Flat-File Persistence Engine**:
  - High-performance, atomic local JSON repository storage (`data/fares.json`, `data/index_history.json`, `data/scrapy_status.json`).
  - Thread-safe and process-safe with file-level synchronization locks.
- **Institutional Analytics Dashboard**:
  - Real-time time series charts for index trajectory vs. baseline ($P_0 = 100.0$).
  - Dynamic lead-time yield curve breakdown ($T+1$ peak last-minute surge to $T+45$ advance discount).
  - Searchable, filterable repository table with JSON export.

---

## 🏗️ Project Architecture

```
├── main.py                      # FastAPI application backend and API routes
├── scraper.py                   # Market scrape coordinator & econometric baseline generators
├── scrapy_runner.py             # Subprocess Scrapy runner with Twisted reactor isolation
├── econometrics.py              # Jevons index engine, tax breakdown, and flat-file I/O
├── spiders/
│   └── flight_fare_spider.py    # Production Scrapy spider for live travel portal scraping
├── templates/
│   └── index.html               # Institutional dark-mode analytics dashboard
├── data/
│   ├── fares.json               # Atomic repository of real-world airfare observations
│   ├── index_history.json       # Daily historical Jevons index points
│   └── scrapy_status.json       # Live Scrapy crawler telemetry & health metrics
├── requirements.txt             # Python dependencies
└── metadata.json                # Application configuration
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (if running Vite preview container)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

Open [http://localhost:3000](http://localhost:3000) in your browser to access the dashboard.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check and flat-file repository status |
| `GET` | `/api/index/summary` | Latest National Airfare Index, 24h delta, route weights |
| `GET` | `/api/index/trends` | Historical daily index points from `data/index_history.json` |
| `GET` | `/api/lead-time-curve` | Yield curve averages across $T+1$ to $T+45$ booking horizons |
| `GET` | `/api/raw-fares?limit=150` | Recent airfare observations with website source attribution |
| `POST` | `/api/scrape/trigger` | Triggers a live Scrapy web harvest across routes |
| `GET` | `/api/scrapy/status` | Current crawler engine telemetry and harvest stats |

---

## 🕷️ Running the Scrapy Spider Manually

You can test the Scrapy spider directly from the command line:

```bash
scrapy runspider spiders/flight_fare_spider.py \
  -a routes=DEL-BOM,BLR-DEL,BOM-BLR \
  -a lead_times=1,7,15,30,45 \
  -O latest_scraped.json
```

---

## 📜 License

MIT License. Designed for open economic research, inflation tracking, and transport economics.
