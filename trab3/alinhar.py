import numpy as np
import cv2
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
    # Calcular o centro da imagem
    center = (img.shape[1] // 2, img.shape[0] // 2)
    # Realizar a rotação da imagem
    rot_matrix = cv2.getRotationMatrix2D(center, angulo, 1.0)
    rotated_image = cv2.warpAffine(img, rot_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR)
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

def main(imagem_entrada, modo, imagem_saida):
    print("--- Algoritmo de alinhamento ---")

    img = readImage(imagem_entrada)
    showImage("Imagem original", img)

    angulo, imagem = projecao_horizontal(img)
    print("Angulo da imagem inclinada: ", angulo)
    showImage("Imagem Corrigida", imagem)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Use: python alinhar.py imagem_entrada.png modo imagem_saida.png")
        sys.exit(1)
    
    imagem_entrada = sys.argv[1]
    modo = sys.argv[2]
    imagem_saida = sys.argv[3]
    
    main(imagem_entrada, modo, imagem_saida)