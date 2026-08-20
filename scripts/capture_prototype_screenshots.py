import asyncio
import os
import time
from playwright.async_api import async_playwright

ASSETS_DIR = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

async def capture_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})

        # 1. Capture NexTel Chat UI (/chat)
        page = await context.new_page()
        try:
            print("Navigating to /chat...")
            await page.goto("http://localhost:3000/chat", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(2)
            
            # Send a sample customer query if input is available
            input_box = await page.query_selector("input, textarea")
            if input_box:
                await input_box.fill("How do I upgrade my 5G unlimited roaming plan?")
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)
                
            chat_path = os.path.join(ASSETS_DIR, "prototype_chat_ui.png")
            await page.screenshot(path=chat_path)
            print(f"Captured: {chat_path}")
        except Exception as e:
            print(f"Error capturing /chat: {e}")
        finally:
            await page.close()

        # 2. Capture Admin Control Panel (/admin)
        page = await context.new_page()
        try:
            print("Navigating to /admin...")
            await page.goto("http://localhost:3000/admin", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(2)
            
            # Look for trigger or test injection buttons if any
            run_btn = await page.query_selector("button")
            if run_btn:
                try:
                    await run_btn.click()
                    await asyncio.sleep(1.5)
                except Exception:
                    pass
                    
            admin_path = os.path.join(ASSETS_DIR, "prototype_admin_ui.png")
            await page.screenshot(path=admin_path)
            print(f"Captured: {admin_path}")
        except Exception as e:
            print(f"Error capturing /admin: {e}")
        finally:
            await page.close()

        # 3. Capture Dark SOC Dashboard (/dashboard)
        page = await context.new_page()
        try:
            print("Navigating to /dashboard...")
            await page.goto("http://localhost:3000/dashboard", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(2)
            
            dashboard_path = os.path.join(ASSETS_DIR, "prototype_soc_dashboard.png")
            await page.screenshot(path=dashboard_path)
            print(f"Captured: {dashboard_path}")
        except Exception as e:
            print(f"Error capturing /dashboard: {e}")
        finally:
            await page.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
