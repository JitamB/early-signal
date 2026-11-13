"""
Internship Application Tracker & ATS Scanner (ntfy.sh Push Notifications Edition)
Author: Jitam Barman (IIT Kharagpur)
Automated CLI & database to monitor and apply for Data Science, ML/DL, GenAI, and Analytics internships.
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
import urllib.request
import urllib.error

DB_PATH = os.path.join(os.path.dirname(__file__), "internships.json")
TRACKER_MD_PATH = os.path.join(os.path.dirname(__file__), "TRACKER.md")
CSV_PATH = os.path.join(os.path.dirname(__file__), "internships.csv")
XLSX_PATH = os.path.join(os.path.dirname(__file__), "internships.xlsx")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "ntfy_topic": "EarlySignal",
    "scan_time": "09:00",
    "notify_on_new": True,
    "daily_summary": True
}

LOCATIONS = [
    "india", "bengaluru", "bangalore", "hyderabad", "gurugram", "gurgaon",
    "noida", "mumbai", "pune", "delhi", "chennai", "remote"
]

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def load_db():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_ntfy(message, title=None, click_url=None, priority="default", tags=None, topic=None):
    cfg = load_config()
    target_topic = topic or cfg.get("ntfy_topic", "EarlySignal")
    url = f"https://ntfy.sh/{target_topic}"
    
    headers = {"User-Agent": "InternshipTracker/1.0"}
    if title:
        headers["Title"] = title.encode("utf-8")
    if priority:
        headers["Priority"] = priority
    if tags:
        headers["Tags"] = tags
    if click_url:
        headers["Click"] = click_url
        headers["Actions"] = f"view, Open Portal, {click_url}"
    
    req = urllib.request.Request(url, data=message.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200:
                print(f"[+] ntfy notification sent to topic '{target_topic}'.")
                return True
    except Exception as e:
        print(f"[-] Failed to send ntfy notification: {e}")
        return False

def fetch_greenhouse_jobs(board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode())
            return data.get("jobs", [])
    except Exception:
        return []

def matches_filters(title, location_str):
    title_lower = title.lower()
    loc_lower = location_str.lower()
    
    has_intern = any(k in title_lower for k in ["intern", "internship", "trainee", "fellow", "apprentice"])
    has_domain = any(k in title_lower for k in [
        "data", "ml", "machine learning", "ai", "artificial intelligence",
        "deep learning", "nlp", "vision", "genai", "analyst", "quant", "research"
    ])
    has_loc = any(l in loc_lower for l in LOCATIONS) or "remote" in loc_lower or not loc_lower
    
    return has_intern and has_domain and has_loc

def scan_ats(notify=False):
    db = load_db()
    cfg = load_config()
    existing_urls = {item.get("application_url", "").rstrip("/") for item in db}
    
    greenhouse_boards = [
        ("enterpret", "Enterpret", "GenAI & Frontier Labs", "v2 (GenAI/ML)"),
        ("inmobi", "InMobi / Glance", "B2B SaaS & DevTech", "v1 (C++/Quant)"),
        ("postman", "Postman", "B2B SaaS & DevTech", "v1 or v2"),
        ("browserstack", "BrowserStack", "B2B SaaS & DevTech", "v1 (C++/Quant)"),
        ("meesho", "Meesho", "Consumer Tech & Logistics", "v2 (GenAI/ML)"),
        ("observeai", "Observe.ai", "GenAI & Frontier Labs", "v2 (GenAI/ML)"),
        ("glean", "Glean", "GenAI & Frontier Labs", "v2 (GenAI/ML)"),
        ("razorpay", "Razorpay", "FinTech & Payments", "v2 (GenAI/ML)"),
        ("cred", "CRED", "FinTech & Payments", "v2 (GenAI/ML)"),
        ("rubrik", "Rubrik", "B2B SaaS & DevTech", "v1 (C++/Quant)"),
        ("writer", "Writer", "GenAI & Frontier Labs", "v2 (GenAI/ML)"),
        ("togetherai", "Together AI", "GenAI & Frontier Labs", "v1 (C++/Quant)")
    ]
    
    print("=" * 70)
    print(" 📡 SCANNING PUBLIC ATS JOB BOARDS FOR ACTIVE INTERNSHIP ROLES")
    print("=" * 70)
    
    new_findings = []
    for board_token, company_name, cat, resume in greenhouse_boards:
        print(f"[*] Checking Greenhouse: {company_name} ({board_token})...")
        jobs = fetch_greenhouse_jobs(board_token)
        for job in jobs:
            title = job.get("title", "")
            loc = job.get("location", {}).get("name", "")
            job_url = job.get("absolute_url", "")
            
            if matches_filters(title, loc):
                clean_url = job_url.rstrip("/")
                if clean_url not in existing_urls:
                    job_id = f"{board_token}-{job.get('id')}"
                    new_item = {
                        "id": job_id,
                        "company": company_name,
                        "tier": "Mid-Tier / AI Scaleup",
                        "category": cat,
                        "role": title,
                        "domain": "Data Science / ML / AI",
                        "location": loc if loc else "India / Remote",
                        "season": "Winter / Summer",
                        "ats_type": "greenhouse",
                        "ats_id": board_token,
                        "careers_url": f"https://boards.greenhouse.io/{board_token}",
                        "application_url": job_url,
                        "status": "New - Review",
                        "match_score": 88,
                        "recommended_resume": resume,
                        "notes": f"Discovered via automated ATS scan on {datetime.now().strftime('%Y-%m-%d')}."
                    }
                    new_findings.append(new_item)
                    db.append(new_item)
                    existing_urls.add(clean_url)
                    print(f"    [+] NEW OPENING FOUND: {title} | {loc} | {job_url}")
                    
                    if notify:
                        msg = (
                            f"Company: {company_name}\n"
                            f"Role: {title}\n"
                            f"Location: {loc or 'India / Remote'}\n"
                            f"Recommended Resume: {resume}\n"
                            f"Direct Link: {job_url}"
                        )
                        send_ntfy(
                            message=msg,
                            title=f"🎯 New Opening: {company_name} | {title}",
                            click_url=job_url,
                            priority="high",
                            tags="briefcase,rocket,star"
                        )

    if new_findings:
        print(f"\n[+] Total {len(new_findings)} new opening(s) discovered! Updating database...")
        save_db(db)
        export_all()
    else:
        print("\n[*] Scan complete. No unlisted openings discovered at this moment.")
        if notify and cfg.get("daily_summary"):
            send_ntfy(
                message=f"Daily scan finished at {datetime.now().strftime('%H:%M IST')}. 123 target companies monitored. No new unlisted openings today.",
                title="✅ Daily Internship Scan Check-in",
                priority="low",
                tags="white_check_mark"
            )

def list_openings(filter_cat=None, filter_status=None, query=None, paginate=True):
    db = load_db()
    filtered = []
    for item in db:
        cat = item.get("category", "")
        status = item.get("status", "")
        company = item.get("company", "")
        role = item.get("role", "")
        domain = item.get("domain", "")
        
        if filter_cat and filter_cat.lower() not in cat.lower():
            continue
        if filter_status and filter_status.lower() not in status.lower():
            continue
        if query:
            q = query.lower()
            if q not in company.lower() and q not in role.lower() and q not in domain.lower() and q not in cat.lower():
                continue
        filtered.append(item)
    
    total = len(filtered)
    if total == 0:
        print("\n[-] No companies found matching your filters.")
        return

    page_size = 20
    is_interactive = sys.stdin.isatty() and paginate and total > page_size

    def print_header():
        print("\n" + "=" * 105)
        print(f"{'#':<4} | {'COMPANY':<20} | {'CATEGORY':<28} | {'ROLE':<33} | {'STATUS':<12}")
        print("=" * 105)

    print_header()
    for idx, item in enumerate(filtered, 1):
        cat = item.get("category", "")
        status = item.get("status", "")
        company = item.get("company", "")
        role = item.get("role", "")
        print(f"{idx:<4} | {company[:20]:<20} | {cat[:28]:<28} | {role[:33]:<33} | {status:<12}")
        
        if is_interactive and idx % page_size == 0 and idx < total:
            print("-" * 105)
            prompt = f"--- [Showing {idx} of {total} | Press Enter for next page, or 'q' to quit] --- "
            try:
                user_choice = input(prompt).strip().lower()
                if user_choice == 'q':
                    print("\n[Exited listing early]")
                    return
                print_header()
            except (KeyboardInterrupt, EOFError):
                print()
                return

    print("=" * 105)
    print(f"Showing {total} total tracked companies/roles.")
    print("💡 Tip: View all full details, links, and notes in TRACKER.md")

def update_status(job_id, new_status, notes=None):
    db = load_db()
    updated = False
    for item in db:
        if item.get("id").lower() == job_id.lower() or item.get("company").lower() == job_id.lower():
            item["status"] = new_status
            if notes:
                item["notes"] = f"{item.get('notes', '')} | {notes}"
            item["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            updated = True
            print(f"[+] Updated {item['company']} ({item['id']}) status to: {new_status}")
            break
    if updated:
        save_db(db)
        export_all()
    else:
        print(f"[-] Could not find entry matching '{job_id}'. Run with --list to view valid IDs or company names.")

def export_markdown():
    db = load_db()
    now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
    
    categories = [
        ("🚀 1. GenAI, LLMs, NLP & Frontier AI Startups / Labs", "GenAI & Frontier Labs", 
         "Focus: Indic foundation models, agentic workflows (LangGraph), multi-modal LLMs, and vector search."),
        ("🛵 2. Mid-Tier Consumer Tech, Logistics & Quick Commerce", "Consumer Tech & Logistics", 
         "Focus: Dispatch algorithms, route optimization, dynamic pricing, and spatio-temporal GNNs."),
        ("💳 3. FinTech, InsurTech, Payments & Neobanks", "FinTech & Payments", 
         "Focus: Transaction risk ML, graph fraud detection (Neo4j), alternative credit scoring, and user behavior analytics."),
        ("☁️ 4. B2B SaaS, DevTech & Enterprise Cloud Tech", "B2B SaaS & DevTech", 
         "Focus: API telemetry, test cloud ML, high-volume ad tech, and conversational SaaS agents."),
        ("📊 5. Pure-Play AI & Analytics Consultancies", "AI & Analytics Consultancies", 
         "Focus: Applied statistics, decision sciences, enterprise AI delivery, and industrial digital twins."),
        ("🏢 6. Tier 1 Global Tech MNCs & R&D Hubs", "Global Tech MNCs", 
         "Focus: Large-scale ML infrastructure, neuromorphic computing / SNNs, and research fellowships."),
        ("📈 7. Quant Research, High-Frequency Trading & Global FinTech", "Quant & High-Frequency Trading", 
         "Focus: Low-latency C++, multithreading, stochastic calculus, probability, and convex optimization under uncertainty.")
    ]
    
    md_content = f"""# 🎯 Internship Application Tracker & Pipeline (120+ Companies)
