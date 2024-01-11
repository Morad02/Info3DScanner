from tkinter import *
import os
import cv2
import face_recognition
import time
from genderDetection import age_gender_detector

# URL de la cámara
cam = 'http://192.168.38.83:4747/video'

class ReconocimientoFacial:
    #constructor
    def __init__(self,gui):
        self.gui = gui
        
        self.capturando_video = False
        self.login_exitoso = False
        self.usuario = None
        self.genero = None
        self.edad = None

    #Función para registrar un usuario
    def registro_facial(self):
        cap = cv2.VideoCapture(cam)
        self.capturando_video = True
        while self.capturando_video:
            ret, frame = cap.read()
            cv2.imshow('Registro Facial', frame)
            if cv2.waitKey(1) == 27:
                self.capturando_video = False
                
        nombre_usuario = self.entrada_usuario.get()
        cv2.imwrite(f"./db/{nombre_usuario}.jpg", frame)
        cap.release()
        cv2.destroyAllWindows()

        self.entrada_usuario_widget.delete(0, END)
        Label(self.pantalla_registro, text="Registro Facial Exitoso", fg="green", font=("Calibri", 11)).pack()

    #Función para crear una ventana para el registro
    def registro(self):
        self.pantalla_registro = Toplevel(self.gui.pantalla)
        self.pantalla_registro.title("Registro")
        self.pantalla_registro.geometry("300x250")

        self.entrada_usuario = StringVar()

        Label(self.pantalla_registro, text="Registro facial: debe asignar un usuario:").pack()
        Label(self.pantalla_registro, text="").pack()
        Label(self.pantalla_registro, text="Usuario * ").pack()
        self.entrada_usuario_widget = Entry(self.pantalla_registro, textvariable=self.entrada_usuario)
        self.entrada_usuario_widget.pack()
        Label(self.pantalla_registro, text="").pack()

        Button(self.pantalla_registro, text="Registro Facial", width=15, height=1, command=self.registro_facial).pack()

    #Función para comparar el rostro detectado en el video con los almacenados en la carpeta db
    def comparar_rostros(self, rostro_login_encodings, reconocimientos):
        if len(rostro_login_encodings) > 0:
            for reconocimiento in reconocimientos:
                similitud = face_recognition.compare_faces([reconocimiento["encoding"]], rostro_login_encodings[0])
                if similitud[0]:
                            self.usuario = reconocimiento["nombre"]
                            self.login_exitoso = True
    
    #Función para gestionar el inicio de sesión 
    def login_facial(self):
        cap = cv2.VideoCapture(cam)
        self.capturando_video = True
        archivos_imagenes = os.listdir("db")
        reconocimientos = []
        for archivo in archivos_imagenes:
            if archivo != "LOG.jpg":
                rostro_registrado = face_recognition.load_image_file(f"./db/{archivo}")
                rostro_registrado_encodings = face_recognition.face_encodings(rostro_registrado)
                if len(rostro_registrado_encodings) > 0:
                    reconocimientos.append({"nombre": archivo.split(".")[0], "encoding": rostro_registrado_encodings[0]})

        cont = 4
        start_time = time.time() # Agregar línea para registrar el tiempo inicial

        while self.capturando_video:
            ret, frame = cap.read()
            rostro_login_encodings = face_recognition.face_encodings(frame)
            
            cont += 1
            # Comprobar si ha pasado más de 5 segundos
            if time.time() - start_time > 5:
                print("Se agotó el tiempo para reconocimiento facial. Volviendo a la pantalla principal.")
                self.capturando_video = False
                cap.release()
                cv2.destroyAllWindows()
                self.cerrar_sesion()
                return

            
            if cont % 5 == 0:
                self.comparar_rostros(rostro_login_encodings, reconocimientos)
                if self.login_exitoso is True:
                    cv2.putText(frame, self.usuario, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    self.capturando_video = False

            cv2.imshow('Login Facial', frame)
            if cv2.waitKey(1) == 27:
                self.capturando_video = False
                
        cap.release()
        cv2.destroyAllWindows()
        
        
        if self.login_exitoso is False:
            print("Inicio de sesión fallido.")
            self.cerrar_sesion()
        else:
            print(f"Bienvenido, {self.usuario}")
            self.cerrar_sesion()
            self.gui.pantalla.destroy()
            results = age_gender_detector(f'db/{self.usuario}.jpg')
            self.genero , self.edad = results[0]
            
    #Función para iniciar el proceso de login
    def login(self):
        self.login_facial()

    #Fucción para cerrar la cámara
    def cerrar_sesion(self):
        self.capturando_video = False






