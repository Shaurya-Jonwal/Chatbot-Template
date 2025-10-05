import asyncio
from playwright.async_api import async_playwright

# Variables
model_name = "Chatbot"
UserDefaultName = "You"

# Introduction
def bot_introduction():
    print("-----------------------------")
    print(f"Welcome to {model_name}")
    print("-----------------------------")

bot_introduction()

# Function to fetch answer using headless browser
async def get_web_answer(query: str) -> str:
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go to Google search
            await page.goto(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            
            # Try to get Google Featured Snippet (text answer)
            selectors = [
                'div[data-attrid="wa:/description"] span',          # Direct snippet
                'div[data-attrid="kc:/people/person:description"] span', # Knowledge panel
                'div[data-attrid="kc:/common/topic:description"] span',
                'div[data-attrid="kc:/location/location:description"] span'
            ]
            for sel in selectors:
                try:
                    snippet = await page.locator(sel).text_content()
                    if snippet and snippet.strip():
                        await browser.close()
                        return snippet.strip()
                except:
                    continue
            
            # Fallback: first search result snippet
            try:
                first_snippet = await page.locator('div.IsZvec').first.text_content()
                first_snippet = first_snippet.strip() if first_snippet else None
                if first_snippet:
                    await browser.close()
                    return first_snippet
            except:
                pass
            
            # Fallback: first search result link
            try:
                first_result = await page.locator('div.yuRUbf a').first.get_attribute('href')
                await browser.close()
                if first_result:
                    return f"Here's the first link I found: {first_result}"
            except:
                pass
            
            await browser.close()
            return "Sorry, I couldn't find any information on that."
        
        except Exception as e:
            return f"Error occurred while fetching answer: {e}"

# Chat loop using synchronous input
async def GetResponseWithUser():
    loop = asyncio.get_event_loop()
    while True:
        userinput = await loop.run_in_executor(None, input, f"{UserDefaultName}: ")
        userinput = userinput.strip().lower()

        # Exit
        if userinput in ["bye", "exit", "quit"]:
            print(f"{model_name}: Bye! Have a great day 👋")
            await asyncio.sleep(1)
            break

        # Web search
        elif any(word in userinput for word in ["what", "who", "where", "when", "how"]):
            print(f"{model_name}: Let me search that for you...")
            result = await get_web_answer(userinput)
            print(f"{model_name}: {result}")

        # Greetings
        elif userinput in ["hi", "hello", "hey"]:
            print(f"{model_name}: Hey! What's up? What do you want?")

        # Default
        else:
            print(f"{model_name}: I'm not sure about that. Try asking me something else!")

if __name__ == "__main__":
    asyncio.run(GetResponseWithUser())