**Candidate:** Jitam Barman | **Institute:** IIT Kharagpur (Dual Degree 5Y, Metallurgical + CS Minor + AI Micro-spec)  
**Domains:** Data Science, ML/DL, GenAI/LLMs, NLP/CV, Analytics, Quant  
**Total Target Companies Tracked:** **{len(db)}**  
**Last Updated:** {now_str}

---

## 📊 Quick Pipeline Breakdown
"""
    for title, cat_key, _ in categories:
        cat_count = len([x for x in db if x.get("category") == cat_key])
        md_content += f"- **{title.split(' ')[1]} {title.split('. ')[1]}**: {cat_count} companies\n"

    md_content += """
---

## 📂 Master Resume Match Matrix: Which Resume for Which Domain?

* **`Jitam_Data v2.pdf` (GenAI / Applied ML / Research):**
  * **Key Anchors:** **VEDAS** (Neo4j Knowledge Graph + LangGraph RCA Agent), **Amazon ML Challenge** (Multimodal ResNet50 + Ridge ensemble), **Microstructural Crack Propagation** (Voronoi + A* Search), and **University of Oulu** research.
  * **Submit to:** Categories 1, 2, 3, 5, and Research Labs in Category 6 (*Sarvam, Enterpret, Level AI, Glean, Swiggy, Zepto, Delhivery, Razorpay, MSR India, Adobe MDSR*).

