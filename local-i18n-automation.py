import os
import json
import re
import argparse
from typing import Dict, Tuple, List, Any, Optional
import asyncio
import aiofiles

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

    


class I18nExtractor:
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model_name = model_name
        self.chat = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name
        )

    # Extract translatable strings and update code using LLM
    async def process_file(self, file_path: str, framework: str = "React") -> Tuple[str, Dict[str, str]]:
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                code = await f.read()
            
            print(f"Processing {file_path} ({len(code)} characters)")
            
            extraction_prompt = f"""
            You are an internationalization assistant for a {framework} project.
            Extract all user-facing text such as headers, titles, button text, paragraphs from the following code.
            Replace them with t('key') from {'react-i18next' if framework == 'React' else 'next-i18next'}, and import useTranslation from 'react-i18next'; 

            Here is the code to process:

            ```jsx
            {code}
            ```

            RESPONSE FORMAT:
            Your response must be valid JSON with exactly these two fields:
            {{
                "updated_code": "// The complete modified code with t() functions",
                "i18n_json": {{
                    "key1": "Original text 1",
                    "key2": "Original text 2"
                }}
            }}

            IMPORTANT RULES:
            1. The output must be VALID JSON - no comments, no trailing commas.
            2. The "updated_code" must be the COMPLETE code, not just excerpts. Do not comment any parts of the code, and it must be without syntax errors such as unclosed brackets or parentheses ...
            3. The "i18n_json" field must have ALL extracted strings.
            4. Create logical keys based on the content (e.g., "welcomeMessage", "submitButton").
            5. Process only human-readable text inside JSX, alt attributes, and aria-labels.
            6. DO NOT modify dynamic expressions, component props, or JavaScript code.
            7. Make sure to properly escape quotes in the JSON output.
            8. Use DOUBLE QUOTES in the JSON response, not single quotes.

            YOUR RESPONSE MUST CONTAIN ONLY THE JSON OBJECT - NO EXPLANATIONS OR MARKDOWN FORMATTING.
            """

            # Try up to 3 times with backoff
            max_attempts = 3
            backoff_factor = 2
            
            for attempt in range(max_attempts):
                try:
                    response = await self.invoke_model(extraction_prompt)
                    json_data = self.extract_valid_json(response)
                    
                    if json_data and "updated_code" in json_data and "i18n_json" in json_data:
                        updated_code, i18n_json = json_data["updated_code"], json_data["i18n_json"]
                        
                        # Validate the JSON structure
                        if not isinstance(i18n_json, dict):
                            raise ValueError("i18n_json is not a dictionary")
                        
                        # Write the updated code back to the file
                        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                            await f.write(updated_code)
                        
                        return updated_code, i18n_json
                        
                    else:
                        print(f"Attempt {attempt+1}: Invalid JSON response. Retrying...")
                        await asyncio.sleep(backoff_factor ** attempt)
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {e}")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_factor ** attempt)
                    else:
                        raise
                        
            print("All attempts failed. Returning original code.")
            return code, {"error": "Failed to extract valid JSON after multiple attempts"}

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return code, {"error": str(e)}

    # Translate extracted strings to target language
    async def translate_strings(self, strings: Dict[str, str], language: str) -> Dict[str, str]:
        translation_prompt = f"""
        You are a translation assistant. Translate the following JSON key-value pairs into {language}.
        Return only the translated JSON in the exact same format as the input. Do not add any extra text or explanations.
        Ensure your response is valid JSON that can be parsed with JSON.parse() or equivalent.

        Input JSON:
        {json.dumps(strings, indent=2, ensure_ascii=False)}

        Translated JSON (valid JSON only):
        """
        
        print(f"Translating to {language}...")
        response = await self.invoke_model(translation_prompt)
        translated_json = self.extract_valid_json(response)
        
        if translated_json:
            return translated_json
        else:
            print(f"Could not extract valid JSON from {language} translation response.")
            return {"error": f"Failed to translate to {language}"}

    # Helper method to invoke the model
    async def invoke_model(self, prompt: str) -> str:
        try:
            response = self.chat.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Error invoking model: {e}")
            raise
    
    def extract_valid_json(self, response_content: str) -> Optional[Dict[str, Any]]:
        # Strip any markdown code block syntax
        content = re.sub(r'```(?:json)?|```', '', response_content).strip()
        
        # Try multiple extraction approaches
        try:
            # Direct parse if the entire string is JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            
            # Find JSON object pattern
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                potential_json = json_match.group(1)
                return json.loads(potential_json)
                
            # Look for multiple JSON objects and take the largest
            json_objects = re.findall(r'({[^{}]*(?:{[^{}]*})*[^{}]*})', content)
            if json_objects:
                # Sort by length and try to parse each one starting with longest
                for obj in sorted(json_objects, key=len, reverse=True):
                    try:
                        return json.loads(obj)
                    except json.JSONDecodeError:
                        continue
                        
            # If all else fails, use a cleanup approach to fix common JSON issues
            cleaned_json = self._cleanup_json_string(content)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"Error extracting valid JSON: {e}")
            print(f"Original content: {response_content[:100]}...")
            return None
            
    def _cleanup_json_string(self, json_str: str) -> str:
        """Attempt to fix common JSON formatting issues"""
        # Replace single quotes with double quotes (but not inside strings)
        json_str = re.sub(r"(?<!['\"])'([^']*)'(?!['\"])", r'"\1"', json_str)
        
        # Fix trailing commas in arrays and objects
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Add missing quotes around property names
        json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
        
        return json_str

    # # Extract valid JSON from model response
    # def extract_valid_json(self, response_content: str) -> Optional[Dict[str, Any]]:
    #     # First try to directly extract JSON
    #     try:
    #         json_match = re.search(r'({[\s\S]*})', response_content)
    #         if json_match:
    #             potential_json = json_match.group(1)
    #             return json.loads(potential_json)
    #         elif response_content.startswith("{") and response_content.endswith("}"):
    #             return json.loads(response_content)
    #     except json.JSONDecodeError:
    #         pass
        
    #     # If direct extraction fails, use a secondary model prompt
    #     try:
    #         json_extraction_prompt = f"""
    #         Extract only the valid JSON object from the following text. Return only the JSON object with no additional text.
    #         If there are multiple JSON objects, extract the one that appears to contain i18n translations (key-value pairs of strings).

    #         Input:
    #         {response_content}

    #         Output (valid JSON only):
    #         """
            
    #         json_extraction_response = self.chat.invoke([HumanMessage(content=json_extraction_prompt)])
    #         json_text = json_extraction_response.content.strip()
            
    #         json_match = re.search(r'({[\s\S]*})', json_text)
    #         if json_match:
    #             potential_json = json_match.group(1)
    #             return json.loads(potential_json)
    #         else:
    #             return json.loads(json_text)
    #     except Exception as e:
    #         print(f"Error extracting valid JSON: {e}")
    #         return None

    # Generate i18n configuration file
    def generate_i18n_config(self, languages: List[str], framework: str = "React") -> str:
        if framework == "Next":
            return self._generate_next_i18n_config(languages)
        else:
            return self._generate_react_i18n_config(languages)
    
    def _generate_react_i18n_config(self, languages: List[str]) -> str:
        imports = '\n'.join([
            f'import {lang}Translation from "./locales/{lang}.json";'
            for lang in languages
        ])
        
        resources = ',\n'.join([
            f'    {lang}: {{ translation: {lang}Translation }}'
            for lang in languages
        ])
        
        return f"""import i18n from "i18next";
import {{ initReactI18next }} from "react-i18next";
{imports}

i18n
  .use(initReactI18next)
  .init({{
    resources: {{
{resources}
    }},
    lng: "en", // Default language
    fallbackLng: "en",
    interpolation: {{
      escapeValue: false
    }}
  }});

export default i18n;"""

    def _generate_next_i18n_config(self, languages: List[str]) -> str:
        return f"""// next-i18next.config.js
module.exports = {{
  i18n: {{
    defaultLocale: 'en',
    locales: {json.dumps(languages)},
  }},
}};
"""


