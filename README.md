# Automated Internship Sourcing & Application Pipeline
**Candidate:** Jitam Barman | **Institute:** IIT Kharagpur (Dual Degree 5Y, Metallurgical + CS Minor + AI Micro-spec)  
**Domains:** Data Science, Machine Learning, Deep Learning, GenAI/LLMs, NLP, Computer Vision, Analytics, Quant

---

## Architecture & Cloud Automation

This repository runs completely in the cloud with **zero local hardware dependency**:
1. **GitHub Actions Cron:** Executes automated scans twice a day (09:00 AM & 06:00 PM IST) on an Ubuntu runner.
2. **ATS Board Scanner:** Queries public ATS endpoints (Greenhouse, Lever, Ashby) for 120+ tracked tech, AI, and quant companies.
3. **Instant Mobile Alerts (`ntfy.sh`):** Pushes high-priority alerts with 1-click application buttons straight to your phone.
4. **Auto-Commit:** If new openings are detected, GitHub Actions commits and updates [TRACKER.md](TRACKER.md) directly on GitHub.

---

## 📊 Live Tracker & Company Roster
All 120+ target companies, roles, application URLs, and resume assignments are tracked across:
* 📄 **[TRACKER.md](TRACKER.md)** — Clean formatted markdown dashboard for quick reading on GitHub / mobile.
* 📈 **[internships.csv](internships.csv)** — Visual tabular spreadsheet; renders directly as an interactive table on GitHub, and opens in Microsoft Excel or Google Sheets.
* 📗 **`internships.xlsx`** — Excel spreadsheet with colored headers and clickable hyperlinks, generated automatically on each cloud run.
* 🤖 **[internships.json](internships.json)** — Machine-readable database maintaining metadata, IDs, and ATS tokens.

---

## Triggering from Your Phone
You don't need a computer to run a fresh scan:
1. Open this repository on the **GitHub Mobile App** or mobile browser.
2. Go to **Actions** $\rightarrow$ **Daily Internship Scanner & ntfy Alert**.
3. Tap **Run workflow**.
4. The cloud runner will execute the scan and push updates to your `ntfy` app within 30 seconds!
