import cv2
from cv2 import aruco
import numpy as np 
import requests # para realizar solicituddes HTTP 
from pyzbar.pyzbar import decode # para decodificar el código de barras
import os # para acceder a los archivos del sistema
import openai # para acceder a la API de OpenAI
import speech_recognition as sr # para reconocimiento de voz
from gtts import gTTS # para sintetizar voz
from IPython.display import clear_output # para limpiar la salida
from pydub import AudioSegment # para manipulación de audio
from pydub.playback import play # para reproducir audio
from tempfile import NamedTemporaryFile # para crear archivos temporales
import threading # para utilizar hebras

# URL de la cámara
cam = 'http://192.168.38.83:4747/video'

# Para importar la calibración de la cámara
if os.path.exists('camara.py'):
    import camara
else:
    print("Es necesario realizar la calibración de la cámara")
    exit()

class BarcodeScanner:
    # Constructor
    def __init__(self,user,age,gender):
        openai.api_key = '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'
        self.DICCIONARIO = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.open_food_facts_url = 'https://world.openfoodfacts.org/api/v0/product/{}.json'
        self.chatgpt_model = "gpt-3.5-turbo"
        self.chatgpt_system = {
            "nickname": "scannerinfo3D",
            "person": {
                "description": "I am Info3DScanner, a digital assistant specialized in food products. I provide accurate, concise, and short answers based on users' gender and age to help users make informed decisions about their food choices."
            }
        }
        self.imageProduct = None
        self.ejecutar = True
        self.user = user
        self.age = age
        self.gender = gender
        self.comando_cierre = threading.Event()

    # Método para escanear el código de barras
    def comenzar_escaneo(self):
        cap = cv2.VideoCapture(cam) 
        barcode_data = self.escanear_codigo_barras(cap)
        cap.release()
        cv2.destroyAllWindows()
        
        return barcode_data
        

    # Método para cancelar la cámara
    def cancelar_camara(self):
        def cerrar():
            while not self.comando_cierre.is_set():
                comando = self.listen()
                if 'cancelar' in comando.lower():
                    self.comando_cierre.set()

        threading.Thread(target=cerrar).start()
    
    #Método para convertir texto a voz
    def speak(self, text):
        #Instancia gTTS
        #text: Texto a convertir a voz
        #lang: Idioma
        #slow: Velocidad lenta o no
        tts = gTTS(text=text, lang='es', slow=False)  
        
        #Fichero temporal para almacenar el audio
        with NamedTemporaryFile(delete=False) as f:
            tts.save(f.name)
            #Cargamos el fichero como mp3
            audio = AudioSegment.from_file(f.name, format="mp3")
            #Aceleramos el audio
            faster_audio = audio.speedup(playback_speed=1.35)
            play(faster_audio)
        #Eliminamos el fichero temporal
        os.unlink(f.name)  
        
    #Método para escuchar y reonoceer la voz
    def listen(self):
        
        r = sr.Recognizer()
        #Umbral de energía para destinguir entre ruido y voz
        r.energy_threshold = 4000
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            #Convertir el audio a texto
            text = r.recognize_google(audio, language="es-ES")
            return text
        except:
            #Informar si no se ha entendido el audio
            print("Lo siento, no te he entendido. Por favor, intenta de nuevo.")
            self.speak("Lo siento, no te he entendido. Por favor, intenta de nuevo.")
            
            return self.listen()

    #Método para obtener información del producto usando el código de barras
    def get_product_info(self, barcode):
        
        response = requests.get(self.open_food_facts_url.format(barcode))
        data = response.json()
        if data['status'] == 1:
            if 'image_front_url' in data['product']:
                self.imageProduct = self.descargar_imagen_producto(data['product']['image_front_url'])
            return data['product']
        else:
            return None

    #Método para descargar la imagen del prodcuto
    def descargar_imagen_producto(self, url_imagen_producto):
        
        resp = requests.get(url_imagen_producto, stream=True)
        resp.raise_for_status()
        with open('temp_image.png', 'wb') as f:
            f.write(resp.content)
        imagen_producto = cv2.imread('temp_image.png', cv2.IMREAD_COLOR)
        os.remove('temp_image.png')
        return imagen_producto

    #Método para detectar un código de barras en un frame
    def detectar_codigo_barras(self, frame):
        
        #función decode de pyzbar para detectar códigos de barras
        barcodes = decode(frame)
        #Por cada codigo de barras detectado
        for barcode in barcodes:
            #Coordenadas del rectangulo que encierra el código de barras
            x, y, w, h = barcode.rect
            #Dibujamos el rectángulo
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_data = barcode.data.decode("utf-8")
            print(f"Datos del código de barras: {barcode_data}")
            return barcode_data
        return None

    #Método para obtener respuesta de GPT
    def get_gpt4_response(self, previous_messages, new_message):
        
        response = openai.ChatCompletion.create(
            model=self.chatgpt_model,
            messages=previous_messages + [
                {"role": "system", "content": str(self.chatgpt_system)},  # Convertir el contenido del sistema a cadena de texto
                {"role": "user", "content": f"I am {self.user}, a {self.gender} and I am {self.age} years old."},
                {"role": "user", "content": str(new_message)}  # Convertir el nuevo mensaje a cadena de texto
            ]
        )
        
        return response['choices'][0]['message']['content']

    #Método para interactuar continuamente con el usuario 
    def continuous_interaction(self):
        previous_messages = []
        while self.ejecutar:
            clear_output(wait=True)
            self.speak(f'Hola {self.user}, soy Info3DScanner, tu asistente personal para la información de productos alimenticios. ¿En qué puedo ayudarte?')
            
            newProduct = False
            mostrar_producto = False
            while self.ejecutar:
                
                if(newProduct):
                    product_info = self.get_product_info(barcode)
                    if(product_info is None):
                        self.speak('Lo siento, no he podido encontrar información sobre este producto. Por favor, intenta de nuevo.')
                        mostrar_producto = False
                    else:
                        user_message = f"El producto {product_info.get('product_name', 'No disponible')} tiene la siguiente información: " \
                                       f"Nutrientes: {product_info.get('nutriments', 'No disponibles')}, " \
                                       f"Alergenos: {product_info.get('allergens', 'No disponibles')}, " \
                                       f"Categorias: {product_info.get('categories', 'No disponibles')}."

                        previous_messages.append({"role": "user", "content": user_message})
                    newProduct = False
                
                
                question = self.listen()

                if 'adiós' in question or 'gracias' in question:
                    self.speak("Hasta luego, fue un placer ayudarte.")
                    self.ejecutar = False
                    return
                elif 'mostrar producto' in question.lower() and mostrar_producto:
                    self.speak("Preparando producto...")
                    self.mostrar_producto()
                elif 'escanear' in question.lower():
                    self.speak("Preparando escaneo...")
                    barcode = self.comenzar_escaneo()
                    mostrar_producto = True
                    newProduct = True
                else:
                    print("Procesando su pregunta...")
                    self.speak("Procesando su pregunta...")
                    
                    response = self.get_gpt4_response(previous_messages, question)
                    print("Respuesta: ", response)
                    self.speak(response)
                    previous_messages.append({"role": "assistant", "content": response})

    #Método para escanear el código de barras usando la cámara
    def escanear_codigo_barras(self, cap):
        barcode_detected = False
        #Obtener dimensiones  del frame de la cámara
        wframe = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        hframe = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #Obtener la matriz de cámara óptima y la región de interés (ROI)
        matrix, roi = cv2.getOptimalNewCameraMatrix(camara.cameraMatrix, camara.distCoeffs, (wframe, hframe), 1, (wframe, hframe))
        roi_x, roi_y, roi_w, roi_h = roi
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            #Corregir distorsión de la cámara
            corrected_frame = cv2.undistort(frame, camara.cameraMatrix, camara.distCoeffs, None, matrix)
            #Recortar frame a la región de interés
            corrected_frame = corrected_frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

            if not barcode_detected:
                barcode_data = self.detectar_codigo_barras(corrected_frame)
                
                if barcode_data is not None:
                    barcode_detected = True
                    cv2.imshow("WEBCAM", corrected_frame)
                    cv2.waitKey(2000)  # Pausa de 3 segundos
                else:
                    cv2.imshow("WEBCAM", corrected_frame)
                    cv2.waitKey(1)

            else:
                cap.release()
                cv2.destroyAllWindows()
                break
        
        return barcode_data
    
    #Método para buscar marcador aruco en un frame
    def buscar_marcador_aruco(self, frame):
        #Convertir frame a escala de grises
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Detectar marcadores aruco
        corners, ids, _ = aruco.detectMarkers(gris, self.DICCIONARIO)
        #Obtener coordenas de las esquenas del marcador
        if ids is not None:
            c1 = (corners[0][0][0][0], corners[0][0][0][1])
            c2 = (corners[0][0][1][0], corners[0][0][1][1])
            c3 = (corners[0][0][2][0], corners[0][0][2][1])
            c4 = (corners[0][0][3][0], corners[0][0][3][1])
            return np.array([c1,c2,c3,c4])
        return None

    #Método para agregar imagen de un prdcuto a un frame
    def agregar_imagen_producto(self, frame, esquinas_marcador, imagen_producto):
        #dimensiones de la imagen del producto
        size = imagen_producto.shape
        #Coordenas de las esquinas de la imagen del producto
        imagePoints = np.array([
            [0,0],
            [size[1]-1,0],
            [size[1]-1,size[0]-1],
            [0,size[0]-1]
        ], dtype=float)
        
        #Matriz homografía para mapear las esquinas de la imagen a las esquinas del marcador
        h, state = cv2.findHomography(imagePoints, esquinas_marcador)
        #Aplicar transformación perspectiva a la imagen del producto
        perspectiva = cv2.warpPerspective(imagen_producto,h,(frame.shape[1],frame.shape[0]))
        #rellenar el área del marcador con negro
        cv2.fillConvexPoly(frame, esquinas_marcador.astype(int),0,16)
        return frame + perspectiva #Imagen del producto transformada + frame
    
    #Método para mostrar un producto
    def mostrar_producto(self):
        
        if self.imageProduct is not None:
            self.cancelar_camara()
            cap = cv2.VideoCapture(cam)
            
            while True:
                if self.comando_cierre.is_set():
                    break
                ret, frame = cap.read()
                if not ret:
                    break
                esquinas_marcador = self.buscar_marcador_aruco(frame)
                if esquinas_marcador is not None:
                    frame = self.agregar_imagen_producto(frame, esquinas_marcador, self.imageProduct)
                cv2.imshow("WEBCAM", frame)
                cv2.waitKey(1)
            cap.release()
            cv2.destroyAllWindows()
            self.comando_cierre.clear()
            
        else:
            self.speak("No se ha descargado la imagen del producto.")


