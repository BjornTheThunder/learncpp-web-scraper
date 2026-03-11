# 📚 LearnCPP Lessons Web Scraper

A lightweight Python utility designed to scrape educational content from [learncpp.com](https://www.learncpp.com) and generate a local, offline copy for personal study.

---

## ⚠️ Important Disclaimers

### Educational Purposes Only
This project is developed and shared strictly for **educational purposes**. It serves as a technical exercise in web scraping and as a tool for students to maintain a personal offline backup of their study materials.

### Usage & Redistribution Policy
In alignment with the requirements specified by the site owner:
* **No Redistribution:** Content downloaded using this tool **must not** be redistributed, hosted elsewhere, or shared publicly.
* **Personal Use:** Users should only keep a single offline copy for private, individual use.

### Project Status
> [!NOTE]
> This project is currently still in **development and testing phase** 

---

## 🚀 Features

* **Recursive Scraping:** Automatically navigates through chapters and lessons.
* **Local Storage:** Saves lessons in a structured directory format.
* **Preservation:** Accessibility and preservation should be available for all and this tool permits that, keeping the owners wishes on redistribution

---

## 🛠️ Getting Started

### Prerequisites
* install Python 3.10 or higher
* `pip` (Python package manager)
* use pip to install requests and beautifulsoup4

#### On Windows open PowerShell and execute:
```shell
pip install requests beautifulsoup4 pywebview
```

#### On Linux execute:
1. On Debian:
```bash
sudo apt update && sudo apt upgrade
sudo apt install python-requests python-bs4 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```
2. On Arch
```bash
sudo pacman -Sy python-requests python-beautifulsoup4 python-pywebview webkit2gtk-4.1 python-gobject
```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/BjornTheThunder/learncpp-web-scraper
   cd learncpp-scraper
2. Run the scraper:
```bash
   python scraper.py
```
3. Open index.html downloaded inside content folder
