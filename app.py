from flask import Flask, jsonify, render_template, request
from gtts import gTTS
import requests
import os 
from pymongo import MongoClient 
from pdfminer.high_level import extract_text 

app = Flask(__name__)

#conexiones con BBDD
mongo_url ='mongodb+srv://falberola:5zZi7xSEYPPIdGgc@cluster0.hd9lmf3.mongodb.net/datadmin_fincas'
client = MongoClient(mongo_url)
db = client.get_database('datadmin_fincas')
resumen_collection = db['resumen'] 
audios_collection = db['audios'] 

@app.route('/', methods=['GET'])
def plantilla():
    return render_template('endpoints.html')

@app.route('/subir_pdf', methods=['POST'])
def subir_pdf():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo"

    file = request.files['file']

    if not file:
        return "El archivo está vacío"

    # Ubicación temporal
    file_path = os.path.join("temp", "uploaded_file.pdf")
    file.save(file_path)

    fs_pdf = GridFS(db, collection='pdfs')

    with open(file_path, 'rb') as pdf_file:
    # Save the binary content to GridFS
        file_id = fs_pdf.put(pdf_file, filename='acta.pdf', metadata={'folder': 'pdfs'})

    return "Archivo recibido correctamente", 200

@app.route('/resumen', methods=['GET','POST'])
def resumen():
    #if 'file' not in request.files:
    #    return "No se proporcionó ningún archivo"
    #file = request.files['file']
    #file_content = request.args.get('file_content')

    file_path = os.path.join("temp", "uploaded_file.pdf")

    file = request.files['file']

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

if __name__ == '__main__':
    app.run(debug=True,port=8000)