* **`Jitam_Data.pdf` (High-Performance C++ / Systems / Quant):**
  * **Key Anchors:** **Multithreaded Molecular Dynamics Simulator in C++** ($O(N)$ cell-list decomposition, custom `jthread` pool, 4.5x speedup, bitwise-deterministic), SNN Chance-Constrained QP, Codeforces 1428.
  * **Submit to:** Category 7 (Quant/HFT) & Systems-heavy tech in Categories 4 & 6 (*Tower Research, WorldQuant, Graviton, Jane Street, D.E. Shaw, Google SWE-ML, NVIDIA, BrowserStack*).

---
"""

    for section_title, cat_key, blurb in categories:
        items = [x for x in db if x.get("category") == cat_key]
        md_content += f"\n## {section_title} ({len(items)} Companies)\n*{blurb}*\n\n"
        md_content += "| Company | Role | Domain | Location | Recommended Resume | Status | Link |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for x in items:
            rec = x.get('recommended_resume', 'v2')
            short_rec = "v2 (GenAI/ML)" if "v2" in rec else ("v1 (C++/Quant)" if "v1" in rec else "v1 or v2")
            md_content += f"| **{x['company']}** | {x['role']} | `{x['domain']}` | {x['location']} | **{short_rec}** | `{x['status']}` | [Apply / View]({x['application_url']}) |\n"

    md_content += """
