@app.route('/subir_pdf', methods=['POST'])
def subir_pdf():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo", 400

    file = request.files['file']

    if not file:
        return "El archivo está vacío", 400

    # Ubicación temporal
    file_path = os.path.join("temp", "uploaded_file.pdf")
    file.save(file_path)

    return "Archivo recibido correctamente", 200

@app.route('/resumen', methods=['GET','POST'])
def resumen():
    #if 'file' not in request.files:
    #    return "No se proporcionó ningún archivo"
    #file = request.files['file']
    #file_content = request.args.get('file_content')

    file_path = os.path.join("temp", "uploaded_file.pdf")

    if not os.path.exists(file_path):
        return "No se encontró el archivo", 400
    if not file:
        return "No se proporcionó ningún archivo en el parámetro 'file'", 400

    text = extract_text(file_path)
    
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    resumen = query({"inputs": text})
    contenido_resumen = resumen[0][next(iter(resumen[0]))]
    resumen_collection.insert_one({'resumen': contenido_resumen})
    tts = gTTS(text=contenido_resumen, lang='es')
    audio = tts.save("audio.mp3")
    audios_collection.insert_one({'audio': audio})
    
    return jsonify({'resumen': contenido_resumen, 'audio': audio})
