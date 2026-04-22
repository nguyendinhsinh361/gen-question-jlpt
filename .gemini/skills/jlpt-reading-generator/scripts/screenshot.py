#!/usr/bin/env python3
"""
Screenshot tool — crop sát content, không thừa khoảng trắng.
Usage:
    python3 screenshot.py --html <html_file> --png <output_png>
    python3 screenshot.py --html-dir <dir> --png-dir <dir>
"""
import argparse, asyncio, glob, os, sys

JS_MEASURE = """
    (() => {
        const c = document.querySelector('.container');
        if (!c) return null;
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
"""

async def capture(html_path, img_path):
    # Validate input
    if not os.path.exists(html_path):
        print(f"❌ ERROR: File not found: {html_path}", file=sys.stderr)
        return False

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 700, "height": 800})
            abs_path = os.path.abspath(html_path)
            print(f"📄 Loading: {html_path}")
            await page.goto(f"file://{abs_path}", wait_until="networkidle")
            await page.wait_for_timeout(1500)

            # Force white background
            await page.evaluate("""
                document.documentElement.style.cssText += 'background:#fff!important;';
                document.body.style.cssText += 'background:#fff!important;';
            """)

            # Measure content height
            clip = await page.evaluate(JS_MEASURE)
            if clip is None:
                print(f"❌ ERROR: No .container element found in {html_path}", file=sys.stderr)
                await page.close()
                await browser.close()
                return False

            print(f"📐 Measure 1: {clip['width']}x{clip['height']}px")

            # Resize viewport to fit content
            await page.set_viewport_size({"width": 700, "height": clip["height"] + 20})
            await page.wait_for_timeout(300)

            # Re-measure after resize
            clip = await page.evaluate(JS_MEASURE)
            print(f"📐 Measure 2: {clip['width']}x{clip['height']}px")

            # Ensure output directory exists
            os.makedirs(os.path.dirname(img_path) or '.', exist_ok=True)

            await page.screenshot(path=img_path, clip=clip)
            size_kb = os.path.getsize(img_path) // 1024
            print(f"✅ {img_path} — {clip['width']}x{clip['height']}px ({size_kb}KB)")
            await page.close()
        except Exception as e:
            print(f"❌ ERROR capturing {html_path}: {e}", file=sys.stderr)
            await browser.close()
            return False
        await browser.close()
    return True

def main():
    parser = argparse.ArgumentParser(description="Screenshot tool — crop sát content")
    parser.add_argument("--html", help="Single HTML file")
    parser.add_argument("--png", help="Output PNG path")
    parser.add_argument("--html-dir", help="Directory of HTML files")
    parser.add_argument("--png-dir", help="Output directory for PNGs")
    args = parser.parse_args()

    ok, fail = 0, 0
    if args.html and args.png:
        success = asyncio.run(capture(args.html, args.png))
        if success:
            ok += 1
        else:
            fail += 1
    elif args.html_dir and args.png_dir:
        os.makedirs(args.png_dir, exist_ok=True)
        files = sorted(glob.glob(os.path.join(args.html_dir, "*.html")))
        if not files:
            print(f"⚠️  No HTML files found in {args.html_dir}", file=sys.stderr)
            sys.exit(1)
        print(f"📂 Found {len(files)} HTML file(s) in {args.html_dir}\n")
        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            success = asyncio.run(capture(f, os.path.join(args.png_dir, f"{base}.png")))
            if success:
                ok += 1
            else:
                fail += 1
            print()  # blank line between files
        print(f"{'='*40}")
        print(f"Done: {ok} OK, {fail} FAILED out of {len(files)} files")
    else:
        parser.print_help()
        sys.exit(1)

    if fail > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
