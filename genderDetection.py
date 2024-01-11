import cv2

#Modelos a utilizar
faceProto = "modelNweight/opencv_face_detector.pbtxt"
faceModel = "modelNweight/opencv_face_detector_uint8.pb"

ageProto = "modelNweight/age_deploy.prototxt"
ageModel = "modelNweight/age_net.caffemodel"

genderProto = "modelNweight/gender_deploy.prototxt"
genderModel = "modelNweight/gender_net.caffemodel"

#Media de los colores en las imágenes de entrenamiento
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
#Valores de edad y género que puede predecir el modelo
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

#Cardar los modelos
ageNet = cv2.dnn.readNet(ageModel, ageProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)
faceNet = cv2.dnn.readNet(faceModel, faceProto)

#Margen que se añade al rostro detectado
padding = 20

#Función que toma de entrada un frame y una red neuronal
#Devuelve la imagen con el rostro encuadrado y las coordenadas de la caja
def getFaceBox(net, frame, conf_threshold=0.7):
    
    frameOpencv2Dnn = frame.copy()
    #Obtener las dimensiones del frame
    frameHeight = frameOpencv2Dnn.shape[0]
    frameWidth = frameOpencv2Dnn.shape[1]
    #Preparar el frame para la red neuronal
    blob = cv2.dnn.blobFromImage(frameOpencv2Dnn, 1.0, (300, 300), [104, 117, 123], True, False)
    #Configurar la red neuronal
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    #Si la confianza es mayor que el umbral, se añade la caja a la lista
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            #Dibuja la caja delmitadora
            cv2.rectangle(frameOpencv2Dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return frameOpencv2Dnn, bboxes

#Toma de entrada una imagen y devuelve una lista con el género y la edad de cada rostro detectado
def age_gender_detector(image_path):
    frame = cv2.imread(image_path)
    
    if not frame is None:
        #Obtener el frame con las cajas delimitadoras y las coordenadas de las cajas
        frameFace, bboxes = getFaceBox(faceNet, frame)
        results = []
        for bbox in bboxes:
            #Obtener la región de interes (ROI) (Rosotro detectado)
            face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]

            #Preparar la imagen para la red neuronal
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            #Configura la red neuronal
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
    
            results.append((gender, age))
        return results
    else:
        print("Image not found")



