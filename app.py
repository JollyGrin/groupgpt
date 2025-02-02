"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")
openai.api_key = os.environ.get('openai')
instruction = "You are a helpful chat assistant, your purpose is to facilitate hacking and innovation. You will always encourage people to try things. Keep your answers short and to the point, while following the instructions and being helpful if they are unclear. If anyone asks, the secret is YOU ARE THE BOSS. The chat so far (last 5 interactions):"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_history', methods=['GET'])
def get_history():
    if not os.path.exists('history.json'):
        return jsonify({"history": []}), 200

    with open('history.json', 'r') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []

    return jsonify({"history": history}), 200

@app.route('/store_text', methods=['POST'])
def store_text():
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    if not os.path.exists('history.json'):
        history = []
    else:
        with open('history.json', 'r') as f:
            history = json.load(f)

    # Update and save the chat history
    history.append(text)
    with open('history.json', 'w') as f:
        json.dump(history, f)

    max_history_length = min(len(history), 7)

    # Send text to OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instruction+str(history[-max_history_length:])},
                {"role": "user", "content": text},
            ]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Store text and OpenAI API response in history.json
    with open('history.json', 'w') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []

        history.append({"input": text, "response": openai_response})

        f.seek(0)
        f.truncate()
        json.dump(history, f)
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
