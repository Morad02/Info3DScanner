from RFacial import ReconocimientoFacial as rf
from info3DScanner import BarcodeScanner
from tkinter import *

class GUI:
    def __init__(self):
        self.usuario = None
        
    
    def app(self):
        self.pantalla = Tk()
        self.pantalla.geometry("300x250")
        self.pantalla.title("info3DScanner")

        reconf = rf(self)

        Label(text="").pack()
        Button(text="Iniciar Sesión", height="2", width="30", command=reconf.login).pack()
        Label(text="").pack()
        Button(text="Registro", height="2", width="30", command=reconf.registro).pack()
        
        self.pantalla.mainloop()
        
        if reconf.login_exitoso:
            self.usuario = reconf.usuario
            self.gender = reconf.genero
            self.age = reconf.edad
            self.barcode_scanner = BarcodeScanner(self.usuario, self.age, self.gender)
            self.barcode_scanner.continuous_interaction()
            
    

if __name__ == "__main__":
    gui = GUI()
    gui.app()
    