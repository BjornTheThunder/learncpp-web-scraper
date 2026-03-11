import requests
from bs4 import BeautifulSoup
import time
import os
import concurrent.futures
import json
from urllib.parse import urljoin, urlparse, urlunparse, quote_plus

# --- Configuration ---
START_URL = "https://www.learncpp.com/cpp-tutorial/introduction-to-these-tutorials/"
BASE_URL = "https://www.learncpp.com"
MAX_LESSONS = 10
STOP_TITLE = "C.1 — The end?"
OUTPUT_FOLDER = "content"
IMG_FOLDER = os.path.join(OUTPUT_FOLDER, "img")
CSS_FILENAME = "style.css"
CHECKPOINT_FILE = os.path.join(OUTPUT_FOLDER, "checkpoint.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def download_single_image(img_url, local_path):
    """Worker function to download a single image."""
    if os.path.exists(local_path):
        return  # Skip if we already downloaded it

    try:
        img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
        with open(local_path, "wb") as f:
            f.write(img_data)
            print(f"    ↳ Downloaded: {os.path.basename(local_path)}")
    except Exception as e:
        print(f"    ↳ Error downloading {img_url}: {e}")


def normalize_url(url):
    """Normalizes URLs to ensure consistent matching, stripping off #fragments."""
    if url.startswith("/"):
        url = urljoin(BASE_URL, url)
    parsed = urlparse(url)

    # Strip params, query, and fragment to get the base page URL
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))

    # Ensure it ends with a slash for exact matching
    if not clean_url.endswith("/"):
        clean_url += "/"

    return clean_url, parsed.fragment


def download_local_images(content_div):
    """Finds all images, updates HTML, and downloads them in parallel."""
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER)

    download_tasks = []
    fallback_counter = 0

    for img in content_div.find_all("img"):
        original_src = img.get("data-src") or img.get("src")
        if not original_src:
            continue

        full_img_url = urljoin(BASE_URL, original_src)
        parsed_url = urlparse(full_img_url)
        img_filename = os.path.basename(parsed_url.path)

        # Fallback if URL has no clear filename
        if not img_filename:
            fallback_counter += 1
            img_filename = f"img_{int(time.time())}_{fallback_counter}.png"

        local_path = os.path.join(IMG_FOLDER, img_filename)

        # 1. Queue it up for the parallel downloader
        download_tasks.append((full_img_url, local_path))

        # 2. Instantly update the HTML DOM
        img["src"] = f"img/{img_filename}"
        if img.has_attr("data-src"):
            del img["data-src"]

    # 3. Execute all downloads in parallel using 5 worker threads
    if download_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks to the executor
            futures = [
                executor.submit(download_single_image, url, path)
                for url, path in download_tasks
            ]
            # Wait for all downloads in this lesson to finish before moving on
            concurrent.futures.wait(futures)


def scrape_lesson(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content_div = soup.find("div", class_="entry-content")
        if not content_div:
            return None, None

        next_url = None
        for link in soup.find_all("a", class_="nav-link"):
            if "next" in link.get_text(strip=True).lower():
                href = link.get("href")
                next_url = urljoin(BASE_URL, href) if href else None
                break

        download_local_images(content_div)

        unwanted = [
            "a.nav-link",
            ".nav-links",
            ".post-navigation",
            ".entry-navigation",
            ".prevnext",
            ".ezoic-ad",
            ".wpdiscuz-wrapper",
            ".sharedaddy",
            ".code-block",
        ]
        for sel in unwanted:
            for el in content_div.select(sel):
                el.decompose()

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Untitled"

        # We return the body as a string to be re-parsed in Phase 2
        return {"title": title, "body": str(content_div), "original_url": url}, next_url
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None


def wrap_and_nav(lesson, idx, total, all_lessons):
    """Wraps body in Material UI structure with a sticky sidebar."""

    # 1. Build the Sidebar HTML
    sidebar_items = []
    for i, l in enumerate(all_lessons):
        active_class = 'class="active"' if i == idx else ""
        sidebar_items.append(
            f'<li><a href="{l["filename"]}" {active_class}>{l["title"]}</a></li>'
        )

    sidebar_html = f"""
    <div class="sidebar">
        <h3>Lessons</h3>
        <ul>
            <li><a href="index.html">🏠 Home / Index</a></li>
            {"".join(sidebar_items)}
        </ul>
    </div>
    """

    prev_link = (
        f'<a href="lesson_{idx - 1}.html">← Previous</a>'
        if idx > 0
        else "<span></span>"
    )
    next_link = (
        f'<a href="lesson_{idx + 1}.html">Next →</a>'
        if idx < total - 1
        else "<span></span>"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{lesson["title"]}</title>
    <link rel="stylesheet" href="{CSS_FILENAME}">
    <link href="prism.css" rel="stylesheet" />
    <script>
        (function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        }})();

        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('theme', target);
        }}

        function cppSolutionToggle(e,l,s,h){{e.style.display=(e.style.display==='none'||e.style.display==='')?'block':'none';l.innerHTML=(e.style.display==='none')?s:h;}}
        function cppHintToggle(e,l,s,h){{cppSolutionToggle(e,l,s,h);}}
    </script>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">🌓</button>
    
    <div class="main-wrapper">
        {sidebar_html}
        
        <div class="content-container">
            <div class="entry-content">
                <h1>{lesson["title"]}</h1>
                {lesson["body"]}
                <div class="local-lesson-nav">{prev_link}<a href="index.html">📚 Index</a>{next_link}</div>
            </div>
        </div>
    </div>
    
    <script src="prism.js"></script>
