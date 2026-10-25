"""Walk the 3-minute demo script in a real browser and fail on any console error.

Saves screenshots of every step to docs/report/img/ for the report and PPT.
Needs the stack running (make dev). Run: python tests/e2e/ui_demo.py [--base http://localhost:5173]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright

IMG = Path(__file__).resolve().parents[2] / "docs" / "report" / "img"
CHROME = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or shutil.which("chromium")


def shot(page: Page, name: str, full: bool = False) -> None:
    page.wait_for_timeout(350)  # let the 200 ms gauge reveal finish
    page.screenshot(path=str(IMG / f"{name}.png"), full_page=full)
    print(f"  ✓ {name}")


def message_steps(page: Page, base: str) -> None:
    page.goto(f"{base}/check")
    page.get_by_role("button", name="KYC block alert").click()
    expect(page.get_by_role("img", name="Risk score")).to_contain_text("High risk", timeout=10_000)
    expect(page.get_by_text("Dangerous", exact=True)).to_be_visible()
    shot(page, "01_fake_kyc_high_risk", full=True)

    page.get_by_role("button", name="Bank OTP (genuine)").click()
    expect(page.get_by_role("img", name="Risk score")).to_contain_text("Looks safe", timeout=10_000)
    shot(page, "02_genuine_otp_safe")

    page.get_by_role("button", name="Refund collect (Hinglish)").click()
    expect(page.get_by_text("PIN asked to receive money").first).to_be_visible(timeout=10_000)
    page.get_by_role("radio", name="हिन्दी").click()
    expect(page.get_by_text("पैसे पाने के लिए", exact=False).first).to_be_visible(timeout=10_000)
    shot(page, "03_hinglish_refund_hindi")
    page.get_by_role("radio", name="தமிழ்").click()
    expect(page.get_by_text("பணம் பெற", exact=False).first).to_be_visible(timeout=10_000)
    shot(page, "04_hinglish_refund_tamil")
    page.get_by_role("radio", name="English").click()


def transaction_steps(page: Page, base: str) -> None:
    page.goto(f"{base}/transactions?user=U003")
    page.get_by_role("row", name="SBI Refund Desk").click()
    drawer = page.get_by_role("dialog")
    expect(drawer).to_contain_text("Payee account is only 3 days old", timeout=10_000)
    shot(page, "05_u003_collect_drawer")
    drawer.get_by_role("button", name="Simulate paying this request").click()
    modal = page.get_by_role("alertdialog")
    expect(modal).to_contain_text("Pause before you pay")
    shot(page, "06_pause_before_you_pay")
    modal.get_by_role("button", name="Decline request").click()
    expect(page.get_by_role("status").filter(has_text="Request declined")).to_be_visible()
    page.keyboard.press("Escape")
    shot(page, "07_transaction_feed", full=True)


def report_and_learn(page: Page, base: str) -> None:
    page.goto(f"{base}/report")
    expect(page.get_by_role("rowheader", name="Verity (model + rules + floors)")).to_be_visible(timeout=10_000)
    shot(page, "08_model_report", full=True)
    page.goto(f"{base}/learn")
    page.get_by_role("button", name="It’s a scam").click()
    expect(page.get_by_text("Correct.")).to_be_visible(timeout=10_000)
    expect(page.get_by_text("Verity says")).to_be_visible(timeout=10_000)
    shot(page, "09_quiz")
    page.goto(base)
    shot(page, "00_home", full=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:5173")
    args = parser.parse_args()
    IMG.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME) if CHROME else p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        print("Demo script:")
        message_steps(page, args.base)
        transaction_steps(page, args.base)
        report_and_learn(page, args.base)
        mobile = browser.new_page(viewport={"width": 375, "height": 812}, device_scale_factor=2)
        mobile.goto(f"{args.base}/check?sample=fake-kyc")
        expect(mobile.get_by_role("img", name="Risk score")).to_contain_text("High risk", timeout=10_000)
        shot(mobile, "10_mobile_check", full=True)
        browser.close()
    if errors:
        print("Console errors:\n  " + "\n  ".join(errors))
        return 1
    print("Demo script passed with no console errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
