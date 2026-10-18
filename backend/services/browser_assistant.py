"""
CPGRAMS Browser Assistant Service
Controlled browser automation using Playwright and installed system Chrome/Edge.
Assists authorized officer interaction, navigation, read-only visible record extraction,
and session expiry detection.
STRICT SECURITY POLICY: Never stores passwords, never bypasses CAPTCHA/MFA,
never performs write/disposal actions on the portal.
"""

import threading
import time
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from backend.config import (
    CPGRAMS_PORTAL_URL,
    CPGRAMS_OPERATIONAL_DESK_URL,
    CPGRAMS_SEARCH_URL,
    CPGRAMS_SEARCH_LIST_URL,
    get_installed_browser
)

class BrowserAssistantManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.last_sync_time = None
        self.last_error = None
        self._thread = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def launch_session(self) -> Dict[str, Any]:
        """
        Launches a visible browser session directed to the official CPGRAMS Officer Portal.
        The officer logs in themselves (username, password, CAPTCHA / Parichay).
        """
        if self.is_running and self.page and not self.page.is_closed():
            return {
                "status": "already_running",
                "current_url": self.page.url,
                "title": self.page.title()
            }

        browser_info = get_installed_browser()
        if not browser_info:
            raise RuntimeError("No supported browser (Google Chrome or Microsoft Edge) found on system.")

        try:
            self.playwright = sync_playwright().start()
            
            # Use installed channel (chrome or msedge)
            channel = browser_info["name"]
            self.browser = self.playwright.chromium.launch(
                channel=channel,
                headless=False,  # Must be visible for officer manual login & OTP
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )
            self.context = self.browser.new_context(no_viewport=True)
            self.page = self.context.new_page()
            
            # Navigate to CPGRAMS Login
            self.page.goto(CPGRAMS_PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
            self.is_running = True
            self.last_error = None

            return {
                "status": "launched",
                "browser": channel,
                "current_url": self.page.url,
                "title": self.page.title(),
                "instructions": "Official login page loaded. Please complete your authentication (credentials, CAPTCHA, or Parichay) directly in the browser window."
            }
        except Exception as e:
            self.last_error = str(e)
            self.close_session()
            raise RuntimeError(f"Failed to launch browser assistant: {e}")

    def get_session_status(self) -> Dict[str, Any]:
        """
        Detects current status of the browser session, active page URL, and session state.
        """
        if not self.is_running or not self.page or self.page.is_closed():
            return {
                "is_running": False,
                "state": "CLOSED",
                "current_url": None,
                "is_logged_in": False,
                "last_sync_time": self.last_sync_time,
                "last_error": self.last_error
            }

        try:
            url = self.page.url
            title = self.page.title()
            
            # Detect page state
            is_login_page = "login" in url.lower() or "/CPGOFFICE/" in url and not any(k in url.lower() for k in ["operationaldesk", "search", "report"])
            is_operational_desk = "operationaldesk" in url.lower()
            is_search_page = "search" in url.lower()
            
            # Check if session appears expired (e.g. redirected to login with timeout notice)
            is_session_expired = False
            if "session expired" in title.lower() or "timeout" in title.lower():
                is_session_expired = True

            is_logged_in = not is_login_page and not is_session_expired

            state_label = "LOGGED_IN" if is_logged_in else ("SESSION_EXPIRED" if is_session_expired else "AWAITING_OFFICER_LOGIN")
            if is_operational_desk:
                current_view = "Operational Desk"
            elif is_search_page:
                current_view = "Search / List"
            elif is_login_page:
                current_view = "Official Login Page"
            else:
                current_view = title

            return {
                "is_running": True,
                "state": state_label,
                "current_url": url,
                "title": title,
                "current_view": current_view,
                "is_logged_in": is_logged_in,
                "is_session_expired": is_session_expired,
                "last_sync_time": self.last_sync_time,
                "last_error": self.last_error
            }
        except Exception as e:
            return {
                "is_running": False,
                "state": "ERROR",
                "current_url": None,
                "is_logged_in": False,
                "last_error": str(e)
            }

    def navigate_to(self, destination: str) -> Dict[str, Any]:
        """Navigates to authorized portal sections."""
        if not self.is_running or not self.page or self.page.is_closed():
            raise RuntimeError("Browser session is not active. Please launch browser first.")

        target_map = {
            "operational_desk": CPGRAMS_OPERATIONAL_DESK_URL,
            "search": CPGRAMS_SEARCH_URL,
            "search_list": CPGRAMS_SEARCH_LIST_URL,
            "login": CPGRAMS_PORTAL_URL
        }
        url = target_map.get(destination)
        if not url:
            raise ValueError(f"Unknown destination: {destination}")

        self.page.goto(url, wait_until="domcontentloaded", timeout=25000)
        return {
            "destination": destination,
            "url": self.page.url,
            "title": self.page.title()
        }

    def inspect_visible_records(self) -> List[Dict[str, Any]]:
        """
        Safely inspects the active browser DOM to extract visible grievance records
        from the officer's current authorized view (Operational Desk or Search/List).
        Read-only extraction.
        """
        if not self.is_running or not self.page or self.page.is_closed():
            raise RuntimeError("Browser session is not active.")

        status = self.get_session_status()
        if not status["is_logged_in"]:
            raise RuntimeError("Officer is not logged in to CPGRAMS. Please sign in via the browser window first.")

        # JavaScript evaluation to find and extract tabular data safely from DOM
        js_extractor = """
        () => {
            const records = [];
            // Look for table rows in common grid/datatable selectors
            const tables = Array.from(document.querySelectorAll('table'));
            for (const table of tables) {
                const rows = Array.from(table.querySelectorAll('tbody tr'));
                if (rows.length === 0) continue;
                
                // Get header text
                const ths = Array.from(table.querySelectorAll('thead th, tr th')).map(th => th.innerText.trim().toLowerCase());
                
                for (const row of rows) {
                    const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                    if (cells.length < 3) continue;
                    
                    let reg_no = null;
                    let subject = null;
                    let applicant = null;
                    let date_rec = null;
                    let status = 'New';
                    
                    // Match by headers if available
                    cells.forEach((val, i) => {
                        const h = ths[i] || '';
                        if (val.match(/[A-Z0-9]{3,8}\\/[EOP]\\/[0-9]{4}\\/[0-9]{3,8}/i)) {
                            reg_no = val.match(/[A-Z0-9]{3,8}\\/[EOP]\\/[0-9]{4}\\/[0-9]{3,8}/i)[0];
                        } else if (h.includes('reg') || h.includes('number')) {
                            reg_no = val;
                        } else if (h.includes('subject') || h.includes('detail')) {
                            subject = val;
                        } else if (h.includes('name') || h.includes('complainant')) {
                            applicant = val;
                        } else if (h.includes('date') || h.includes('received')) {
                            date_rec = val;
                        } else if (h.includes('status')) {
                            status = val;
                        }
                    });

                    // Fallback heuristics if no matching headers
                    if (!reg_no) {
                        for (const c of cells) {
                            const m = c.match(/[A-Z0-9]{3,8}\\/[EOP]\\/[0-9]{4}\\/[0-9]{3,8}/i);
                            if (m) { reg_no = m[0]; break; }
                        }
                    }

                    if (reg_no) {
                        records.push({
                            registration_no: reg_no,
                            subject: subject || cells[2] || 'CPGRAMS Grievance',
                            applicant_name: applicant || cells[1] || 'Citizen',
                            date_received: date_rec || new Date().toISOString().split('T')[0],
                            status: status,
                            category: 'AI & Emerging Technologies',
                            raw_row: cells.join(' | ')
                        });
                    }
                }
            }
            return records;
        }
        """
        extracted = self.page.evaluate(js_extractor)
        self.last_sync_time = time.strftime("%Y-%m-%d %H:%M:%S")
        return extracted

    def close_session(self):
        """Safely closes the browser context and playwright instance."""
        try:
            if self.page and not self.page.is_closed():
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            self.is_running = False
