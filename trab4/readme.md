# Transformações Geométicas e Registro de Imagens

## 1.1 - Transformações Geométricas
- O fator de escala e o valor do angulo de rotacao das transformadas devem permitir valores continuos (ou seja, valores em ponto flutuante).
Um modo de se ampliar uma imagem é mapear cada posicao dos pontos da imagem de saida a partir da posicao correspondente dos pontos na imagem de entrada. Por exemplo, se o fator de escala é 2.25, enta ̃o a posicao de saida do pixel Po = (10, 23) seria mapeado para Pi = Po /s = (10/2.25, 23/2.25) = (4.444, 10.222) na imagem de entrada. Para determinar o valor do pixel em Pi, utilize os métodos de intepolacao descritos a seguir.
    - vizinho mais próximo
    - bilinearr
    - bicubica
    - lagrange

### Especificação do programa
- Para executar o programa faça:
``` 
python transf_geo.py 
                    [-a angulo]
                    [-e fator de escala]
                    [-d largura altura]
                    [-m interpolacao]
                    [-i imagem]
                    [-o imagem]
```
    - Onde:
        -a: angulo de rotacao medido em graus no sentido anti-horarrio 
        -e fator de escala.
        -d: dimensao da imagem de saida em pixels.
        -m: metodo de interpolacao utilizado (v - vizinho mais proximo | b - bilinear | bc - bicubica | l - lagrange).
        -i: imagem de entrada no formato PNG.
        -o: imagem de saida no formato PNG (apos a transformacao geometrica).
    - OBS: o programa só pode realizar apenas uma transformação geométrica por vez (escala ou rotação).
    - Ex1:
        - ``` python transf_geo.py -a 45 -d 800 600 -m bilinear -i input.png -o output.png ```
        - ``` python transf_geo.py -e 1.5 -d 800 600 -m bilinear -i input.png -o output.png ```

## 1.2 - Registo de Imagens
- Nesta etapa, uma imagem panoramica deve ser gerada a partir da correspondencia de um par de imagens. Pontos de interesse devem ser detectados e associados para o registro das imagens.

- Os principais passos do processo de correspondencia e geracao da imagem panoramica sao listados a seguir:
    - (1) converter as imagens coloridas de entrada em imagens de nıveis de cinza.
    - (2) encontrar pontos de interesse e descritores invariantes locais para o par de imagens.
    - (3) computar distancias (similaridades) entre cada descritor das duas imagens.
    - (4) selecionar as melhores correspondencias para cada descritor de imagem.
    - (5) executar a tecnica RANSAC (RANdom SAmple Consensus) para estimar a matriz de homografia (cv2.findHomography).
    - (6) aplicar uma projecao de perspectiva (cv2.warpPerspective) para alinhar as imagens.
    - (7) unir as imagens alinhadas e criar a imagem panoramica.
    - (8) desenhar retas entre pontos correspondentes no par de imagens.

- OBS:
    - No passo (2), explore e compare diferentes detectores de pontos de interesse e descritores, tais como SIFT (Scale Invariant Feature Transform), SURF (Speed Up Robust Feature), BRIEF (Robust Independent Elementary Features) e ORB (Oriented FAST, Rotated BRIEF). 
    - No passo (4), uma correspondencia sera considerada se o limiar definido estiver acima de um valor especificado pelo usuario. 
    - No passo (5), o calculo da matriz de homografia requer o uso de, no mınimo, 4 pontos de correspondencia.

- Para executar o programa faça:
``` python regis_img.py -l -d -a -b -o  ```
    - Onde:
        - -l: limiar para usar no match dos descritores.
        - -d: tipo do descritor (s - SIFT | b - BRIEF | o - ORB).
        - -a: primeira imagem para registro.
        - -b: segunda imagem para registro.
        - -o: nome + formato da imagem de saída.
    - Ex: ``` python regis_img.py -l 0.1 -d s -a imgs/foto5A.jpg -b imgs/foto5B.jpg -o imagem_saida.png ```