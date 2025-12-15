#!/usr/bin/env python3
"""
Simple Udemy Course Downloader
For downloading content you own/purchased on Udemy
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yt_dlp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============= AUTHENTICATION =============

def load_credentials() -> Tuple[str, str]:
    """Load access_token and client_id from .env file or cache"""
    token_cache = Path(".udemy_token")

    # Try cache first
    if token_cache.exists():
        try:
            data = json.loads(token_cache.read_text())
            access_token = data.get("access_token")
            client_id = data.get("client_id")

            if access_token and client_id:
                logging.info("Found cached credentials, validating...")
                if validate_token(access_token, client_id):
                    return access_token, client_id
                else:
                    logging.info("Cached credentials expired")
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")

    # Load from .env
    load_dotenv()
    access_token = os.getenv("UDEMY_ACCESS_TOKEN")
    client_id = os.getenv("UDEMY_CLIENT_ID")

    if not access_token or not client_id:
        logging.error("\n⚠️  Credentials not found!")
        logging.error("Please create a .env file with:")
        logging.error("  UDEMY_ACCESS_TOKEN=your_token_here")
        logging.error("  UDEMY_CLIENT_ID=your_client_id_here")
        logging.error("\nSee docs/EXTRACT_COOKIES.md for instructions.")
        sys.exit(1)

    logging.info("Validating credentials from .env...")
    if validate_token(access_token, client_id):
        # Save to cache
        save_token_cache(access_token, client_id)
        return access_token, client_id
    else:
        logging.error("✗ Invalid credentials. Please refresh your access_token.")
        logging.error("See docs/EXTRACT_COOKIES.md for instructions.")
        sys.exit(1)


def validate_token(access_token: str, client_id: str) -> bool:
    """Test if credentials are valid by calling Udemy API"""
    url = "https://www.udemy.com/api-2.0/contexts/me/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Udemy-Bearer-Token": access_token,
        "X-Udemy-Client-Id": client_id,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.udemy.com",
        "Referer": "https://www.udemy.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            logging.info("✓ Token validation successful")
            return True
        elif response.status_code in [401, 403]:
            logging.error("✗ Token invalid or expired")
            return False
        else:
            logging.warning(f"Unexpected status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Token validation failed: {e}")
        return False


def save_token_cache(access_token: str, client_id: str):
    """Save validated credentials to .udemy_token file"""
    token_cache = Path(".udemy_token")
    try:
        token_cache.write_text(json.dumps({
            "access_token": access_token,
            "client_id": client_id
        }))
        logging.info("✓ Credentials cached for future use")
    except Exception as e:
        logging.warning(f"Failed to save cache: {e}")


# ============= API INTERACTION =============

def create_session(access_token: str, client_id: str) -> requests.Session:
    """Create authenticated session for Udemy API calls"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "X-Udemy-Bearer-Token": access_token,
        "X-Udemy-Client-Id": client_id,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.udemy.com",
        "Referer": "https://www.udemy.com/",
    })
    return session


def fetch_enrolled_courses(session: requests.Session) -> List[Dict]:
    """Fetch all enrolled courses"""
    courses = []
    page = 1
    page_size = 100

    logging.info("Fetching your courses...")

    while True:
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses/"
        params = {
            "page": page,
            "page_size": page_size,
            "fields[course]": "id,title,url,visible_instructors,num_lectures,content_info"
        }

        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch courses: {e}")
            break

        data = response.json()
        results = data.get("results", [])

        for course in results:
            courses.append({
                "id": course["id"],
                "title": course["title"],
                "url": course["url"],
                "num_lectures": course.get("num_lectures", 0),
                "instructors": [i["title"] for i in course.get("visible_instructors", [])]
            })

        # Check for more pages
        if not data.get("next"):
            break
        page += 1

    logging.info(f"✓ Found {len(courses)} enrolled courses")
    return courses


