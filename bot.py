import asyncio
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# CONFIG
URL = "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-vinciano/151991"
TARGET_MONTH = 6  # Junio

TOKEN = "8773506897:AAHf__2fC3UteIHS8L9sWB7vCZAmNn4iLNU"
CHAT_ID = "1315605699"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        page = await browser.new_page()

        print("Checking availability...")

        await page.goto(URL)
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
            message = "🎟️ ENTRADAS DISPONIBLES 4 JUNIO "
            print(message)
            send_telegram(message)

        if title5 and "not available" not in title5.lower():
            message = "🎟️ ENTRADAS DISPONIBLES 5 JUNIO"
            print(message)
            send_telegram(message)

        await browser.close()


async def main():
    while True:
        try:
            await check()
        except Exception as e:
            print("Error:", e)

        print("Esperando 5 minutos...\n")
        await asyncio.sleep(300)


asyncio.run(main())