</body>
</html>"""


def run_scraper():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    current_url = START_URL
    all_lessons = []

    # --- PHASE 0: Load Checkpoint ---
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_lessons = data.get("lessons", [])
                current_url = data.get("next_url", START_URL)
                print(
                    f"Checkpoint found! Loaded {len(all_lessons)} completely scraped lessons."
                )
                print(f"Resuming scrape at: {current_url}\n")
        except Exception as e:
            print(f"Error loading checkpoint: {e}. Starting fresh.")

    # --- PHASE 1: Scrape all pages into memory ---
    while current_url and len(all_lessons) < MAX_LESSONS:
        print(f"Scraping [{len(all_lessons) + 1}]: {current_url}")

        # If the script crashes inside scrape_lesson, the checkpoint remains untouched.
        # Next time it runs, it will load the exact same current_url.
        lesson_data, next_url = scrape_lesson(current_url)

        if lesson_data:
            all_lessons.append(lesson_data)

            # --- PHASE 1.5: Save Checkpoint ---
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "next_url": next_url,  # Save the URL for the NEXT lesson
                        "lessons": all_lessons,  # Save the completed lessons list
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            if lesson_data["title"].strip() == STOP_TITLE:
                print(f"Target reached: {STOP_TITLE}. Stopping crawl.")
                break

            current_url = next_url
            time.sleep(1.5)
        else:
            print("Stopping: No lesson data returned or End of course reached.")
            break

    print(f"\nProcessing internal links for {len(all_lessons)} lessons...")
    # --- PHASE 2a: Map original URLs to local filenames ---
    url_to_local_map = {}
    for i, lesson in enumerate(all_lessons):
        lesson["filename"] = f"lesson_{i}.html"
        clean_url, _ = normalize_url(lesson["original_url"])
        url_to_local_map[clean_url] = lesson["filename"]

    # --- PHASE 2b: Rewrite Links and Save Files ---
    for i, lesson in enumerate(all_lessons):
        soup = BeautifulSoup(lesson["body"], "html.parser")

        # Find all hyperlink tags
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            # Adding Prism.js functionality
            for pre in soup.find_all("pre"):
                code_content = pre.get_text()
                pre.string = ""  # Clear pre
                new_code_tag = soup.new_tag("code", attrs={"class": "language-cpp"})
                new_code_tag.string = code_content
                pre.append(new_code_tag)

            # Check if it's an internal LearnCPP link (or a relative link)
            if BASE_URL in href or href.startswith("/"):
                clean_target, fragment = normalize_url(href)

                if clean_target in url_to_local_map:
                    # Route to local file
                    new_href = url_to_local_map[clean_target]
                    if (
                        fragment
                    ):  # Preserve anchor jumps (e.g., lesson_5.html#chapter-1)
                        new_href += f"#{fragment}"
                    a_tag["href"] = new_href
                else:
                    # Route to Google Search
                    link_text = a_tag.get_text(strip=True)
                    if not link_text:
                        link_text = "C++"
                    # quote_plus turns "C++ pointers" into "C%2B%2B+pointers"
                    search_query = quote_plus(f"C++ {link_text}")
                    a_tag["href"] = f"https://www.google.com/search?q={search_query}"
                    a_tag["target"] = "_blank"  # Open searches in a new tab

        # Update the body with rewritten links
        lesson["body"] = str(soup)

        # Wrap and save to disk
        with open(
            os.path.join(OUTPUT_FOLDER, lesson["filename"]), "w", encoding="utf-8"
        ) as f:
            f.write(wrap_and_nav(lesson, i, len(all_lessons), all_lessons))

    # --- PHASE 3: Generate Index ---
    with open(os.path.join(OUTPUT_FOLDER, "index.html"), "w", encoding="utf-8") as f:
        list_items = "".join(
            [
                f'<li><a href="{l["filename"]}">{l["title"]}</a></li>'
                for l in all_lessons
            ]
        )
        f.write(f"""
        <html>
        <head>
            <link rel="stylesheet" href="{CSS_FILENAME}">
            <meta charset="UTF-8">
            <script>
                (function() {{
                    const savedTheme = localStorage.getItem('theme') || 'light';
                    document.documentElement.setAttribute('data-theme', savedTheme);
                }})();
                function toggleTheme() {{
                    const current = document.documentElement.getAttribute('data-theme');
                    const target = current === 'dark' ? 'light' : 'dark';
                    document.documentElement.setAttribute('data-theme', target);
                    localStorage.setItem('theme', target);
                }}
            </script>
        </head>
        <body>
            <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
            <div class="entry-content"><h1>Index</h1><ul>{list_items}</ul></div>
        </body>
        </html>""")

    print("✅ Done! Links are fully localized.")


if __name__ == "__main__":
    print("⚠️Project created for educational purposes only!")
    print("  Local copies shall not be redistributed as by owners wishes!")

    run_scraper()