def fetch_course_curriculum(session: requests.Session, course_id: int) -> Dict:
    """Fetch detailed curriculum for a course"""
    url = f"https://www.udemy.com/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items/"
    params = {
        "page_size": 1000,
        "fields[lecture]": "title,object_index,asset",
        "fields[chapter]": "title,object_index",
        "fields[asset]": "asset_type,stream_urls"
    }

    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch curriculum: {e}")
        return {}

    data = response.json()
    results = data.get("results", [])

    # Parse curriculum structure
    sections = []
    current_section = None

    for item in results:
        item_type = item.get("_class")

        if item_type == "chapter":
            # New section
            if current_section:
                sections.append(current_section)
            current_section = {
                "title": item.get("title", "Untitled Section"),
                "index": item.get("object_index", 0),
                "lectures": []
            }
        elif item_type == "lecture" and current_section:
            # Lecture in current section
            asset = item.get("asset", {})
            asset_type = asset.get("asset_type", "")

            if asset_type == "Video":
                current_section["lectures"].append({
                    "id": item.get("id"),
                    "title": item.get("title", "Untitled"),
                    "index": item.get("object_index", 0)
                })

    # Add last section
    if current_section:
        sections.append(current_section)

    return {"sections": sections}


def save_course_metadata(course: Dict, curriculum: Dict, output_dir: Path):
    """Save course metadata to course_info.json"""
    metadata = {
        "id": course["id"],
        "title": course["title"],
        "url": course["url"],
        "instructors": course.get("instructors", []),
        "num_lectures": course.get("num_lectures", 0),
        "num_sections": len(curriculum.get("sections", [])),
        "download_date": datetime.now().isoformat()
    }

    metadata_file = output_dir / "course_info.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))


# ============= DOWNLOAD LOGIC =============

def create_cookies_file(access_token: str, client_id: str) -> Path:
    """Create Netscape-format cookies.txt for yt-dlp"""
    cookies_path = Path(".udemy_cookies.txt")

    # Netscape HTTP Cookie File format
    content = f"""# Netscape HTTP Cookie File
.udemy.com\tTRUE\t/\tTRUE\t2147483647\taccess_token\t{access_token}
.udemy.com\tTRUE\t/\tTRUE\t2147483647\tclient_id\t{client_id}
"""

    cookies_path.write_text(content)
    return cookies_path


def classify_error(error_msg: str) -> str:
    """Classify error type for better logging"""
    error_lower = error_msg.lower()

    if "widevine" in error_lower or "drm" in error_lower:
        return "DRM_PROTECTED"
    elif "403" in error_msg or "forbidden" in error_lower:
        return "AUTH_FAILURE_403"
    elif "401" in error_msg or "unauthorized" in error_lower:
        return "AUTH_FAILURE_401"
    elif "timeout" in error_lower:
        return "NETWORK_TIMEOUT"
    elif "connection" in error_lower:
        return "NETWORK_ERROR"
    elif "not available" in error_lower:
        return "VIDEO_UNAVAILABLE"
    else:
        return "UNKNOWN_ERROR"


def log_failed_download(
    failed_log: Path,
    course_title: str,
    section_title: str,
    lecture_title: str,
    error_type: str,
    error_msg: str
):
    """Append failed download to log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = (
        f"{timestamp} | {error_type} | "
        f"{course_title} > {section_title} > {lecture_title}\n"
        f"  Error: {error_msg}\n\n"
    )

    # Append to log
    with failed_log.open('a', encoding='utf-8') as f:
        f.write(log_entry)


def download_lecture_video(
    lecture_url: str,
    output_path: Path,
    cookies_file: Path,
    failed_log: Optional[Path] = None,
    course_title: str = "",
    section_title: str = "",
    lecture_title: str = ""
) -> bool:
    """Download a single lecture using yt-dlp"""

    logging.info(f"  ↓ Downloading: {lecture_title}")

    ydl_opts = {
        'outtmpl': str(output_path.with_suffix('')),  # yt-dlp adds extension
        'cookies': str(cookies_file),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['all'],
        'http_headers': {
            'Referer': 'https://www.udemy.com/',
            'Origin': 'https://www.udemy.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        },
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([lecture_url])

        logging.info("    ✓ Download complete")
        return True

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        error_type = classify_error(error_msg)

        logging.error(f"    ✗ Download failed: {error_type}")

        if failed_log:
            log_failed_download(
                failed_log, course_title, section_title,
                lecture_title, error_type, error_msg
            )

        return False

    except Exception as e:
        error_msg = str(e)
        logging.error(f"    ✗ Unexpected error: {error_msg}")

        if failed_log:
            log_failed_download(
                failed_log, course_title, section_title,
                lecture_title, "UNKNOWN_ERROR", error_msg
            )

        return False


# ============= UI & USER INTERACTION =============

def display_courses(courses: List[Dict]):
    """Display numbered list of enrolled courses"""
    print("\n" + "="*60)
    print("Your Enrolled Courses:")
    print("="*60 + "\n")

    for i, course in enumerate(courses, 1):
        instructors = ", ".join(course.get("instructors", ["Unknown"]))
        print(f"{i:3d}. {course['title']}")
        print(f"      Instructor: {instructors} | Lectures: {course['num_lectures']}")
        print()


def get_user_selection(courses: List[Dict]) -> List[Dict]:
    """Get user's course selection"""
    while True:
        choice = input("\nEnter course numbers (e.g., 1,3,5 or 'all'): ").strip()

        if choice.lower() == 'all':
            return courses

        try:
            # Parse comma-separated numbers
            indices = [int(x.strip()) for x in choice.split(',')]

            # Validate range
            if all(1 <= i <= len(courses) for i in indices):
                selected = [courses[i - 1] for i in indices]

                # Confirm selection
                print(f"\nYou selected {len(selected)} course(s):")
                for course in selected:
                    print(f"  - {course['title']}")

                confirm = input("\nProceed with download? (y/n): ").strip().lower()
                if confirm == 'y':
                    return selected
            else:
                print("Error: Invalid course number(s)")
        except ValueError:
            print("Error: Invalid input format. Use numbers separated by commas (e.g., 1,3,5)")


