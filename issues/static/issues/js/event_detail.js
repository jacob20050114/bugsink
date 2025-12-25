document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('ask-gemini-btn');
    const responseArea = document.getElementById('gemini-response-area');
    const contentDiv = document.getElementById('gemini-content');
    const loadingSpan = document.getElementById('gemini-loading');
    
    btn.addEventListener('click', function(e) {
        e.preventDefault(); 
        
        // UI 重置
        responseArea.classList.remove('hidden');
        loadingSpan.classList.remove('hidden');
        loadingSpan.classList.add('block');
        contentDiv.innerHTML = ""; // 清空內容
        
        const apiUrl = btn.getAttribute('data-api-url');
        
        fetch(apiUrl)
            .then(async response => {
                const text = await response.text();
                let data;
                try { data = JSON.parse(text); } catch (e) { data = null; }

                if (!response.ok) {
                    let msg = response.statusText;
                    if (data && data.analysis) msg = data.analysis;
                    else if (text) msg = text.replace(/<[^>]*>/g, '').substring(0, 300);
                    throw new Error(`Server Error (${response.status}): ${msg}`);
                }
                return data;
            })
            .then(data => {
                loadingSpan.classList.add('hidden');
                
                // [關鍵修改] 使用 marked.parse 將 Markdown 轉為 HTML
                // 這會自動處理 **粗體**、*列表* 以及 \n 換行
                contentDiv.innerHTML = marked.parse(data.analysis);
            })
            .catch(error => {
                loadingSpan.classList.add('hidden');
                // 錯誤訊息通常是純文字，我們簡單包裝一下
                contentDiv.innerHTML = `<div class="text-red-600 font-bold">執行失敗</div><div class="text-red-500">${error.message}</div>`;
            });
    });
});