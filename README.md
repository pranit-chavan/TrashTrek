# ♻️ TrashTrek: Smart City Waste Management
*(Formerly SmartBin++)*

**TrashTrek** is an advanced Data Structures and Algorithms (DSA) project that optimizes municipal waste collection routes using Knapsack, Dijkstra's, and Greedy algorithms, powered by **Real-World Map Data**.

---

## 🎯 The Core Innovation

In typical routing problems, systems optimize solely for the *shortest distance*. TrashTrek introduces a practical, real-world metric:
**`Efficiency = (Weight × Fill_Level) / Distance`**

This ensures that trucks actively prioritize overflowing bins while maximizing the amount of garbage collected per kilometer driven.

---

## 🗺️ Real Map Integration (OSRM & Leaflet)

Unlike traditional console-based DSA projects, TrashTrek features a complete interactive web dashboard:
- **Leaflet.js Mapping:** A fully interactive street map centered on Indira Nagar, Nashik (or any specific city).
- **OSRM Distance Matrix:** Uses the Open Source Routing Machine API to calculate the *actual road driving distances* between bins, completely replacing random Euclidean geometry with real-world infrastructure data.
- **Route Visualization:** Beautifully draws the exact driving path on the streets, highlighting selected bins and fading out inefficient ones.

---

## ⚙️ Algorithms Used

1. **Route-Aware Greedy Selection (0/1 Knapsack variant)** 
   Selects bins based on the custom efficiency ratio to maximize truck capacity. | `O(n²)`
2. **Dijkstra's Algorithm** 
   Finds the shortest driving path between valid locations using the real road distance matrix. | `O(V² + E log V)`
3. **Nearest Neighbor Optimization** 
   Determines the absolute optimal visiting sequence. | `O(n²)`

---

## 🚀 Quick Start

```bash
# 1. Install dependencies (Requires internet for API calls)
pip install -r requirements.txt

# 2. Run the Web Dashboard
python app.py

# 3. Open your browser
http://localhost:5000
```

---

## 🌐 Dashboard Features

- 🗺️ **Interactive Real Maps** - Click on any bin marker on the map to manually set its garbage weight and fill level.
- ⚙️ **Dynamic Optimization** - Watch the algorithm draw the best driving route instantly.
- 🚛 **Multi-Truck Support** - Splits routes dynamically if one truck cannot carry all prioritized waste, drawing each truck's path in a unique color.
- 📊 **Results Analytics** - Tracks capacity utilization, total distance driven, and total weight collected.

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `trashtrek.py` | Core algorithmic optimization engine |
| `app.py` | Flask server and OSRM API handler |
| `templates/index.html` | UI, Leaflet Map, and GeoJSON routing logic |
| `requirements.txt` | Python dependencies (Flask, Requests, Numpy) |

---

## ✅ Key Benefits Demonstrated

- **Solves a Real Problem:** Bridges theoretical DSA with practical urban logistics.
- **Visual Impact:** Easily explainable to non-technical stakeholders via the live map.
- **Scalable Architecture:** Easily expandable to hundreds of IoT sensor nodes.

**DSA Concepts:** Dynamic Programming • Graph Algorithms • Greedy Heuristics • Priority Queues • REST API Integration