---

## 💡 How to Operate Your Tracker CLI
- **List companies with filters:**
  - By category: `python check_openings.py --category genai` (or `quant`, `logistics`, `fintech`, `saas`, `consultancy`, `mnc`)
  - By search term: `python check_openings.py --search "graph"` or `python check_openings.py --search "bangalore"`
- **Scan public ATS job boards for live postings:** `python check_openings.py --scan`
- **Scan and dispatch push notifications:** `python check_openings.py --scan --notify`
- **Test phone notification:** `python check_openings.py --test-ntfy`
- **Update application status:** `python check_openings.py --update "Sarvam AI" --status "Applied"`
- **Mark alumni referral requested:** `python check_openings.py --update "Zepto" --status "Referral Pinged"`
- **Sync database back to TRACKER.md:** `python check_openings.py --export`
"""

    with open(TRACKER_MD_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[+] Markdown tracker successfully updated at: {TRACKER_MD_PATH}")

def export_csv():
    db = load_db()
    fields = [
        "Company", "Category", "Tier", "Role", "Domain", "Location",
        "Season", "Status", "Recommended Resume", "Application URL", "Notes"
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for x in db:
            writer.writerow([
                x.get("company", ""),
                x.get("category", ""),
                x.get("tier", ""),
                x.get("role", ""),
                x.get("domain", ""),
                x.get("location", ""),
                x.get("season", ""),
                x.get("status", "Identified"),
                x.get("recommended_resume", ""),
                x.get("application_url", ""),
                x.get("notes", "")
            ])
    print(f"[+] CSV tracker successfully updated at: {CSV_PATH}")

def export_xlsx():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        db = load_db()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Internships"

        headers = [
            "Company", "Category", "Tier", "Role", "Domain", "Location",
            "Season", "Status", "Recommended Resume", "Application URL", "Notes"
        ]
        ws.append(headers)

        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        status_colors = {
            "applied": "C6EFCE",
            "referral pinged": "FFEB9C",
            "oa": "BDD7EE",
            "interview": "E2EFDA",
            "identified": "F2F2F2",
            "new - review": "FCE4D6"
        }

        for row_idx, x in enumerate(db, start=2):
            app_url = x.get("application_url", "")
            status = x.get("status", "Identified")
            row_data = [
                x.get("company", ""),
                x.get("category", ""),
                x.get("tier", ""),
                x.get("role", ""),
                x.get("domain", ""),
                x.get("location", ""),
                x.get("season", ""),
                status,
                x.get("recommended_resume", ""),
                app_url,
                x.get("notes", "")
            ]
            ws.append(row_data)

            status_cell = ws.cell(row=row_idx, column=8)
            norm_status = status.strip().lower()
            if norm_status in status_colors:
                status_cell.fill = PatternFill(start_color=status_colors[norm_status], end_color=status_colors[norm_status], fill_type="solid")

            url_cell = ws.cell(row=row_idx, column=10)
            if app_url.startswith("http"):
                url_cell.hyperlink = app_url
                url_cell.font = Font(color="0563C1", underline="single")

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

        wb.save(XLSX_PATH)
        print(f"[+] Excel (.xlsx) tracker successfully updated at: {XLSX_PATH}")
    except ImportError:
        pass
    except Exception as e:
        print(f"[-] Note: Could not generate .xlsx: {e}")

def export_all():
    export_markdown()
    export_csv()
    export_xlsx()

def main():
    parser = argparse.ArgumentParser(description="Internship Application Tracker CLI (ntfy.sh Edition)")
    parser.add_argument("--scan", action="store_true", help="Scan ATS boards for new live openings")
    parser.add_argument("--notify", action="store_true", help="Send ntfy push notification if new jobs found")
    parser.add_argument("--test-ntfy", action="store_true", help="Send a test notification to your ntfy topic")
    parser.add_argument("--topic", type=str, help="Set or override ntfy topic name")
    parser.add_argument("--list", action="store_true", help="List all tracked openings")
    parser.add_argument("--all", action="store_true", help="Print all without interactive pagination")
    parser.add_argument("--category", type=str, help="Filter listing by category (e.g. genai, quant, logistics, fintech)")
    parser.add_argument("--search", type=str, help="Search by company name, role, or keyword")
    parser.add_argument("--export", action="store_true", help="Regenerate TRACKER.md from JSON database")
    parser.add_argument("--update", type=str, help="Company name or ID to update")
    parser.add_argument("--status", type=str, help="New status (e.g., 'Applied', 'Referral Pinged', 'OA')")
    parser.add_argument("--notes", type=str, help="Optional note to append")
    
    args = parser.parse_args()
    
    if args.topic:
        cfg = load_config()
        cfg["ntfy_topic"] = args.topic.strip()
        save_config(cfg)
        print(f"[+] Default ntfy topic set to: '{cfg['ntfy_topic']}'")
        if not (args.test_ntfy or args.scan or args.update or args.export or args.list or args.category or args.search or args.all):
            return
    
    if args.test_ntfy:
        cfg = load_config()
        print(f"[*] Sending test push notification to ntfy topic: '{cfg['ntfy_topic']}'...")
        success = send_ntfy(
            message=f"Test alert from your IIT Kharagpur Internship Tracker at {datetime.now().strftime('%H:%M:%S IST')}!\n123 target companies active.",
            title="Internship Tracker Test Ping",
            click_url="https://github.com/JitamB",
            priority="high",
            tags="bell,rocket"
        )
        if success:
            print("[+] Success! Check your phone's ntfy app now.")
        else:
            print("[-] Notification failed. Check internet connection.")
    elif args.scan:
        scan_ats(notify=args.notify)
    elif args.update and args.status:
        update_status(args.update, args.status, args.notes)
    elif args.export:
        export_all()
    elif args.list or args.category or args.search:
        list_openings(filter_cat=args.category, query=args.search, paginate=not args.all)
    else:
        export_all()
        list_openings(paginate=not args.all)

if __name__ == "__main__":
    main()
