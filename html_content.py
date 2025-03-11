def get_html_content(question=None, answer=None):
    if question is None:
        question = "Enter your first prompt :)"
    if answer is None:
        answer = """~ And you'll see the answer here ~"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Chat Interface</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .question {{
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .answer {{
            margin-bottom: 20px;
            color: #444;
            max-width: 600px;
            text-align: center;
        }}
        .input-container {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        input {{
            padding: 8px;
            width: 300px;
        }}
        button {{
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #45a049;
        }}
    </style>
</head>
<body>
    <div class="question">{question}</div>
    <div class="answer">{answer}</div>
    <form id="promptForm">
        <div class="input-container">
            <input type="text" id="promptInput" name="prompt" placeholder="Type your question here">
            <button type="submit">Send</button>
        </div>
    </form>

    <script>
        document.getElementById('promptForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const promptInput = document.getElementById('promptInput');
            const prompt = promptInput.value.trim();
            
            if (prompt) {{
                try {{
                    const response = await fetch('/ask', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ prompt }}),
                    }});
                    
                    if (response.ok) {{
                        const htmlContent = await response.text();
                        document.open();
                        document.write(htmlContent);
                        document.close();
                    }} else {{
                        console.error('Error:', response.statusText);
                    }}
                }} catch (error) {{
                    console.error('Fetch error:', error);
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content
