# Udemy Course Backup

A standalone Python tool to **backup your own purchased courses** from Udemy for personal offline viewing.

## ⚖️ Legal Disclaimer

**This tool is ONLY for backing up content you legally own or have purchased.**

- ✅ **Legal Use**: Downloading courses you paid for and own for personal backup
- ❌ **Illegal Use**: Downloading courses you don't own, sharing downloaded content, piracy

**By using this tool, you agree:**
1. You will ONLY download content you have legally purchased
2. You will NOT distribute, share, or republish downloaded content
3. You accept full legal responsibility for your use of this tool
4. The author bears NO responsibility for misuse

**Violating copyright law can result in severe civil and criminal penalties.**

---

## ⚠️ Important Limitations (as of 2025)

- **DRM-Protected Courses**: Udemy uses Widevine DRM on many courses. These CANNOT be downloaded (by design, for copyright protection)
- **Cloudflare Anti-Bot**: Some downloads may fail due to Udemy's anti-bot measures
- **Cookie Expiration**: You'll need to refresh your access token periodically (when downloads start failing)

This tool works best for:
- ✅ Older courses without DRM
- ✅ Free courses
- ✅ Courses with downloadable resources

**For DRM-protected courses**, use Udemy's official mobile app for offline viewing.

---

## ✨ Features

- 🔐 **Manual Cookie Authentication** - No browser automation, avoid CAPTCHA issues
- 📁 **Organized Structure** - Clean folder hierarchy by course/section/lecture
- ⏸️ **Resume Support** - Skips already downloaded videos
- 📝 **Subtitle Download** - Auto-downloads all available subtitles
- 🎥 **High Quality** - Downloads best available video quality
- 📊 **Course Metadata** - Saves course info to JSON for cataloging
- ⚠️ **DRM Detection** - Graceful handling of protected content
- 🔒 **Privacy First** - All processing happens locally

---

## 📋 Requirements

- **Python 3.12+**
- **ffmpeg** (for video merging/conversion)

---

## 🚀 Installation

### 1. Clone Repository

```bash
cd ~/c
git clone https://github.com/YOUR_USERNAME/udemy-course-backup.git
cd udemy-course-backup
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR: venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

---

## 🔑 Setup Authentication

### Extract Cookies from Browser (Required)

You need to extract your `access_token` and `client_id` from your browser while logged into Udemy.

**Quick Steps:**

1. **Open Udemy in your browser** and log in
2. **Open DevTools** (F12 or Right-click → Inspect)
3. **Go to Network tab**
4. **Filter by "api-2.0"** in the filter box
5. **Navigate to "My Courses"** on Udemy (or refresh the page)
6. **Click on a request** (e.g., `subscribed-courses` or `users/me`)
7. **Go to Headers tab** → Find "Request Headers" section
8. **Copy two values:**
   - `authorization: Bearer <TOKEN>` → Copy everything **after "Bearer "**
   - `x-udemy-client-id: <CLIENT_ID>` → Copy the value

**Detailed Guide:** See [docs/EXTRACT_COOKIES.md](docs/EXTRACT_COOKIES.md) for step-by-step instructions with screenshots.

### Create .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and paste your credentials:

```env
UDEMY_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
UDEMY_CLIENT_ID=abc123xyz789...
```

**Security:** Never commit this file to git! It's already in `.gitignore`.

---

## 🎯 Usage

### Run the Downloader

```bash
python simple_downloader.py
```

### Select Courses

You'll see a numbered list of your enrolled courses:

```
Your Enrolled Courses:
====================================

  1. The Complete Python Course
      Instructor: John Doe | Lectures: 150

  2. Web Development Bootcamp
      Instructor: Jane Smith | Lectures: 200

Enter course numbers (e.g., 1,3,5 or 'all'):
```

**Options:**
- Single course: `1`
- Multiple courses: `1,3,5`
- All courses: `all`

### Download Process

The tool will:
1. Fetch course curriculum
2. Create organized folder structure
3. Download videos + subtitles
4. Skip already downloaded files
5. Log failures to `failed_downloads.txt`

---

## 📂 Output Structure

```
downloads/
└── The Complete Python Course/
    ├── course_info.json
    ├── 01. Introduction/
    │   ├── 01. Welcome.mp4
    │   ├── 01. Welcome.en.vtt
    │   └── 02. Setup.mp4
    ├── 02. Python Basics/
    │   └── 01. Variables.mp4
    └── failed_downloads.txt  (if any failures)
```

---

## 🛠️ Troubleshooting

### "Authentication failed" Error

**Cause:** Token expired or invalid

**Solution:**
1. Delete `.udemy_token` file
2. Extract fresh cookies from browser (see Setup Authentication)
3. Update `.env` file
4. Run script again

### Many Downloads Failing with "DRM_PROTECTED"

**Cause:** Course uses encryption (Widevine DRM)

**Solution:** Unfortunately, there's no workaround. These videos cannot be downloaded due to copyright protection. Consider:
- Watching online
- Using Udemy's mobile app for offline viewing (official method)

### "403 Forbidden" Errors

**Cause:** Cloudflare anti-bot detection or token issues

**Solution:**
1. Refresh your access token (see above)
2. Try again with fresh cookies
3. Use same IP address as when you extracted cookies
4. Wait a few minutes and try again

### Token Expired Mid-Download

**Cause:** Udemy tokens typically expire after 24-48 hours

**Solution:**
1. Extract fresh cookies from browser
2. Update `.env` file
3. Run script again - it will resume (skip already downloaded files)

### Slow Downloads

**Cause:** Missing ffmpeg or network throttling

**Solution:**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check your internet connection
- Try downloading during off-peak hours

### "Can't find authorization header" in DevTools

**Cause:** Looking at the wrong request

**Solution:**
- Make sure you filtered by `api-2.0`
- Look for requests to `users/me` or `subscribed-courses`
- Try refreshing the page after applying the filter

---

## 🔒 Privacy & Security

- ✅ **No Data Sent to Third Parties** - All processing is local
- ✅ **Open Source** - You can inspect all code
- ⚠️ **Credential Security** - Keep `.env` file secure, never commit it
- ⚠️ **Token Expiration** - Access tokens expire; refresh periodically

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Code is used for **legal, personal backup only**
2. No features that enable piracy or content sharing
3. Maintain clear legal disclaimers

---

## 📜 License

MIT License - See LICENSE file

**Legal Reminder:** This license does NOT grant you rights to downloaded content. You must own/purchase content before downloading.

---

## ⚠️ Final Warning

**Copyright infringement is a serious crime.**

This tool is a **backup utility** for content you legally own. Misuse can result in:
- Civil lawsuits (damages up to $150,000 per work in the US)
- Criminal prosecution
- Account termination
- Legal fees

**Use responsibly. Download only what you own.**

---

## 🙋 Support

- 🐛 **Bug Reports**: Open a GitHub issue
- 💡 **Feature Requests**: Open a GitHub discussion
- 🚫 **Piracy Support**: Will be ignored/reported

---

**Made with care for legitimate course backup**

*Remember: Creators deserve to be paid for their work. Support them by purchasing content legally.*
