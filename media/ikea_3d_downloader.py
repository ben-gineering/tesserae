#!/usr/bin/env python3
"""
IKEA 3D Model Downloader CLI

Downloads 3D models (GLB files) from IKEA product pages.
Requires: playwright (install with: pip install playwright)
Then run: playwright install
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright, Route
except ImportError:
    print("Error: playwright not installed.")
    print("Install with: pip install playwright")
    print("Then run: playwright install")
    sys.exit(1)


class IKEA3DDownloader:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.glb_urls: list[str] = []
        self.product_name = "ikea_product"
        self.product_color = ""
        self.product_id = ""

    def log(self, message: str):
        if self.verbose:
            print(f"[DEBUG] {message}")

    def extract_product_info(self, url: str, page_title: str) -> None:
        """Extract product name, color, and ID from URL or page title."""
        # Extract product ID from URL (e.g., .../hektar-wand-klemmspot-dunkelgrau-80215308/)
        id_match = re.search(r'-(\d{8})/?$', url)
        if id_match:
            self.product_id = id_match.group(1)
            self.log(f"Found product ID: {self.product_id}")

        # Extract name from page title (e.g., "HEKTAR Wand-/Klemmspot, dunkelgrau - IKEA")
        if page_title:
            title_clean = page_title.replace(" - IKEA", "").strip()
            parts = [p.strip() for p in title_clean.split(",")]
            if parts:
                self.product_name = parts[0]
            if len(parts) > 1:
                self.product_color = parts[1]
            self.log(f"Product name: {self.product_name}, Color: {self.product_color}")

    def get_safe_filename(self) -> str:
        """Generate a safe filename for the downloaded model."""
        filename = self.product_name
        if self.product_color:
            filename += f" - {self.product_color}"
        if self.product_id:
            filename += f" ({self.product_id})"
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        return filename + ".glb"

    def download(self, url: str, output_path: str | None = None) -> str | None:
        """
        Download the 3D model from an IKEA product page.

        Args:
            url: IKEA product page URL
            output_path: Optional output path. If not provided, uses product name.

        Returns:
            Path to downloaded file, or None if failed.
        """
        self.glb_urls = []

        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Intercept all network requests to find GLB files
            def handle_route(route: Route):
                request_url = route.request.url
                if ".glb" in request_url or "glb_draco" in request_url:
                    self.glb_urls.append(request_url)
                    self.log(f"Found GLB URL: {request_url}")
                route.continue_()

            page.route("**/*", handle_route)

            try:
                self.log(f"Navigating to: {url}")
                page.goto(url, wait_until="networkidle", timeout=60000)

                # Get page title for product info
                page_title = page.title()
                self.extract_product_info(url, page_title)

                # Wait a bit for any dynamic content to load
                page.wait_for_timeout(3000)

                # Try to click the "View in 3D" button if it exists to trigger model load
                try:
                    view_3d_button = page.query_selector(".pipf-xr-button, .pip-xr-button")
                    if view_3d_button:
                        self.log("Found View in 3D button, clicking to load model...")
                        view_3d_button.click()
                        page.wait_for_timeout(5000)  # Wait for model to load
                except Exception as e:
                    self.log(f"Could not click 3D button: {e}")

                # Also check for model-viewer elements
                model_viewers = page.query_selector_all("model-viewer")
                for mv in model_viewers:
                    src = mv.get_attribute("src")
                    if src and (".glb" in src or "glb_draco" in src):
                        self.glb_urls.append(src)
                        self.log(f"Found GLB from model-viewer: {src}")

                # Check inside iframes too
                frames = page.frames
                for frame in frames:
                    try:
                        model_viewers = frame.query_selector_all("model-viewer")
                        for mv in model_viewers:
                            src = mv.get_attribute("src")
                            if src and (".glb" in src or "glb_draco" in src):
                                self.glb_urls.append(src)
                                self.log(f"Found GLB from iframe model-viewer: {src}")
                    except Exception:
                        pass

            except Exception as e:
                print(f"Error loading page: {e}")
                return None
            finally:
                browser.close()

        if not self.glb_urls:
            print("No 3D model found on this product page.")
            print("This product may not have a 3D model available.")
            return None

        # Use the last (most recent) GLB URL, which is usually the highest quality
        glb_url = self.glb_urls[-1]
        print(f"Found 3D model: {glb_url}")

        # Determine output path
        if output_path:
            output = Path(output_path)
            if output.is_dir():
                output = output / self.get_safe_filename()
        else:
            output = Path(self.get_safe_filename())

        # Download the file
        print(f"Downloading to: {output}")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                response = page.request.get(glb_url)
                if response.ok:
                    buffer = response.body()
                    output.write_bytes(buffer)
                    print(f"Successfully downloaded: {output}")
                    return str(output)
                else:
                    print(f"Download failed with status: {response.status}")
                    return None
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Download 3D models from IKEA product pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.ikea.com/de/de/p/hektar-wand-klemmspot-dunkelgrau-80215308/
  %(prog)s -o my_model.glb https://www.ikea.com/us/en/p/billy-bookcase-white-00263850/
  %(prog)s -v https://www.ikea.com/fr/fr/p/...
        """
    )
    parser.add_argument("url", help="IKEA product page URL")
    parser.add_argument("-o", "--output", help="Output file path (default: product name.glb)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Validate URL
    parsed = urlparse(args.url)
    if not parsed.netloc.endswith("ikea.com"):
        print("Error: URL must be from ikea.com")
        sys.exit(1)

    downloader = IKEA3DDownloader(verbose=args.verbose)
    result = downloader.download(args.url, args.output)

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
