import numpy as np
import cv2
import pytesseract
import sys
import matplotlib.pyplot as plt

def readImage(file):
	'''
	- Funcao que le a imagem.
	- O padrao de leitura do cv2 é BGR
	'''
	try:
		return cv2.imread(file)
	except Exception as error:
		print("Erro ao ler imagem: ", error)

def showImage(title, img):
	cv2.imshow(title, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def saveImage(name, img):
	print("Salvando arquivo {}...".format(name))
	cv2.imwrite(name, img)

def plotImage(binary_image, imagem_rotacionada):
    # Plotar a imagem original e a imagem rotacionada
    plt.figure(figsize=(10, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(binary_image, cmap='gray')
    plt.title('Imagem Original')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(imagem_rotacionada, cmap='gray')
    plt.title('Imagem Rotacionada')
    plt.axis('off')

    plt.show()

def plotHistogram(horizontal_projection, binary_image):
    # Plotar a projeção horizontal
    plt.plot(horizontal_projection, range(binary_image.shape[0]))
    plt.gca().invert_yaxis()  # Inverter o eixo y para corresponder à imagem
    plt.title('Horizontal Projection')
    plt.xlabel('Sum of Intensities')
    plt.ylabel('Pixel Row')
    plt.show()

def giraImagem(img, angulo):
    h, w = img.shape[:2]
    # calcular centro da imagem
    center = (w // 2, h // 2)
    # Realizar a rotação da imagem
    rot_matrix = cv2.getRotationMatrix2D(center, angulo, 1.0)
    # extender imagem para preencher cantos pretos
    cos = np.abs(rot_matrix[0, 0])
    sin = np.abs(rot_matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    # Ajustar a matriz de rotação para acomodar a extensão da imagem
    rot_matrix[0, 2] += (new_w / 2) - center[0]
    rot_matrix[1, 2] += (new_h / 2) - center[1]
    # rotacionando imagem
    rotated_image = cv2.warpAffine(img, rot_matrix, (new_w, new_h), borderValue=(255, 255, 255))
    return rotated_image

def projecao_horizontal(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    projecoes = []
    valores = []
    angles = range(-45, 46, 1)
    for angulo in angles:
        imagem_rotacionada = giraImagem(cinza, angulo)

        # Binarizar a imagem
        _, binary_image = cv2.threshold(imagem_rotacionada, 127, 255, cv2.THRESH_BINARY)
        # Inverter cores para que pixels pretos se tornem 1 e pixels brancos se tornem 0
        binary_image = cv2.bitwise_not(binary_image)
        # Projeção Horizontal
        horizontal_projection = np.sum(binary_image / 255, axis=1)  # (projetando pixels pretos) Dividir por 255 para normalizar os valores binários
        # print(horizontal_projection)
        # plotHistogram(horizontal_projection, binary_image)
        # salvando projecao
        projecoes.append(horizontal_projection)
        # calculando funcao objetivo
        diferencas = np.diff(horizontal_projection)
        valor = np.sum(diferencas ** 2)
        valores.append(valor)

    # Plotar as projeções horizontais para cada ângulo
    plt.figure(figsize=(10, 12))
    for i, projection in enumerate(projecoes):
        plt.plot(projection, label=f'Angle: {angles[i]}')
    plt.title('Projeção horizontal de todas as rotações de angulos (-45 a 45)')
    plt.xlabel('Linha de pixel')
    plt.ylabel('Número de pixels pretos')
    plt.legend()
    plt.show()

    # possivel angulo de inclinacao da imagem
    return angles[np.argmax(valores)], giraImagem(img, angles[np.argmax(valores)])

def moda(numeros):
    moda = np.nan
    contagem = 0
    valores, contagens = np.unique(numeros, return_counts=True)
    indice_max = np.argmax(contagens)
    if contagens[indice_max] > 1:
        moda = valores[indice_max]
    return moda

def transformada_hough(img):
    # converte para tons de cinza
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Suavizar a imagem para reduzir o ruído
    suaviza_gauss = cv2.GaussianBlur(cinza, (5, 5), 0)

    # Equalizar o histograma para melhorar o contraste
    equalizado = cv2.equalizeHist(suaviza_gauss)

    # Binarizar a imagem
    _, binary_image = cv2.threshold(equalizado, 127, 255, cv2.THRESH_BINARY)

    edges = cv2.Canny(binary_image, 50, 150, apertureSize=3) # usando canny
    # showImage("edges", edges)

    lines = cv2.HoughLines(edges, 1, np.pi/180, 130)

    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        # cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2) # riscar linhas detectadas
    
    # Mostrar imagem com as linhas detectadas
    # showImage("Hough Lines", img)
    
    if lines is not None:
        angulos = []

        for line in lines:
            ro, theta = line[0]
            angulo_grau = np.degrees(theta)
            angulos.append(angulo_grau)
        
        # foi testato a média, máximo e a moda, porem nos testes com as imagens
        # dadas, o melhor é calcular a moda para pegar a maior frequencia dos
        # angulos
        avg_angulo = moda(angulos)
        
        angulo = avg_angulo - 90

    return angulo, giraImagem(img, angulo)

def main(imagem_entrada, modo, imagem_saida):
    print("\n--- Algoritmo de alinhamento ---")

    img = readImage(imagem_entrada)
    showImage("Imagem original", img)

    # se 0 executar algoritmo de projecao horizontal
    if modo == "0":
        angulo, imagem = projecao_horizontal(img)
    else: # se 1 executar algoritmo da transformada de hough
        angulo, imagem = transformada_hough(img)
    # printa resultados
    print("Angulo da imagem inclinada: ", angulo)
    showImage("Imagem Corrigida", imagem)
    saveImage("Imagem_Corrigida.png", imagem)

    # tesseract
    # coloque nessa linha o path para o tesseract na sua máquina
    # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
    texto_original = pytesseract.image_to_string(img, lang='eng')
    texto_corrigido = pytesseract.image_to_string(imagem, lang='eng')
    print("Texto Original: ", texto_original)
    print("Texto Corrigido: ", texto_corrigido)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Use: python alinhar.py imagem_entrada.png modo imagem_saida.png")
        sys.exit(1)
    
    imagem_entrada = sys.argv[1]
    modo = sys.argv[2]
    imagem_saida = sys.argv[3]
    
    main(imagem_entrada, modo, imagem_saida)