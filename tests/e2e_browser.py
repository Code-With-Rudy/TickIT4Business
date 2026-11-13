"""Browser end-to-end test (Playwright + in-memory Firestore). Run: python tests/e2e_browser.py
The QR CDN library is stubbed (no network in CI sandbox), so this checks UI flows, not real QR decoding."""
import os, sys, threading, time
src = open(os.path.join(os.path.dirname(__file__), "test_backend.py")).read()
exec(src.split('os.environ["JWT_SECRET"]')[0])          # fake firestore + stubbed firebase/limiter modules
os.environ["JWT_SECRET"] = "e2e"; os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = "{}"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
import main
from flask import send_from_directory
from werkzeug.serving import make_server
PUBLIC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
@main.app.route("/", defaults={"p": "index.html"})
@main.app.route("/<path:p>")
def static_files(p): return send_from_directory(PUBLIC, p)
srv = make_server("127.0.0.1", 8766, main.app, threaded=True)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:8766"

QR_STUB = """window.qrcode=function(){var d=[];return{addData:function(t){d.push(t)},make:function(){},getModuleCount:function(){return 25},
isDark:function(r,c){return (r*7+c*3+(d[0]||'').length)%3===0}}};"""

from playwright.sync_api import sync_playwright
fails = 0
def check(name, cond, extra=""):
    global fails
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if not cond else ""))
    fails += 0 if cond else 1

