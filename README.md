
# **Helsinki Multi-Vehicle Route Optimization (VRP)**

*A G-OPT Case Study*

This project demonstrates a real-world **Vehicle Routing Problem (VRP)** solved using:

* 🇫🇮 Real Helsinki coordinates
* 🚚 Three delivery vehicles
* 🕒 Time windows
* 📦 Vehicle capacity constraints
* 📍 Geographical map visualization
* ⚙️ Google OR-Tools optimization engine

G-OPT provides optimization services for small delivery companies in Finland and the Nordic region.
This project is part of the official G-OPT portfolio.

---

## 🔍 **Features**

* Multi-vehicle route optimization
* VRPTW (Vehicle Routing Problem with Time Windows)
* Capacity constraints
* Realistic travel times using Haversine distance
* Professional map visualization
* Direction arrows and depot highlight
* PDF export for business reports

---

## 📁 **Project Files**

| File                          | Description                      |
| ----------------------------- | -------------------------------- |
| `helsinki_vrp_portfolio.py`   | Main optimization script         |
| `helsinki_vrp.csv`            | Dataset of 10 Helsinki locations |
| `gopt_case_study_routing.pdf` | Professional case study (1 page) |
| `helsinki_vrp_portfolio.png`  | Route visualization image        |
| `README.md`                   | Project documentation            |

---

## 🧠 **Optimization Model**

* Google OR-Tools Routing Model
* Haversine distance matrix (km)
* Time dimension with waiting
* Capacity constraints (vehicle load)
* Guided Local Search metaheuristic

---

## ▶️ **How to Run**

Install dependencies:

```bash
pip install ortools pandas numpy geopandas shapely contextily matplotlib
```

Run the optimization:

```bash
python helsinki_vrp_portfolio.py
```

Outputs:

* PNG map visualization
* PDF routing report
* Console route summary

---

## 🧾 **Case Study**

A professional, 1-page G-OPT case study is included:

* `gopt_case_study_routing.pdf`

This document is suitable for portfolio presentation, client proposals, and demonstrations.

---

## 🏢 **About G-OPT**

**G-OPT (Global Optimization)** provides affordable and intelligent optimization solutions for:

* Route optimization
* Delivery scheduling
* Logistics analytics
* Technician & service routing

Helping businesses reduce costs, improve efficiency, and automate operational planning.
