
"""--------------------Versión Meme Game 1.0---------------------"""

import pygame
from pygame.locals import  *
from pygame import mixer
import sys
import time
width= 640
height = 480
color_verde = (0,128,0)
color_blanco = (255,255,255)
color_negro = (0,0,0)

class Escena:
    def __init__(self):
        "Inicialización"
        self.proximaEscena = False
        self.jugando = True
    def leer_eventos(self, eventos):
        "Lee la lista de todos los eventos"
        pass
    def actualizar(self):
        "Cálculos y lógica"
        pass
    def dibujar(self, pantalla):
        "Dibuja todos los elementos en pantalla"
        pass
    def cambiar_escena(self, escena):
        "Selecciona la nueva escena a ser desplegada"
        self.proximaEscena = escena
class Director:
    def __init__(self, titulo = "", resolution = (width, height)):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('ridin.wav')
        pygame.mixer.music.play(-1)
        self.pantalla = pygame.display.set_mode(resolution)
        pygame.display.set_caption(titulo)
        self.surface = pygame.image.load('icono.ico')
        pygame.display.set_icon(self.surface)
        self.reloj = pygame.time.Clock()
        self.escena = None
        self.escenas = {}
   
    def ejecutar(self, escena_inicial, fps = 90):
        self.escena = self.escenas[escena_inicial]
        jugando = False
        menu = True
        while menu == True:
            pantallaMenu = pygame.display.set_mode((width, height))
            fondo = pygame.image.load('fondo.jpg')
            pantallaMenu.blit(fondo, (0,0))
            fuente = pygame.font.SysFont('Arial', 30)
            self.texto1 = fuente.render('Jugar: ENTER', True, color_blanco)
            self.texto1_rect = self.texto1.get_rect()
            self.texto1_rect.center = [550, 300]
            self.texto2 = fuente.render('Salir: ESCAPE', True, color_blanco)
            self.texto2_rect = self.texto2.get_rect()
            self.texto2_rect.center = [550, 400]
            self.pantalla.blit(self.texto1, self.texto1_rect)      
            self.pantalla.blit(self.texto2, self.texto2_rect)
            pygame.display.flip()
            
            for evento_menu in pygame.event.get():
                if evento_menu.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                # Presionando la tecla Enter se entra al juego y se sale con el Escape
                if evento_menu.type == pygame.KEYDOWN:
                    if evento_menu.key == pygame.K_RETURN:
                        jugando = True
                        menu = False
                    elif evento_menu.key == pygame.K_ESCAPE:
                        jugando = False
                        menu = False
        if jugando:  
            pygame.mixer.music.stop()
            pygame.mixer.music.load('xue.wav')
            pygame.mixer.music.play(-1)
            pygame.display.flip()         
        while jugando:
            self.reloj.tick(fps)
            eventos = pygame.event.get()
            # Revisar todos los eventos
            for evento in eventos:
                # Si se presiona la tachita de la barra de título
                if evento.type == pygame.QUIT:
                    # Cerrar el videojuego
                    jugando = False
            self.escena.leer_eventos(eventos)
            self.escena.actualizar()  
            self.escena.dibujar(self.pantalla)
            self.elegirEscena(self.escena.proximaEscena)
                            
            if jugando:  
                jugando = self.escena.jugando
                                
            pygame.display.flip()
        time.sleep(3)
    
    def elegirEscena(self, proximaEscena):
        if proximaEscena:
            if proximaEscena not in self.escenas:
                self.agregarEscena(proximaEscena)
            self.escena = self.escenas[proximaEscena]
    def agregarEscena(self, escena):
        escenaClase = 'Escena'+escena
        escenaObj = globals()[escenaClase]
        self.escenas[escena] = escenaObj();

