import os
import re

MAIN_FILE = "./main.jsx"  # Adjust if it's main.js
I18N_IMPORTS = """import { I18nextProvider } from "react-i18next";
import i18n from "./i18n";"""

I18N_WRAPPER = """<I18nextProvider i18n={i18n}>
    <App />
   </I18nextProvider>"""

def modify_main_file():
    """Modifies main.tsx to include i18n imports and wrap App in I18nextProvider."""
    
    if not os.path.exists(MAIN_FILE):
        print("Error: main.tsx not found!")
        return

    with open(MAIN_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    # Add imports if not present
    if 'i18next' not in content:
        content = I18N_IMPORTS + "\n\n" + content

    # Wrap <App /> inside <I18nextProvider>
    if "<App />" in content and "I18nextProvider" not in content:
        content = re.sub(r"(<App\s*/>)", I18N_WRAPPER, content)

    with open(MAIN_FILE, "w", encoding="utf-8") as file:
        file.write(content)

    print("✅ main.tsx updated successfully!")

if __name__ == "__main__":
    modify_main_file()
