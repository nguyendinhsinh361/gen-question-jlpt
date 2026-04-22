#!/usr/bin/env python3
"""
Screenshot tool — crop sát content, không thừa khoảng trắng.
Usage:
    python3 screenshot.py --html <html_file> --png <output_png>
    python3 screenshot.py --html-dir <dir> --png-dir <dir>
"""
import argparse, asyncio, glob, os

async def capture(html_path, img_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 700, "height": 800})
        await page.goto(f"file://{os.path.abspath(html_path)}", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        # Force white background
        await page.evaluate("""
            document.documentElement.style.cssText += 'background:#fff!important;';
            document.body.style.cssText += 'background:#fff!important;';
        """)
        # Đo content height thực (container stretch theo body → không dùng bounding_box)
        clip = await page.evaluate("""
            (() => {
                const c = document.querySelector('.container');
                const cRect = c.getBoundingClientRect();
                let maxBottom = cRect.top;
                for (const ch of c.children) {
                    const r = ch.getBoundingClientRect();
                    if (r.bottom > maxBottom) maxBottom = r.bottom;
                }
                return {
                    x: Math.round(cRect.left),
                    y: Math.round(cRect.top),
                    width: Math.round(cRect.width),
                    height: Math.ceil(maxBottom - cRect.top) + 8
                };
            })()
        """)
        # Resize viewport vừa content (tránh cắt cụt bài dài)
        await page.set_viewport_size({"width": 700, "height": clip["height"] + 20})
        await page.wait_for_timeout(300)
        # Re-measure sau resize
        clip = await page.evaluate("""
            (() => {
                const c = document.querySelector('.container');
                const cRect = c.getBoundingClientRect();
                let maxBottom = cRect.top;
                for (const ch of c.children) {
                    const r = ch.getBoundingClientRect();
                    if (r.bottom > maxBottom) maxBottom = r.bottom;
                }
                return {
                    x: Math.round(cRect.left),
                    y: Math.round(cRect.top),
                    width: Math.round(cRect.width),
                    height: Math.ceil(maxBottom - cRect.top) + 8
                };
            })()
        """)
        await page.screenshot(path=img_path, clip=clip)
        print(f"✅ {img_path} — {clip['width']}x{clip['height']}px")
        await page.close()
        await browser.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", help="Single HTML file")
    parser.add_argument("--png", help="Output PNG path")
    parser.add_argument("--html-dir", help="Directory of HTML files")
    parser.add_argument("--png-dir", help="Output directory for PNGs")
    args = parser.parse_args()

    if args.html and args.png:
        asyncio.run(capture(args.html, args.png))
    elif args.html_dir and args.png_dir:
        os.makedirs(args.png_dir, exist_ok=True)
        for f in sorted(glob.glob(os.path.join(args.html_dir, "*.html"))):
            base = os.path.splitext(os.path.basename(f))[0]
            asyncio.run(capture(f, os.path.join(args.png_dir, f"{base}.png")))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
