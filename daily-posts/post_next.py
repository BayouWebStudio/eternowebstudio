#!/usr/bin/env python3
"""Post next Eterno daily image to Instagram and Facebook.
Run once per day via cron. Tracks which post is next in a state file.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

# === CONFIG ===
ENV_PATH = "/Users/wescheclaw/.openclaw/workspace/.env"
STATE_PATH = "/Users/wescheclaw/.openclaw/workspace/eternowebstudio-new/daily-posts/.post_state.json"
BASE_URL = "https://raw.githubusercontent.com/BayouWebStudio/eternowebstudio/main/daily-posts"

# Post schedule in order
POSTS = [
    {
        "file": "eterno-01-A-marker-manifesto.png",
        "caption": "YR ART, ONLINE, FOREVER. ⚡\n\nWebsite + portfolio + booking — all in one. No credit card. No catch.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-04-A-crossed-out-phone.png",
        "caption": "243 unread DMs. Sound familiar? 😤\n\nStop running your shop out of the DMs. Get a real booking form.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-05-A-checklist.png",
        "caption": "A website that looks like your work. 🖤\n\n5 pages. Custom layout. Built from your IG. Not a template. Not Squarespace.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-02-B-pinned-polaroids.png",
        "caption": "REAL SITES. REAL TATTOOERS. 🔥\n\nFrank Vortex. Golden Soul. Venus Balam. + 14 more.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-06-A-scattered-polaroids.png",
        "caption": "Your IG, but it doesn't disappear. 📸\n\nEvery piece of flash, every healed photo — archived the way they deserve. Auto-synced from your IG.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-04-B-not-a-receptionist.png",
        "caption": "You are a tattooer. Not a receptionist. 💀\n\nOne form. Done. No back-and-forth. Style, placement, budget, refs — everything you need in one go.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-07-A-form-checklist.png",
        "caption": "Inquiries, without the chaos. ✅\n\nWhat style? Where? How big? Budget? Refs? Availability? — All in one form. No more chasing DMs.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-09-B-stat-cards.png",
        "caption": "15 DMs → 1. 2 days → 10 min. Always missing info → Never. 📊\n\nStop the friction. Start the booking.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-08-A-hand-drawn-calendar.png",
        "caption": "Your calendar. Your rules. 🗓️\n\nOpen. Booked. Off. Set it once and forget it.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-06-B-flash-healed-sessions.png",
        "caption": "Flash. Healed pieces. Every session. 🔄\n\nArchived the way they deserve — not buried in an IG feed. Auto-synced from your IG.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-08-B-block-confirm-repeat.png",
        "caption": "BLOCK. CONFIRM. REPEAT. 📅\n\nMaya · Fine Line · Forearm — BOOKED. That's how clean it should be.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-03-A-big-numeral.png",
        "caption": "17 tattooers on the roster. 🔥\n\nReal shops. Real clients. Real bookings. You're next.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
    {
        "file": "eterno-10-A-0-00-receipt.png",
        "caption": "Alright, here's the deal. 💰\n\nWebsite — free. Portfolio — free. Booking — free. Scheduling — free. 5 pages — free. Total: $0.00. No CC. No contracts.\n\n👉 eternowebstudio.com\n\n#eternowebstudio #tattooartist #webdesign #houston #smallbusiness"
    },
]

# === LOAD CREDENTIALS ===
with open(ENV_PATH) as f:
    env = f.read()

def get_env(name):
    m = re.search(rf'{name}=(\S+)', env)
    return m.group(1) if m else None

PAGE_TOKEN = get_env('GETMINTED_PAGE_TOKEN')
IG_ID = get_env('GETMINTED_IG_ID')
FB_PAGE_ID = get_env('GETMINTED_PAGE_ID')

if not all([PAGE_TOKEN, IG_ID, FB_PAGE_ID]):
    print("ERROR: Missing credentials in .env")
    sys.exit(1)

IG_BASE = f"https://graph.facebook.com/v20.0/{IG_ID}"
FB_BASE = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}"

# === STATE MANAGEMENT ===
def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"next_index": 0}

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

# === GET NEXT POST ===
state = load_state()
idx = state["next_index"] % len(POSTS)
post = POSTS[idx]
print(f"Posting #{idx+1}/{len(POSTS)}: {post['file']}")

image_url = f"{BASE_URL}/{post['file']}"
caption = post["caption"]

# === VERIFY IMAGE URL ===
try:
    req = urllib.request.Request(image_url, method='HEAD')
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"Image accessible: {resp.status} ({int(resp.headers.get('Content-Length',0))/1024:.0f}KB)")
except Exception as e:
    print(f"ERROR: Cannot reach image URL: {e}")
    sys.exit(1)

# === POST TO INSTAGRAM ===
print("\n=== INSTAGRAM ===")
payload = json.dumps({
    "image_url": image_url,
    "caption": caption,
    "access_token": PAGE_TOKEN,
}).encode()

req = urllib.request.Request(f"{IG_BASE}/media", data=payload,
    headers={"Content-Type": "application/json"}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        container_id = data['id']
        print(f"Container: {container_id}")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"IG container error: {e.code} — {err[:300]}")
    sys.exit(1)

# Wait for processing
print("Processing...")
for attempt in range(12):
    time.sleep(5)
    check_url = f"{IG_BASE}/media?fields=status_code&access_token={PAGE_TOKEN}"
    # Check specific container
    check_url2 = f"https://graph.facebook.com/v20.0/{container_id}?fields=status_code&access_token={PAGE_TOKEN}"
    req = urllib.request.Request(check_url2)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            sd = json.loads(resp.read())
            status = sd.get('status_code', 'UNKNOWN')
            print(f"  {attempt*5}s: {status}")
            if status == 'FINISHED':
                break
            elif status == 'ERROR':
                print(f"IG processing error: {sd}")
                sys.exit(1)
    except Exception as e:
        print(f"  Check error: {e}")

# Publish
payload2 = json.dumps({
    "creation_id": container_id,
    "access_token": PAGE_TOKEN,
}).encode()

req2 = urllib.request.Request(f"{IG_BASE}/media_publish", data=payload2,
    headers={"Content-Type": "application/json"}, method='POST')
try:
    with urllib.request.urlopen(req2, timeout=30) as resp2:
        ig_result = json.loads(resp2.read())
        ig_post_id = ig_result['id']
        print(f"IG Post ID: {ig_post_id}")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"IG publish error: {e.code} — {err[:300]}")
    ig_post_id = None

# === POST TO FACEBOOK ===
print("\n=== FACEBOOK ===")
fb_payload = urllib.parse.urlencode({
    'url': image_url,
    'message': caption,
    'access_token': PAGE_TOKEN,
}).encode()

fb_req = urllib.request.Request(f"{FB_BASE}/photos", data=fb_payload, method='POST')
try:
    with urllib.request.urlopen(fb_req, timeout=30) as resp:
        fb_data = json.loads(resp.read())
        fb_post_id = fb_data['id']
        print(f"FB Post ID: {fb_post_id}")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"FB error: {e.code} — {err[:300]}")
    fb_post_id = None

# === UPDATE STATE ===
state["next_index"] = idx + 1
state["last_post"] = {
    "index": idx,
    "file": post["file"],
    "ig_id": ig_post_id,
    "fb_id": fb_post_id,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
}
save_state(state)

print(f"\n✅ Done! Posted #{idx+1}: {post['file']}")
print(f"   IG: {ig_post_id}")
print(f"   FB: {fb_post_id}")
print(f"   Next up: #{(idx+1) % len(POSTS) + 1}: {POSTS[(idx+1) % len(POSTS)]['file']}")