def new_page(b, scheme="light"):
    ctx = b.new_context(viewport={"width": 430, "height": 932}, color_scheme=scheme)
    pg = ctx.new_page()
    def route(r):
        u = r.request.url
        if u.startswith(BASE): return r.continue_()
        if "qrcode-generator" in u: return r.fulfill(body=QR_STUB, content_type="application/javascript")
        r.abort()
    pg.route("**/*", route)
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    return ctx, pg

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------------- owner signs up (the reported bug) ----------------
    octx, o = new_page(b)
    o.goto(BASE + "/index.html")
    o.click('.tab[data-arg="owner-register"]')
    f = "#ownerRegisterForm "
    check("owner sign-up has password + Create button", o.is_visible(f + "#ownerRegPassword") and o.is_visible(f + "button[type=submit]"))
    o.fill(f + "#ownerRegName", "Eco Owner"); o.fill(f + "#ownerRegEmail", "eco@park.com")
    o.fill(f + "#businessName", "Eco Park Entry1"); o.select_option(f + "#category", "park")
    o.fill(f + "#ownerRegPassword", "password123")
    o.click(f + "button[type=submit]")
    o.wait_for_selector("#ownerRegisterSuccess", state="visible")
    check("owner registered", any(d["businessName"] == "Eco Park Entry1" for d in fake_db.data.get("owners", {}).values()))
    o.wait_for_selector("#owner-login.active")
    o.fill("#ownerLoginForm input[name=email]", "eco@park.com"); o.fill("#ownerLoginForm input[name=password]", "password123")
    o.click("#ownerLoginForm button[type=submit]")
    o.wait_for_url("**/owner_dashboard.html")
    o.wait_for_selector('[data-click="openServiceForm"]')
    check("token in sessionStorage, not localStorage", o.evaluate("!!sessionStorage.getItem('tickit_token') && !localStorage.getItem('tickit_token')"))

    # ---------------- owner creates MULTIPLE services/IDs ----------------
    ids = []
    for name, price, validity in (("Adult Entry", "50", "1440"), ("Child Entry", "20", "1440"), ("Parking 2h", "30", "120")):
        o.click('button:has-text("Add service")')
        o.fill("#svcName", name); o.fill("#svcPrice", price); o.select_option("#svcValidity", validity)
        o.click("#svcSaveBtn")
        o.wait_for_selector("#shareModal.show")
        ids.append(o.inner_text("#shareId"))
        o.click('#shareModal button:has-text("Close")')
        o.wait_for_selector("#shareModal.show", state="hidden")
    check("3 services -> 3 different IDs", len(set(ids)) == 3 and all(main.SERVICE_ID_RE.match(i) for i in ids), ids)
    check("services listed", o.locator(".service-row").count() == 3)
    o.click('.service-row:first-child button:has-text("QR")')
    o.wait_for_selector("#shareModal.show")
    check("share link + whatsapp link", f"/book.html?s={ids[0]}" in o.inner_text("#shareLinkText") and "wa.me" in o.get_attribute("#shareWhatsapp", "href"))
    o.screenshot(path="/tmp/shots/owner_share_light.png")
    o.click('#shareModal button:has-text("Close")')
    # pause then resume
    o.click('.service-row:nth-child(3) button:has-text("Pause")')
    o.wait_for_selector('.service-row.paused')
    check("pause works", fake_db.data["services"][ids[2]]["active"] is False)
    o.click('.service-row.paused button:has-text("Resume")')
    o.wait_for_selector('.service-row.paused', state="detached")

    # ---------------- customer arrives from a shared link ----------------
    cctx, c = new_page(b, "dark")
    c.goto(f"{BASE}/book.html?s={ids[0]}")
    c.wait_for_selector("#serviceView", state="visible")
    check("public page shows service without login", c.text_content("#svcName") == "Adult Entry" and c.text_content("#svcPrice") == "50" and "Eco Park Entry1" in c.text_content("#svcBusiness"))
    c.screenshot(path="/tmp/shots/book_dark.png")
    c.click('a:has-text("Log in or sign up to buy")')
    c.wait_for_selector("#user-register.active")
    check("next= opens customer sign-up", "next=" in c.url)
    f = "#userRegisterForm "
    c.fill(f + "#userRegName", "Ann Cust"); c.fill(f + "#userRegEmail", "ann@x.com"); c.fill(f + "#userRegPassword", "password123")
    c.click(f + "button[type=submit]")
    c.wait_for_selector("#user-login.active")
    c.fill("#userLoginForm input[name=email]", "ann@x.com"); c.fill("#userLoginForm input[name=password]", "password123")
    c.click("#userLoginForm button[type=submit]")
    c.wait_for_url(f"**/book.html?s={ids[0]}")
    c.wait_for_selector("#payBtn")
    check("returned to the shared service after login", True)
    c.click('button[aria-label="More tickets"]')
    check("total updates for 2 tickets", "100" in c.inner_text(".total-row"))
    c.click("#payBtn")
    c.wait_for_selector("#successView", state="visible")
    code = c.inner_text("#okCode")
    check("ticket shown with QR + code", len(code) == 8 and c.locator("#okQr svg").count() == 1 and "2 people" in c.inner_text("#okQty"))
    check("wallet charged 100", [u for u in fake_db.data["users"].values() if u["email"] == "ann@x.com"][0]["walletBalance"] == 400)
    c.screenshot(path="/tmp/shots/ticket_dark.png")
    c.click('a:has-text("View my tickets")')
    c.wait_for_selector(".active-ticket-card")
    check("dashboard lists active ticket", "Adult Entry" in c.inner_text("#activeTickets"))
    c.fill("#serviceInput", ids[1].lower()); c.click('button:has-text("Open")')
    c.wait_for_url(f"**/book.html?s={ids[1]}")
    check("enter-by-ID opens booking page", True)

    # ---------------- owner validates at the gate ----------------
    o.fill("#manualCode", code.lower()); o.click('button:has-text("Validate")')
    o.wait_for_selector("#verifyResult", state="visible")
    check("gate: VALID - Redeemed, ADMIT 2", "VALID - Redeemed" in o.inner_text("#verifyTitle") and "ADMIT 2" in o.inner_text("#verifyAdmit"), o.inner_text("#verifyResult"))
    o.screenshot(path="/tmp/shots/verify_light.png")
    o.click('#verifyModal button:has-text("Close")')
    o.fill("#manualCode", code); o.click('button:has-text("Validate")')
    o.wait_for_function("document.getElementById('verifyTitle').textContent.includes('ALREADY')")
    check("gate: second scan ALREADY USED", True)
    o.click('#verifyModal button:has-text("Close")')
    c.goto(BASE + "/dashboard.html"); c.wait_for_selector("#ticketHistory .history-item")
    check("customer sees ticket as USED", "USED" in c.inner_text("#ticketHistory"))

    # ---------------- dark mode toggle persists ----------------
    o.click("#themeToggle")
    check("toggle -> dark", o.evaluate("document.documentElement.dataset.theme") == "dark")
    o.reload(); o.wait_for_selector(".service-row")
    check("dark persists after reload", o.evaluate("document.documentElement.dataset.theme") == "dark")
    o.screenshot(path="/tmp/shots/owner_dark.png")
    o.click("#themeToggle")
    check("toggle back -> light", o.evaluate("document.documentElement.dataset.theme") == "light")

    # ---------------- guards ----------------
    o.goto(BASE + "/dashboard.html"); o.wait_for_url("**/owner_dashboard.html")
    check("owner is bounced back to own dashboard", "owner_dashboard" in o.url)
    for pg in (o, c):
        real = [e for e in pg.errors if "firebase" not in e.lower() and "module" not in e.lower() and "Not signed in" not in e]
        check("no JS errors", not real, real)
    b.close()
print("\n%s" % ("E2E ALL PASSED" if not fails else f"{fails} E2E FAILED")); sys.exit(1 if fails else 0)
