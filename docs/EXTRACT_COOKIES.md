# How to Extract Udemy Cookies

This guide shows you how to extract your `access_token` and `client_id` from your browser's DevTools.

## Why Do I Need This?

Udemy requires authentication to download course videos. Instead of automating login (which triggers CAPTCHA), you manually extract credentials from your browser session.

## Prerequisites

- You must be logged into Udemy
- Use a modern browser (Chrome, Firefox, Edge, Safari)

---

## Method 1: Chrome DevTools (Recommended)

### Step 1: Log into Udemy

Open https://www.udemy.com and log in to your account.

### Step 2: Open DevTools

**Option A:** Press `F12` on your keyboard
**Option B:** Right-click anywhere → Select "Inspect"
**Option C:** Menu → More Tools → Developer Tools

### Step 3: Go to Network Tab

Click the **Network** tab at the top of DevTools.

### Step 4: Filter Requests

In the filter box, type: `api-2.0`

This will show only Udemy API requests.

### Step 5: Trigger an API Request

Click **"My Courses"** in the Udemy navigation bar (or refresh the page).

You should see several requests appear in the Network tab.

### Step 6: Find a Request

Look for a request that starts with:
- `subscribed-courses`
- `users/me`
- `contexts/me`

Click on it.

### Step 7: View Headers

Click the **Headers** tab (in the right panel).

Scroll down to **Request Headers** section.

### Step 8: Copy Access Token

Find the line that says:
```
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Copy everything AFTER "Bearer "** (the long string of characters)

This is your `UDEMY_ACCESS_TOKEN`.

### Step 9: Copy Client ID

Find the line that says:
```
x-udemy-client-id: abc123xyz...
```

**Copy the value** (everything after the colon and space)

This is your `UDEMY_CLIENT_ID`.

---

## Method 2: Firefox DevTools

The process is identical to Chrome:

1. Press `F12` to open DevTools
2. Go to **Network** tab
3. Filter by `api-2.0`
4. Navigate to "My Courses"
5. Click on a `subscribed-courses` request
6. View **Headers** tab
7. Copy `authorization` (after "Bearer ")
8. Copy `x-udemy-client-id`

---

## Method 3: Safari DevTools

### Enable Developer Tools (First Time Only)

1. Safari → Preferences → Advanced
2. Check "Show Develop menu in menu bar"

### Extract Cookies

1. Develop → Show Web Inspector (or `Cmd+Option+I`)
2. Go to **Network** tab
3. Follow same steps as Chrome

---

## Method 4: Edge DevTools

The process is identical to Chrome:

1. Press `F12` to open DevTools
2. Follow the same steps as Chrome method

---

## Using Your Credentials

### Create .env File

Create a file named `.env` in the project root:

```env
UDEMY_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3d3dy51ZGVteS5jb20iLCJpYXQiOjE3MzM...
UDEMY_CLIENT_ID=273f9db60e3f0e420023c2a31e6bf913
```

**Important:**
- Remove any quotes or extra spaces
- Each credential should be on one line
- No spaces around the `=` sign

### Test Your Credentials

Run the script:

```bash
python simple_downloader.py
```

If credentials are valid, you'll see:
```
✓ Token validation successful
✓ Found 42 enrolled courses
```

If invalid:
```
✗ Token invalid or expired
```

---

## Troubleshooting

### I Don't See "authorization" Header

**Cause:** You're looking at the wrong request

**Solution:**
- Make sure you filtered by `api-2.0`
- Look for requests to `users/me` or `subscribed-courses`
- Try refreshing the page after applying the filter
- Make sure you're on the "My Courses" page

### I See "Cookie: access_token=..."

**Cause:** You're looking at the Cookie header instead of Authorization

**Solution:**
- Scroll down to find `authorization: Bearer ...`
- The Bearer token is what you need (not the cookie)

### Token Works But Downloads Fail

**Cause:** Token is valid for API calls but may have expired for video downloads

**Solution:**
- Extract fresh credentials from browser
- Make sure you're using the same IP address as when you extracted cookies
- Wait a few minutes and try again (may be rate limiting)

### How Long Do Tokens Last?

Udemy access tokens typically expire after **24-48 hours** or when you log out.

When downloads start failing with "403" errors, extract fresh credentials.

### I Can't Find "x-udemy-client-id" Header

**Cause:** Not all requests include this header

**Solution:**
- Try different API requests (look for `users/me/subscribed-courses`)
- Refresh the page and check multiple requests
- If still not found, it may be in a different format - check for `client-id` or similar headers

### Screenshots Not Matching My Browser

**Cause:** Browser UI may look different

**Solution:**
- The core concept is the same across all browsers
- Look for Network tab → Filter → Request Headers
- The header names (`authorization`, `x-udemy-client-id`) are always the same

---

## Security Notes

- **Never share your access token** - it's like sharing your password
- **Don't commit .env to git** - it's already in .gitignore
- **Tokens expire** - extract fresh ones when needed
- **Use same IP** - extract cookies from same network you'll use for downloads

---

## Visual Reference

Here's what you're looking for in the Headers section:

```
Request Headers:
  accept: application/json, text/plain, */*
  accept-language: en-US,en;q=0.9
  authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  ← COPY THIS (after "Bearer ")
  ...
  x-udemy-authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  x-udemy-client-id: abc123xyz789...  ← COPY THIS
  ...
```

---

## Still Having Issues?

1. Check the main [README.md](../README.md) troubleshooting section
2. Make sure you're logged into Udemy
3. Try a different browser
4. Clear browser cache and log in again
5. Open a GitHub issue with details (but never share your actual tokens!)

---

## Alternative: Using Browser Extensions

Some users prefer using browser extensions to export cookies:

- **EditThisCookie** (Chrome)
- **Cookie Quick Manager** (Firefox)

These can export cookies in Netscape format, but you still need to identify the correct `access_token` and `client_id` values.
