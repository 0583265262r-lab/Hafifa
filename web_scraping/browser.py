import json
import asyncio
import base64

from pathlib import Path
from playwright.async_api import async_playwright

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

def read_url(filePath):
    content = Path(filePath).read_text(encoding="utf-8")
    urls = []
    for line in content.splitlines():
        url = line.strip()

        if url:
            urls.append(url)
    return urls
def create_output_folders(urls):

    output_dir = Path("web_scraping/output")
    output_dir.mkdir(parents=True,exist_ok=True)

    folders = []

    for index,url in enumerate(urls, start=1):

        folder = output_dir / f"url_{index}"
        folder.mkdir(parents=True,exist_ok=True)

        folders.append(folder)
    return folders

       

async def browse_website(page,url,folder):

    resources = []

    def handle_request(request):
        resources.append(request.url)
    page.on("request",handle_request)

    await page.goto(url,
                    wait_until="domcontentloaded",
                    timeout=30000
                    )
    try:
        await page.wait_for_load_state(
            "load",
            timeout=10000
        )
    except PlaywrightTimeoutError:
        print(f"Load timeout for {url}, continuing...")

    html = await page.content()

    screenshot_path = folder / "screenshot.png"

    image_bytes = await page.screenshot(
        path=str(screenshot_path),
        full_page=True
    )
    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    data = {
        "html":html,
        "resources":resources,
        "screenshot":encoded_image
    }
    json_path = folder / "browse.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
async def process_website(browser,url,folder,semaphore):
    async with semaphore:
        page = await browser.new_page()
        try:
            await browse_website(page,url,folder)
        except Exception as error:
            print(f"Error processing {url}: {error}")
        finally:
            await page.close()
    

async def main():

    urls = (read_url("web_scraping/urls.input"))
    folders = create_output_folders(urls)

    if not urls:
        print("No Urls found")
        return
    semaphore = asyncio.Semaphore(5)

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(
            channel="chrome",
            headless=True
        )
        try:
            await asyncio.gather(
                *[
                    process_website(
                        browser,
                        url,
                        folder,
                        semaphore
                        )
                        for url,folder in zip(urls,folders)
                ]
            )
        finally:
            await browser.close()

        

asyncio.run(main())