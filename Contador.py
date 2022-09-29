import numpy as np
import cv2
import serial
import PySimpleGUI as sg

# Vetor para detecção de posições:
detects = []

# Variáveis para contagem:
parafusos = 0
contar = 0
contados = 0
i = 0

# Variáveis para morfologia:
morph_thresholding = 87
morph_opening = 2

# Variáveis de dimensão:
scale = 2
line = 50
offset = 30
xy1 = (10*scale, line*scale)
xy2 = (290*scale, line*scale)

# Cálculo do centro:
def center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx,cy

# Captura da imagem (Substituir por 0 dentro do parênteses para abrir webcam):
cap = cv2.VideoCapture(0)

# Função para contagem dos parafusos:
def contagem(parafusos, contar):

    contados = 0
    i = 0

    while(True):

        _, frame = cap.read()
        frame = cv2.resize(frame, (300*scale,300*scale))

        # Morfologia da imagem:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        ret, thresh = cv2.threshold(gray,morph_thresholding,255,cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = morph_opening)

        # Localizar parafusos:
        contours, hierarchy = cv2.findContours(opening,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # Linha para contagem:
        cv2.line(frame, xy1, xy2, (255,0,0), 2)

        # Verificar contornos:
        for cnt in contours:

            # Obter área e contornos:
            x,y,w,h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            # Verificar a área do objeto:
            if area > 8000:
            
                centro = center(x, y, w, h)

                # Desenhar o retângulo e centro dos parafusos:
                cv2.circle(frame, centro, 4, (0,0,255), -1)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                # Detectar posições dos parafusos:
                if len(detects) <= i:
                    detects.append([])
                if centro[1] > (line - offset)*scale and centro[1] < (line + offset)*scale:
                    detects[i].append(centro)
                else:
                    detects[i].clear()
                i += 1

        if i == 0:
            detects.clear()

        i = 0

        if len(contours) == 0:
            detects.clear()

        else:
            for detect in detects:
                for (c,l) in enumerate(detect):

                    if detect[c-1][1] < line*scale  and l[1] >= line*scale :
                        detect.clear()
                        parafusos += 1
                        contados += 1
                        if contar <= contados:
                            arduino.write('d'.encode())
                            contados = 0
                            cv2.destroyAllWindows
                        continue
                
                    if c > 0:
                        cv2.line(frame, detect[c-1], l, (0,0,255), 1)

        # Mostrar contagem:
        cv2.putText(frame, "Parafusos: "+str(parafusos), (5, 290*scale), cv2.FONT_HERSHEY_SIMPLEX, scale*0.5, (0, 255, 255),2)

        # Mostrar a o frame:
        cv2.imshow("Frame", frame)
        #cv2.imshow("Opening", opening)

        # Waitkey:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Loop para a conexão com o Arduino
while True: 
    try:  
        arduino = serial.Serial('COM4', 9600)
        print('Arduino conectado')
        break
    except:
        pass

# Criação da interface
sg.theme('DarkBlue14')
   
layout = [[sg.Text('Insira a quantidade de parafusos a ser contada:')],
          [sg.Input('', size=(20,1), key='quantidade'), sg.Button('Contar')]]
  
window = sg.Window('Contador de parafusos', layout)

# Leitura do Arduino:
while True:
    event, values = window.read()
    quantidade = values['quantidade']
      
    if event in (None, 'Exit'):
        break

    if event == 'Contar':
        arduino.write('l'.encode())
        contagem(parafusos, int(quantidade))

cv2.destroyAllWindows