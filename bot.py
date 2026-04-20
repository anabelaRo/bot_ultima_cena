import asyncio
import requests
import os
from datetime import datetime
from playwright.async_api import async_playwright

# CONFIG
URLS = [
    "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-vinciano/151991",
    "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-visite-guidate-a-orario-fisso-in-inglese/238363"
]

TARGET_MONTH = 6  # Junio

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_HEARTBEAT = None


def send_heartbeat():
    global LAST_HEARTBEAT
    now = datetime.now()

    if LAST_HEARTBEAT is None or (now - LAST_HEARTBEAT).total_seconds() > 86400:
        send_telegram("🤖 Bot activo - sin disponibilidad aún")
        LAST_HEARTBEAT = now


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


async def check(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = await browser.new_page()

        print(f"Checking availability... {url}")

        await page.goto(url)
        await page.wait_for_timeout(2000)

        # aceptar cookies
        try:
            await page.get_by_role("button", name="I agree").click(timeout=3000)
        except:
            pass

        await page.wait_for_timeout(2000)

        # calcular clicks dinámicos
        current_month = datetime.now().month
        clicks_needed = TARGET_MONTH - current_month

        print("Mes actual:", current_month)
        print("Clicks necesarios:", clicks_needed)

        # hacer clicks hasta junio
        for _ in range(clicks_needed):
            await page.get_by_role("link", name="›").click()
            await page.wait_for_timeout(1000)

        # buscar días
        day4 = page.locator("li.day").get_by_text("4", exact=True)
        day5 = page.locator("li.day").get_by_text("5", exact=True)

        title4 = await day4.get_attribute("title")
        title5 = await day5.get_attribute("title")

        print("Day 4:", title4)
        print("Day 5:", title5)

        if title4 and "not available" not in title4.lower():
            message = f"🎟️ ENTRADAS DISPONIBLES 4 JUNIO\n🌐 {url}"
            print(message)
            send_telegram(message)

        if title5 and "not available" not in title5.lower():
            message = f"🎟️ ENTRADAS DISPONIBLES 5 JUNIO\n🌐 {url}"
            print(message)
            send_telegram(message)

        await browser.close()


async def main():
    print("🚀 Bot iniciado")

    while True:
        try:
            print("🔎 Ejecutando check...")
            await check()
            send_heartbeat()
            print("⏱ Esperando...")
        except Exception as e:
            print("❌ ERROR:", str(e))

        await asyncio.sleep(1500)

if __name__ == "__main__":
    asyncio.run(main())
        await asyncio.sleep(1500)


