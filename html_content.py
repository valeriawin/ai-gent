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
    <title>LLM Chat Interface with Tools</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
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
        .tools-section {{
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            max-width: 600px;
        }}
        .tool-info {{
            margin: 8px 0;
            text-align: left;
        }}
        .upload-section {{
            margin: 15px 0;
            padding: 10px;
            border-top: 1px solid #ddd;
        }}
        .reset-button {{
            margin-top: 10px;
            background-color: #f44336;
        }}
        .reset-button:hover {{
            background-color: #d32f2f;
        }}
        .file-input {{
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="tools-section">
        <h3>Available Tools</h3>
        <div class="tool-info">📊 <strong>Calculator:</strong> Solve mathematical problems</div>
        <div class="tool-info">🔍 <strong>DuckDuckGo Search:</strong> Find information online</div>
        <div class="tool-info">📄 <strong>Document QA:</strong> Answer questions about uploaded documents</div>

        <div class="upload-section">
            <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
                <div class="file-input">
                    <input type="file" name="file" id="fileInput" required>
                </div>
                <button type="submit">Upload Document</button>
            </form>
        </div>

        <form id="resetForm" action="/reset" method="post">
            <button type="submit" class="reset-button">Reset Conversation</button>
        </form>
    </div>

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

        // Add functionality for the upload form
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {{
            e.preventDefault();

            const fileInput = document.getElementById('fileInput');
            if (fileInput.files.length > 0) {{
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                try {{
                    const response = await fetch('/upload', {{
                        method: 'POST',
                        body: formData,
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

        // Add functionality for the reset form
        document.getElementById('resetForm').addEventListener('submit', async function(e) {{
            e.preventDefault();

            try {{
                const response = await fetch('/reset', {{
                    method: 'POST',
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
        }});
    </script>
</body>
</html>"""

    return html_content
