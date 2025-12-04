from seleniumbase import SB
import os
import traceback
import re


def download_openai_js_files():
    """
    Script to open the OpenAI API reference page, wait 10 seconds,
    then download all JavaScript files and return their content.
    """
    with SB(uc=True, test=True, locale="en", headless=False) as sb:
        try:
            url = "https://platform.openai.com/docs/api-reference/"
            sb.activate_cdp_mode(url, timeout=10)
            sb.wait_for_ready_state_complete(timeout=5)
            try:
                sb.uc_gui_click_captcha(timeout=8)
            except Exception:
                pass
            js_files = sb.execute_script("""
                // Method 1: Find scripts from DOM
                var scriptTags = Array.from(document.querySelectorAll('script[src]'))
                    .map(s => s.src)
                    .filter(src => src.includes('.js'));
                // Method 2: Find from performance entries
                var perfEntries = performance.getEntriesByType('resource')
                    .filter(r => r.initiatorType === 'script' || r.name.includes('.js'))
                    .map(r => r.name);
                // Combine and remove duplicates
                [...new Set([...scriptTags, ...perfEntries])];
            """)
            print("found files on load", js_files)

            found_any = False
            for js_url in js_files:
                try:
                    print("found file", js_url)
                    # Use XMLHttpRequest which is more reliable than fetch
                    try:
                        content = sb.execute_script(
                            """
                            var url = '"""
                            + js_url
                            + """';
                            var xhr = new XMLHttpRequest();
                            xhr.open('GET', url, false);  // false makes it synchronous
                            var result=null;
                            try {
                                xhr.send(null);
                                if (xhr.status === 200) {
                                    result=xhr.responseText;
                                }
                            } catch (error) {
                                console.error('XHR error:', error);
                            }
                            result;
                        """,
                            timeout=1,
                        )
                        sb.sleep(0.5)
                    except Exception as e:
                        print(f"ERROR in execute_script: {str(e)}")
                        content = None

                    if content:
                        print("successfully got contents for file", js_url)

                    # If browser approach fails, try Python requests as backup
                    if not content:
                        try:
                            import requests

                            response = requests.get(js_url, timeout=15)
                            if response.status_code == 200:
                                content = response.text
                                print(
                                    f"Got content via requests instead: {len(content)} bytes"
                                )
                        except Exception as e:
                            print(f"ERROR in requests: {str(e)}")
                            content = None

                    # Check if content exists before trying to print its properties
                    try:
                        if content is not None:
                            print("content size", len(content))
                            print("content sample", content[:100])
                        else:
                            print("WARNING: Content is None for", js_url)
                    except Exception as e:
                        print(f"ERROR printing content info: {str(e)}")

                    # Process content
                    if content and content.startswith(
                        'const e=[{id:"introduction",type:"markdown",'
                    ):
                        print("***found matching file - saving it***")
                        # Modify export statement as requested
                        modified_content = re.sub(
                            r"export\s*\{\s*(\w+)\s+as\s+A\s*,\s*(\w+)\s+as\s+a\s*\}\s*;?\s*$",
                            r"module.exports={A:\1,a:\2};",
                            content,
                            flags=re.MULTILINE,
                        )
                        output_path = os.path.join(
                            os.getcwd(), "openai-docs-reference.js"
                        )
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(modified_content)
                        # Only save the first match and stop
                        found_any = True

                        break
                except Exception as e:
                    print(f"Error processing {js_url}: {str(e)}")
                    traceback.print_exc()
            if found_any:
                return {js_url: output_path}
            else:
                print("no matching file found")
            return None
        except Exception:
            print("Exception in download_openai_js_files")
            traceback.print_exc()
            return None


if __name__ == "__main__":
    download_openai_js_files()