# ============= FILE MANAGEMENT =============

def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Clean filename for filesystem"""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Limit length
    if len(name) > max_length:
        name = name[:max_length]
    return name.strip()


# ============= MAIN EXECUTION =============

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("Udemy Course Downloader")
    print("="*60 + "\n")

    # Load and validate credentials
    access_token, client_id = load_credentials()

    # Create authenticated session
    session = create_session(access_token, client_id)

    # Fetch enrolled courses
    courses = fetch_enrolled_courses(session)

    if not courses:
        logging.error("No enrolled courses found")
        return

    # Display courses and get user selection
    display_courses(courses)
    selected_courses = get_user_selection(courses)

    # Create cookies file for yt-dlp
    cookies_file = create_cookies_file(access_token, client_id)

    # Download each selected course
    for course in selected_courses:
        print(f"\n{'='*60}")
        print(f"Processing: {course['title']}")
        print(f"{'='*60}\n")

        # Fetch curriculum
        curriculum = fetch_course_curriculum(session, course['id'])
        sections = curriculum.get("sections", [])

        if not sections:
            logging.warning("No sections found for this course")
            continue

        # Create course directory
        course_dir = Path("downloads") / sanitize_filename(course['title'])
        course_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        save_course_metadata(course, curriculum, course_dir)

        # Failed downloads log
        failed_log = course_dir / "failed_downloads.txt"

        # Statistics
        total_lectures = 0
        downloaded = 0
        skipped = 0
        failed = 0

        # Download lectures
        for section in sections:
            print(f"\nSection {section['index']}: {section['title']}")

            section_dir = course_dir / f"{section['index']:02d}. {sanitize_filename(section['title'])}"
            section_dir.mkdir(parents=True, exist_ok=True)

            for lecture in section['lectures']:
                total_lectures += 1

                # Build lecture URL
                # Extract course slug from URL
                course_slug = course['url'].split('/')[-2] if '/' in course['url'] else str(course['id'])
                lecture_url = f"https://www.udemy.com/course/{course_slug}/learn/lecture/{lecture['id']}"

                # Output filename
                output_file = section_dir / f"{lecture['index']:02d}. {sanitize_filename(lecture['title'])}.mp4"

                # Check if already exists
                if output_file.exists():
                    print(f"    ⊙ Already exists: {output_file.name}")
                    skipped += 1
                    continue

                # Download
                success = download_lecture_video(
                    lecture_url,
                    output_file,
                    cookies_file,
                    failed_log,
                    course['title'],
                    section['title'],
                    lecture['title']
                )

                if success:
                    downloaded += 1
                else:
                    failed += 1

                # Small delay to avoid rate limiting
                time.sleep(0.5)

        # Display summary for this course
        print(f"\n{'='*60}")
        print(f"Course Summary: {course['title']}")
        print(f"{'='*60}")
        print(f"Total lectures: {total_lectures}")
        print(f"✓ Downloaded:   {downloaded}")
        print(f"⊙ Skipped:      {skipped} (already exist)")
        print(f"✗ Failed:       {failed}")

        if failed > 0 and failed_log.exists():
            print(f"\nFailed downloads logged to: {failed_log}")

    # Cleanup
    if cookies_file.exists():
        cookies_file.unlink()

    print("\n" + "="*60)
    print("✓ All downloads complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
