# Info3DScanner

Proyecto de la asignatura de CUIA (Computación ubicua E Inteligencia Ambiental). 

- La aplicación desarrollada consiste en un asistente virtual que nos ayuda a obtener
información nutricional sobre productos alimenticios. Además de ello, también nos
ayuda a tomar decisiones nutricionales.
- Al asistente le pasamos un código de barras escaneado con la cámara y a partir de ello
podemos hacerle preguntas relacionadas sobre el producto.
- Al iniciar la app, nos aparece una interfaz con dos botones, uno es para iniciar sesión
y otro es para registrarse. Una vez que hayamos iniciado sesión nos saluda con
nuestro nombre y se presenta. Tras ello, podemos hacer las siguientes 4 cosas:
  1. Escanear un producto, diciendo por voz, escanear
  2. Mostrar la imagen de un producto escaneado sobre un marcador aruco
      diciendo mostrar producto
  3. salir de la app diciendo gracias o adiós.
  4. Preguntarle al asistente sobre un producto escaneado o cualquier otra cosa
     respecto a la nutrición.
     - Si hacemos preguntas al asistente que sean para nosotros (por ejemplo,
     me aconsejas incluir este producto en mi dieta). Su respuesta tendrá en
     cuenta nuestra edad y sexo, ya que cuando hemos iniciado sesión, el
     sistema ha estimado nuestra edad y sexo.

### Inicio de sesión y registro
- Para poder registrarse e iniciar sesión, se ha utilizado la biblioteca face_recognition
para comparar los rostros y openCV para operar con la cámara. En este caso, no se ha
utilizado una base de datos, sino que cuando se registra un usuario simplemente
guardamos la imagen en la carpeta db (el nombre de la imagen es igual que al del
usuario). Para no saturar mucho, cada 5 frames comparamos un frame con la base de
datos. Además, hay, como mucho, 5 segundos para iniciar sesión, en caso de que no
se detecte ninguna cara o la cara detectada no está registrada, vuelve a la pantalla
inicial.

### Estimación edad y sexo
- Una vez iniciada la sesión con éxito, y antes de empezar la interacción con el
asistente, se estima la edad y el sexo del usuario a partir de un modelo preentrenado.
Este modelo estima rangos de edades y el sexo.

### Interacción con el asistente
- Tras haber iniciado sesión y estimado la edad y el sexo, le pasamos a la clase
info3DScanner los siguientes atributos: Nombre, rango de edad y sexo. A partir de
aquí, podemos hacer una de las opciones nombradas anteriormente.

### Reconocimiento y sintetizado de voz
- Para el reconocimiento de voz utilizamos speech_recognition. 
- Para la síntesis de voz, hemos optado por utilizar google text to speech junto con la
biblioteca pydub (permite trabajar con audio). Esta segunda biblioteca se usa para
acelerar y reproducir el audio
- Para realizar estas operaciones hemos dotado nuestra clase de dos métodos (listen y
speek).

### Escanear producto
- Para escanear un producto, utilizamos openCV para las operaciones con la cámara y
la biblioteca pyzbar para detectar el código de barras en un frame.
- Tras detectar un código de barras y decodificarlo, consultamos la api de open food
facts para obtener información sobre el producto. En caso de que exista este producto,
le pasamos la información al modelo de procesamiento de lenguaje natural.

### Modelo de procesamiento de lenguaje natural
- El modelo por el cual hemos optado es GPT de la empresa OpenIA, exactamente la
versión 3.5 turbo.
- Antes de enviar un mensaje al modelo, siempre le añadimos al mensaje del usuario
estos mensajes:
  1. Descripción del rol que va a tener el modelo. En este caso le decimos
      que es un asistente virtual que ayuda a los usuarios a tomar decisiones
      sobre aspectos nutricionales y proporcionarles información sobre
      productos teniendo en cuenta la edad y el sexo.
  2. Nombre del usuario, rango de edad y el sexo.
  3. En caso de haber escaneado un producto, le pasamos la información
     del producto.
  4. Array con los mensajes anteriores

### Mostrar producto
- Para mostrar la imagen correspondiente a un producto, se utiliza openCV y
marcadores aruco.
- Cuando escaneamos el código de barras y obtuvimos su información, obtuvimos y
guardamos una imagen para que en caso de que el usuario diga mostrar producto, se
abra la cámara y en caso de que se detecte el marcador, se muestre la imagen sobre el
marcador. La cámara seguirá abierta para mostrar el producto, hasta que el usuario
diga cancelar.