# Main function to process files and generate translations
async def process_components(
    api_key: str, 
    component_dir: str, 
    output_dir: str = None,
    framework: str = "React",
    languages: List[str] = ["en", "ar", "fr"],
    file_extensions: List[str] = [".jsx", ".tsx", ".js", ".ts"]
):
    if output_dir is None:
        output_dir = os.path.join(component_dir, "i18n_output")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    locales_dir = os.path.join(output_dir, "locales")
    os.makedirs(locales_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = I18nExtractor(api_key=api_key)
    
    # Find all component files
    component_files = []
    for root, _, files in os.walk(component_dir):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                component_files.append(os.path.join(root, file))
    
    if not component_files:
        print(f"No {', '.join(file_extensions)} files found in {component_dir}")
        return
    
    print(f"Found {len(component_files)} component files")
    
    # Process each file to extract strings
    all_strings = {}
    for file_path in component_files:
        print(f"\nProcessing {os.path.basename(file_path)}...")
        updated_code, extracted_strings = await extractor.process_file(file_path, framework)
        
        if "error" not in extracted_strings:
            # Save updated component
            rel_path = os.path.relpath(file_path, component_dir)
            output_file_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            async with aiofiles.open(output_file_path, 'w', encoding='utf-8') as f:
                await f.write(updated_code)
            print(f"Updated component saved to {output_file_path}")
            
            # Merge extracted strings
            all_strings.update(extracted_strings)
    
    if not all_strings:
        print("No translatable strings were extracted.")
        return
    
    print(f"\nExtracted {len(all_strings)} translatable strings")
    
    # Save English strings (source language)
    en_path = os.path.join(locales_dir, "en.json")
    async with aiofiles.open(en_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(all_strings, indent=2, ensure_ascii=False))
    print(f"English strings saved to {en_path}")
    
    # Translate to other languages
    translations = {"en": all_strings}
    for lang in languages:
        if lang != "en":
            translated_strings = await extractor.translate_strings(all_strings, lang)
            if "error" not in translated_strings:
                translations[lang] = translated_strings
                
                # Save translated strings
                lang_path = os.path.join(locales_dir, f"{lang}.json")
                async with aiofiles.open(lang_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(translated_strings, indent=2, ensure_ascii=False))
                print(f"{lang.capitalize()} strings saved to {lang_path}")
    
    # Generate i18n configuration file
    config = extractor.generate_i18n_config(languages, framework)
    config_filename = "next-i18next.config.js" if framework == "Next" else "i18n.js"
    config_path = os.path.join(output_dir, config_filename)
    
    async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
        await f.write(config)
    print(f"\ni18n configuration saved to {config_path}")
    
    print("\nI18n processing complete!")
    print(f"All output files are in: {output_dir}")

# Command line interface
async def main():
    api_key ="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"
    component_dir = "components"
    output_dir = "path_to_output_directory"
    framework = "React" 
    languages = ["en", "ar", "fr"]
    extensions = [".jsx", ".tsx", ".js", ".ts"]
    
    await process_components(
        api_key=api_key,
        component_dir=component_dir,
        output_dir=output_dir,
        framework=framework,
        languages=languages,
        file_extensions=extensions
    )

if __name__ == "__main__":
    asyncio.run(main())