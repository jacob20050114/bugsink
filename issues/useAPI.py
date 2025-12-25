import json
import traceback
import os
from events.models import Event  # 直接從資料庫模型匯入
from dotenv import load_dotenv
from google import genai

def process_task(event_id):
    """
    Directly get event data from data base and use gemini api to get 
    solution to the issues
    """
    try:
        # use event_id (UUID) to get data
        event = Event.objects.get(pk=event_id)
        event_data = event.data 

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            debug_file_path = os.path.join(current_dir, 'dbData.txt')
            with open(debug_file_path, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, indent=4, ensure_ascii=False)
                
            print(f"除錯資料已寫入: {debug_file_path}")
            
        except Exception as e:
            print(f"寫入 dbData.txt 失敗: {str(e)}")
        
    except Event.DoesNotExist:
        return f"錯誤: 在資料庫中找不到 ID 為 {event_id} 的 Event。"
    except Exception as e:
        return f"讀取資料庫時發生錯誤: {str(e)}"

    # 2. process event.data
    if isinstance(event_data, str):
        try:
            event_data = json.loads(event_data)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}\nRaw content: {event_data[:100]}..."
        
    if not isinstance(event_data, dict):
         return f"資料格式錯誤: 預期 event.data 為字典，但得到 {type(event_data)}。"



    try:
        environment = event_data.get("environment", "unknown")
        level = event_data.get("level", "unknown")
        timestamp = event_data.get("timestamp", "unknown")
        
        runtime = event_data.get("contexts", {}).get("runtime", {})
        r_name = runtime.get("name", "Python")
        r_version = runtime.get("version", "")
        runtime_info = f"{r_name} {r_version}".strip() or "Unknown Runtime"

        exception_values = event_data.get("exception", {}).get("values", [])
        exception = exception_values[0] if exception_values else {}

        error_type = exception.get("type", "Unknown Error Type")
        error_value = exception.get("value", "No error message provided")
        error_mechanism = exception.get("mechanism", {}).get("type", "unknown")

        stacktrace_frames = exception.get("stacktrace", {}).get("frames", [])
        
        last_frame = stacktrace_frames[-1] if stacktrace_frames else {}
        
        filename = last_frame.get("filename", "unknown file")
        abs_path = last_frame.get("abs_path", filename)
        lineno = last_frame.get("lineno", "?")
        function = last_frame.get("function", "unknown function")
        context_line = last_frame.get("context_line", "").strip()
        
        error_location_info = (
            f"檔案: {abs_path}\n"
            f"行號: {lineno}\n"
            f"函式: {function}\n"
            f"程式碼: {context_line}"
        )

        ai_context = (
            f"【錯誤報告摘要】\n"
            f"時間: {timestamp}\n"
            f"環境: {environment} ({level})\n"
            f"執行環境: {runtime_info}\n"
            f"錯誤機制: {error_mechanism}\n\n"
            f"【核心錯誤】\n"
            f"錯誤類型: {error_type}\n"
            f"錯誤訊息: {error_value}\n\n"
            f"【錯誤發生位置 (Error Location)】\n"
            f"{error_location_info}"
        )

    except Exception as e:
        return f"資料解析邏輯發生錯誤: {str(e)}\n\n原始錯誤 Traceback:\n{traceback.format_exc()}"
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("錯誤：找不到 GEMINI_API_KEY，請檢查 .env 檔案。")
    else:
        # Client
        client = genai.Client(api_key=api_key)
    
        try:
            # request
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=ai_context
            )

            # reply
            print(f"Gemini 回應：\n{response.text}")
            #ai_context = reponse.text
        except Exception as e:
            print(f"發生錯誤：{e}")

    return f"Gemini 分析報告 (Direct DB Access):\n\n{response.text}"
    #return f"Gemini 分析報告 (Direct DB Access):\n\n{response.text}\n\n{event_data}"