class EscenaNivel(Escena):
    def __init__(self):
        Escena.__init__(self)
        self.bolita = Bolita()
        self.jugador = Abascal()
        self.muro = Muro(20)
        
        self.puntuacion = 0
        self.esperando_saque = True
        self.vidas = 3
        
        #El tiempo por el que se repetirá la tecla
        pygame.key.set_repeat(20)
        
    def leer_eventos(self, eventos):
        for evento in eventos:            
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < width / 2:
                        self.bolita.speed = [3, -3]
                    else:
                        self.bolita.speed = [-3, -3]
    def actualizar(self):           
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop
        #Colision entre bolita y jugador
        if pygame.sprite.collide_rect(self.bolita, self.jugador):
            self.bolita.speed[1] = -self.bolita.speed[1]
            
        #Se colocan todas las colisiones de los BTS con Españita    
        lista = pygame.sprite.spritecollide(self.bolita, self.muro, False)
        if lista:
            obstaculos = lista[0]
            cx = self.bolita.rect.centerx
            #Si la imagen de BTS golpea el lado izquierdo y derecho de la imagen de España hará que rebote, haciendo que no se destruya por esos lados
            if cx < obstaculos.rect.left or cx > obstaculos.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            #Si no pasa eso, se elimina el objeto    
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(obstaculos)
                        
            self.puntuacion += 10
        # Revisa si la imagen de BTS se sale de la pantalla
        if self.bolita.rect.top > height:
            self.vidas -= 1
            self.esperando_saque = True
        if self.puntuacion == 0:
            #Escenas de niveles 2,3,4...
            pygame.mixer.music.stop()
            self.cambiar_escena('Nivel3')
            #self.cambiar_escena('JuegoGanado')
    def dibujar(self, pantalla):
        pantalla.fill(color_negro)
        self.mostrar_puntuacion(pantalla)
        
        self.destroy_hearts(pantalla)
        
        self.mostrar_vidas(pantalla)
        #Representa la imagen de BTS y todos sus movimientos
        pantalla.blit(self.bolita.image, self.bolita.rect)
        #Representa a Abascal y todos sus movimientos como el buen facha que es
        pantalla.blit(self.jugador.image, self.jugador.rect)
        #Se dibuja la imagen de España en la pantalla
        self.muro.draw(pantalla)
        self.mostrar_niveles(pantalla)
    def mostrar_puntuacion(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        texto = fuente.render(str(self.puntuacion).zfill(5), True, color_blanco)
        texto_rect = texto.get_rect()    
        texto_rect.topleft = [0,0]
        pantalla.blit(texto, texto_rect)
    def mostrar_niveles(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Nivel: 1" 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [width / 2 , 0]
        pantalla.blit(texto, texto_rect)
    def mostrar_vidas(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Vidas: " 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [580, 0]
        pantalla.blit(texto, texto_rect)
    def destroy_hearts(self, pantalla):
        if self.vidas ==3:
            lista_vidas = pygame.sprite.Group(Vidas(3))
            lista_vidas.draw(pantalla)
                
        elif self.vidas ==2:
            lista_vidas = pygame.sprite.Group(Vidas(2))
            lista_vidas.draw(pantalla)
                
        elif self.vidas ==1:
            lista_vidas = pygame.sprite.Group(Vidas(1))
            lista_vidas.draw(pantalla)
        elif self.vidas < 0:
            self.cambiar_escena('JuegoTerminado')
class EscenaNivel2(Escena):
    def __init__(self):
        Escena.__init__(self)
        pygame.mixer.init()
        pygame.mixer.music.load('tripaloski.wav')
        pygame.mixer.music.play(-1)
        self.joder = Meme1()
        self.bolita = Bolita2()
        self.jugador = Putin()
        self.muro = Muro2(40)
        
        self.puntuacion = 200
        self.esperando_saque = True
        self.vidas = 2
        
        #El tiempo por el que se repetirá la tecla
        pygame.key.set_repeat(10)
        
    def leer_eventos(self, eventos):
        for evento in eventos:            
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < width / 2:
                        self.bolita.speed = [6, -6]
                    else:
                        self.bolita.speed = [-6, -6]
    def actualizar(self):           
        self.joder.update()
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop
        #Colision entre bolita y jugador
        if pygame.sprite.collide_rect(self.bolita, self.jugador):
            self.bolita.speed[1] = -self.bolita.speed[1]
            
        #Se colocan todas las colisiones de los BTS con Españita    
        lista = pygame.sprite.spritecollide(self.bolita, self.muro, False)
        if lista:
            obstaculos = lista[0]
            cx = self.bolita.rect.centerx
            #Si la imagen de BTS golpea el lado izquierdo y derecho de la imagen de España hará que rebote, haciendo que no se destruya por esos lados
            if cx < obstaculos.rect.left or cx > obstaculos.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            #Si no pasa eso, se elimina el objeto    
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(obstaculos)
                        
            self.puntuacion += 10
        # Revisa si la imagen de BTS se sale de la pantalla
        
        if self.bolita.rect.top > height:
            self.vidas -= 1
            self.esperando_saque = True
        if self.puntuacion == 600:
            #Escenas de niveles 2,3,4...
            self.cambiar_escena('Nivel3')   
    def dibujar(self, pantalla):
        pantalla.fill(color_negro)
        self.mostrar_puntuacion(pantalla)
        
        self.destroy_hearts(pantalla)
        
        self.mostrar_vidas(pantalla)
        #Representa la imagen de BTS y todos sus movimientos
        pantalla.blit(self.bolita.image, self.bolita.rect)
        #Representa a Abascal y todos sus movimientos como el buen facha que es
        pantalla.blit(self.jugador.image, self.jugador.rect)
        
        pantalla.blit(self.joder.image, self.joder.rect)
        #Se dibuja la imagen de España en la pantalla
        self.muro.draw(pantalla)
        self.mostrar_niveles(pantalla)
        
    def mostrar_puntuacion(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        texto = fuente.render(str(self.puntuacion).zfill(5), True, color_blanco)
        texto_rect = texto.get_rect()    
        texto_rect.topleft = [0,0]
        pantalla.blit(texto, texto_rect)
    def mostrar_niveles(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Nivel: 2" 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [width / 2 , 0]
        pantalla.blit(texto, texto_rect)
    def mostrar_vidas(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Vidas: " 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [580, 0]
        pantalla.blit(texto, texto_rect)
    def destroy_hearts(self, pantalla):
        if self.vidas ==2:
            lista_vidas = pygame.sprite.Group(Vidas(2))
            lista_vidas.draw(pantalla)
                
        elif self.vidas ==1:
            lista_vidas = pygame.sprite.Group(Vidas(1))
            lista_vidas.draw(pantalla)
        elif self.vidas < 0:
            self.cambiar_escena('JuegoTerminado')
class EscenaNivel3(Escena):
    def __init__(self):
        Escena.__init__(self)
        pygame.mixer.init()
        pygame.mixer.music.load('imagine.wav')
        pygame.mixer.music.play(-1)
        self.meme1 = Meme2()
        self.meme2 = Meme3()
        self.meme3 = Meme4()
        self.meme4 = Meme5()
        self.bolita = Bolita3()
        self.bolita2 = Bolita4()
        self.jugador = Ricardo()
        self.muro = Muro3(60)
        
        self.puntuacion = 600
        self.esperando_saque = True
        self.vidas = 1
        
        #El tiempo por el que se repetirá la tecla
        pygame.key.set_repeat(8)
        
    def leer_eventos(self, eventos):
        for evento in eventos:            
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < width / 2 or self.bolita2.rect.centerx < width / 2:
                        self.bolita.speed = [9, -9]
                        self.bolita2.speed = [9, -9]
                    else:
                        self.bolita.speed = [-9, -9]
                        self.bolita2.speed = [-9,-9]
    def actualizar(self):           
        self.meme1.update()
        self.meme2.update()
        self.meme3.update()
        self.meme4.update()
        self.bolita2.update()
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop
        #Colision entre bolita y jugador
        if pygame.sprite.collide_rect(self.bolita, self.jugador) or pygame.sprite.collide_rect(self.bolita2, self.jugador) :
            self.bolita.speed[1] = -self.bolita.speed[1]
            self.bolita2.speed[1] = -self.bolita2.speed[1]
            
        #Se colocan todas las colisiones de los BTS con Españita    
        lista = pygame.sprite.spritecollide(self.bolita, self.muro, False)
        if lista:
            obstaculos = lista[0]
            cx = self.bolita.rect.centerx
            #Si la imagen de BTS golpea el lado izquierdo y derecho de la imagen de España hará que rebote, haciendo que no se destruya por esos lados
            if cx < obstaculos.rect.left or cx > obstaculos.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            #Si no pasa eso, se elimina el objeto    
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(obstaculos)
                        
            self.puntuacion += 10
        lista = pygame.sprite.spritecollide(self.bolita2, self.muro, False)
        if lista:
            obstaculos = lista[0]
            cx = self.bolita2.rect.centerx
            #Si la imagen de BTS golpea el lado izquierdo y derecho de la imagen de España hará que rebote, haciendo que no se destruya por esos lados
            if cx < obstaculos.rect.left or cx > obstaculos.rect.right:
                self.bolita2.speed[0] = -self.bolita2.speed[0]
            #Si no pasa eso, se elimina el objeto    
            else:
                self.bolita2.speed[1] = -self.bolita2.speed[1]
            self.muro.remove(obstaculos)
                        
            self.puntuacion += 10    
        # Revisa si la imagen de BTS se sale de la pantalla
        if self.bolita2.rect.top > height:
            self.bolita2.speed[1] = -self.bolita2.speed[1]
        
        if self.bolita.rect.top > height:
            self.vidas -= 1
            self.esperando_saque = True
        if self.puntuacion == 1200:
            #Escenas de niveles 2,3,4...
            self.cambiar_escena('JuegoGanado')    
    def dibujar(self, pantalla):
        pantalla.fill(color_negro)
        self.mostrar_puntuacion(pantalla)
        
        self.destroy_hearts(pantalla)
        
        self.mostrar_vidas(pantalla)
        #Representa la imagen de BTS y todos sus movimientos
        pantalla.blit(self.bolita.image, self.bolita.rect)
        pantalla.blit(self.bolita2.image, self.bolita2.rect)
        #Representa a Abascal y todos sus movimientos como el buen facha que es
        pantalla.blit(self.jugador.image, self.jugador.rect)
        pantalla.blit(self.meme1.image, self.meme1.rect)
        pantalla.blit(self.meme2.image, self.meme2.rect)
        pantalla.blit(self.meme3.image, self.meme3.rect)
        pantalla.blit(self.meme4.image, self.meme4.rect)
        #Se dibuja la imagen de España en la pantalla
        self.muro.draw(pantalla)
        
        self.mostrar_niveles(pantalla)
    def mostrar_puntuacion(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        texto = fuente.render(str(self.puntuacion).zfill(5), True, color_blanco)
        texto_rect = texto.get_rect()    
        texto_rect.topleft = [0,0]
        pantalla.blit(texto, texto_rect)
    def mostrar_niveles(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Nivel: 3" 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [width / 2 , 0]
        pantalla.blit(texto, texto_rect)
    def mostrar_vidas(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 20)
        cadena = "Vidas: " 
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [580, 0]
        pantalla.blit(texto, texto_rect)
    def destroy_hearts(self, pantalla):                
        if self.vidas ==1:
            lista_vidas = pygame.sprite.Group(Vidas(1))
            lista_vidas.draw(pantalla)
        elif self.vidas < 0:
            self.cambiar_escena('JuegoTerminado')
                            
class EscenaJuegoTerminado(Escena):
    def actualizar(self):
        self.jugando = False
    def dibujar(self, pantalla):
        pantalla_end = pygame.display.set_mode((width, height))
        pantalla_end.fill(color_negro)
        pygame.mixer.music.load('astronomia.wav')
        pygame.mixer.music.play(-1)
        fuente = pygame.font.SysFont('Arial', 72)
        texto = fuente.render('GAME OVER', True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.center = [width / 2, height / 2]
        pantalla.blit(texto, texto_rect)
        
        time.sleep(5)
    
    
class EscenaJuegoGanado(Escena):
    def actualizar(self):
        self.jugando = False
    def dibujar(self, pantalla):
        pantalla_win = pygame.display.set_mode((width, height))
        imagen = pygame.image.load('ricardo.jpg')
        pantalla_win.blit(imagen, (0,0))
        pygame.mixer.music.load('ricardoM.wav')
        pygame.mixer.music.play(-1)
        fuente = pygame.font.SysFont('Arial', 40)
        texto = fuente.render('¡GANASTE JOTO!', True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.center = [width / 2, height / 2]
        pantalla.blit(texto, texto_rect)
        time.sleep(10)   
class Meme1(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('willy.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [2,2]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0 or self.rect.top > height:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones

        self.rect.move_ip(self.speed)        
class Meme2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('meme2.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [3,1]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0 or self.rect.top > height:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed) 
class Meme3(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('meme3.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [2,1]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0 or self.rect.top > height:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed) 
class Meme4(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('meme4.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [2,3]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0 or self.rect.top > height:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed) 
class Meme5(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('meme5.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [1,2]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0 or self.rect.top > height:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed) 
class Bolita4(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('anon.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [9,9]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed)        
class Bolita3(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('bts.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [9,9]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed)        
        
class Bolita2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('bts.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [6,6]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed)

class Bolita(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('bts.png')
        #Se dibuja el rectángulo donde se encontrará la imagen y se colocará en el medio de la pantalla
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height / 2

        self.speed = [6,6]
        
    def update(self):
        #Cuando toque la imagen el lado de abajo o el de arriba hará que rebote
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        #Cuando toque la imagen el lado dereho e izquierdo hará que rebote    
        elif self.rect.right >= width or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        #Da el valor de por dónde se moverá la imagen según las condiciones
        self.rect.move_ip(self.speed)
class Putin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('dios.png')
        #Se coloca a Putin en el punto medio de la pantalla por debajo 
        self.rect = self.image.get_rect()
        
        self.rect.midbottom = (width / 2, height - 20)
        #Hará que no se mueva para que sea controlable con la tecla izquierda y derecha
        self.speed = [0,0]
        
    def update(self, evento):
        '''Para mover a Putin'''
        #Para moverse por el lado izquierdo
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-10,0]
        #Para moverse por el lado derecho    
        elif evento.key == pygame.K_RIGHT and self.rect.right < width:
            self.speed = [10,0]
        else:
            self.speed = [0,0]
            
        self.rect.move_ip(self.speed)
class Ricardo(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('god.png')
        #Se coloca a Ricardo en el punto medio de la pantalla por debajo 
        self.rect = self.image.get_rect()
        
        self.rect.midbottom = (width / 2, height - 20)
        #Hará que no se mueva para que sea controlable con la tecla izquierda y derecha
        self.speed = [0,0]
        
    def update(self, evento):
        '''Para mover a Ricardo'''
        #Para moverse por el lado izquierdo
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-10,0]
        #Para moverse por el lado derecho    
        elif evento.key == pygame.K_RIGHT and self.rect.right < width:
            self.speed = [10,0]
        else:
            self.speed = [0,0]
            
        self.rect.move_ip(self.speed)                
class Abascal(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('abascal.png')
        #Se coloca a Abascal en el punto medio de la pantalla por debajo 
        self.rect = self.image.get_rect()
        
        self.rect.midbottom = (width / 2, height - 20)
        #Hará que no se mueva para que sea controlable con la tecla izquierda y derecha
        self.speed = [0,0]
        
    def update(self, evento):
        '''Para mover a Abascal'''
        #Para moverse por el lado izquierdo
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-10,0]
        #Para moverse por el lado derecho    
        elif evento.key == pygame.K_RIGHT and self.rect.right < width:
            self.speed = [10,0]
        else:
            self.speed = [0,0]
            
        self.rect.move_ip(self.speed)
#Tierra
class Obstaculo2(pygame.sprite.Sprite):
    def __init__(self, posicion):
        #Esto hará que la Tierra se convierta en un objeto tipo muro donde se podría romper
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('tierra.png')
        
        self.rect = self.image.get_rect()
        #Coloca a España en el sitio superior en la izquierda de la pantalla
        self.rect.topleft = posicion
class Muro2(pygame.sprite.Group):
    def __init__(self, cantidadObs):
        #Coloca la imagen de la Tierra tantas veces como queramos
        pygame.sprite.Group.__init__(self)
        
        pos_x = 0
        pos_y = 20
        #El bucle for hace que por cada imagen de la Tierra que pongamos se coloque bien en la pantalla sin pasarse de esta
        for i in range(cantidadObs):
            obstaculos = Obstaculo2((pos_x, pos_y))
            self.add(obstaculos)
            #Coloca la imagen de la Tierra más abajo según vayan superando el límite del ancho de la pantalla
            pos_x += obstaculos.rect.width
            if pos_x >= width:
                pos_x = 0
                pos_y += obstaculos.rect.height        
#Universo
class Obstaculo3(pygame.sprite.Sprite):
    def __init__(self, posicion):
        #Esto hará que el Universo se convierta en un objeto tipo muro donde se podría romper
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('universo.png')
        
        self.rect = self.image.get_rect()
        #Coloca a el Universo en el sitio superior en la izquierda de la pantalla
        self.rect.topleft = posicion

class Muro3(pygame.sprite.Group):
    def __init__(self, cantidadObs):
        #Coloca la imagen del Universo tantas veces como queramos
        pygame.sprite.Group.__init__(self)
        
        pos_x = 0
        pos_y = 20
        #El bucle for hace que por cada imagen del Universo que pongamos se coloque bien en la pantalla sin pasarse de esta
        for i in range(cantidadObs):
            obstaculos = Obstaculo3((pos_x, pos_y))
            self.add(obstaculos)
            #Coloca la imagen del Universo más abajo según vayan superando el límite del ancho de la pantalla
            pos_x += obstaculos.rect.width
            if pos_x >= width:
                pos_x = 0
                pos_y += obstaculos.rect.height
#España
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, posicion):
        #Esto hará que España se convierta en un objeto tipo muro donde se podría romper
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('españa.png')
        
        self.rect = self.image.get_rect()
        #Coloca a España en el sitio superior en la izquierda de la pantalla
        self.rect.topleft = posicion
class Muro(pygame.sprite.Group):
    def __init__(self, cantidadObs):
        #Coloca la imagen de España tantas veces como queramos
        pygame.sprite.Group.__init__(self)
        
        pos_x = 0
        pos_y = 20
        #El bucle for hace que por cada imagen de España que pongamos se coloque bien en la pantalla sin pasarse de esta
        for i in range(cantidadObs):
            obstaculos = Obstaculo((pos_x, pos_y))
            self.add(obstaculos)
            #Coloca la imagen de España más abajo según vayan superando el límite del ancho de la pantalla
            pos_x += obstaculos.rect.width
            if pos_x >= width:
                pos_x = 0
                pos_y += obstaculos.rect.height
                
class Corazon(pygame.sprite.Sprite):
    def __init__(self, posicion):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('corazon.png')
        
        self.rect = self.image.get_rect()
        
        self.rect.topright = posicion
    
class Vidas(pygame.sprite.Group):
    def __init__(self, cantidadVid):
        pygame.sprite.Group.__init__(self)
        
        pos_x = width
        pos_y = 0
        
        for i in range(cantidadVid):
            vidas = Corazon((pos_x, pos_y))
            self.add(vidas)
            pos_x -= vidas.rect.width
director = Director('MEME GAME', (width, height))
director.agregarEscena('Nivel')
director.ejecutar('Nivel')
