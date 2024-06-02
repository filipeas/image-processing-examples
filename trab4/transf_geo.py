import numpy as np
import cv2
import pytesseract
import sys
import argparse
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

def vizinhoProximo(image, new_image, x, y):
    x_floor = int(np.floor(x))
    y_floor = int(np.floor(y))
    x_ceil = min(x_floor + 1, image.shape[1] - 1)
    y_ceil = min(y_floor + 1, image.shape[0] - 1)

    dx = x - x_floor
    dy = y - y_floor

    top_left = image[y_floor, x_floor]
    top_right = image[y_floor, x_ceil]
    bottom_left = image[y_ceil, x_floor]
    bottom_right = image[y_ceil, x_ceil]
    if dx < 0.5 and dy < 0.5:
        return top_left
    elif dx >= 0.5 and dy < 0.5:
        return top_right
    elif dx < 0.5 and dy >= 0.5:
        return bottom_left
    elif dx >= 0.5 and dy >= 0.5:
        return bottom_right

def bilinear(image, new_image, x, y):
    x_floor = int(np.floor(x))
    y_floor = int(np.floor(y))
    x_ceil = min(x_floor + 1, image.shape[1] - 1)
    y_ceil = min(y_floor + 1, image.shape[0] - 1)

    dx = x - x_floor
    dy = y - y_floor

    top_left = image[y_floor, x_floor]
    top_right = image[y_floor, x_ceil]
    bottom_left = image[y_ceil, x_floor]
    bottom_right = image[y_ceil, x_ceil]

    pixel = (1 - dx) * (1 - dy) * top_left + dx * (1 - dy) * top_right + (1 - dx) * dy * bottom_left + dx * dy * bottom_right
    return pixel.astype(np.uint8)

def P(t):
    return max(t, 0)

def b_spline(x):
    return (1/6) * (P(x + 2)**3 - 4 * P(x + 1)**3 + 6 * P(x)**3 - 4 * P(x - 1)**3)

def bicubica(image, new_image, x, y):
    x_floor = int(np.floor(x))
    y_floor = int(np.floor(y))

    dx = x - x_floor
    dy = y - y_floor

    pixel = 0
    for m in range(-1, 3):
        for n in range(-1, 3):
            xm = min(max(x_floor + m, 0), image.shape[1] - 1)
            ym = min(max(y_floor + n, 0), image.shape[0] - 1)
            pixel += image[ym, xm] * b_spline(m - dx) * b_spline(dy - n)
    return pixel.astype(np.uint8)

def L(dx, x, y, n, image):
    input_height, input_width = image.shape[:2]
    
    x_m1 = min(max(x - 1, 0), input_width - 1)
    x_0 = min(max(x, 0), input_width - 1)
    x_p1 = min(max(x + 1, 0), input_width - 1)
    x_p2 = min(max(x + 2, 0), input_width - 1)
    y_n2 = min(max(y + n - 2, 0), input_height - 1)

    term1 = (-dx * (dx - 1) * (dx - 2) * image[y_n2, x_m1]) / 6
    term2 = ((dx + 1) * (dx - 1) * (dx - 2) * image[y_n2, x_0]) / 2
    term3 = (-dx * (dx + 1) * (dx - 2) * image[y_n2, x_p1]) / 2
    term4 = (dx * (dx + 1) * (dx - 1) * image[y_n2, x_p2]) / 6

    return term1 + term2 + term3 + term4

def lagrange(image, new_image, x, y):
    x_floor = int(np.floor(x))
    y_floor = int(np.floor(y))

    dx = x - x_floor
    dy = y - y_floor

    L1 = L(dx, x_floor, y_floor, 1, image)
    L2 = L(dx, x_floor, y_floor, 2, image)
    L3 = L(dx, x_floor, y_floor, 3, image)
    L4 = L(dx, x_floor, y_floor, 4, image)

    f1 = (- dy * (dy - 1) * (dy - 2) * L1) / 6
    f2 = ((dy + 1) * (dy - 1) * (dy - 2) * L2) / 2
    f3 = (- dy * (dy + 1) * (dy - 2) * L3) / 2
    f4 = (dy * (dy + 1) * (dy - 1) * L4) / 6
    pixel = f1 + f2 + f3 + f4
            
    return pixel.astype(np.uint8)

def escalarImagem(image, largura, altura, escala, interpolacao):
    # altura = int(altura * escala)
    # largura = int(largura * escala)

    scaled_image = np.zeros((altura, largura, image.shape[2]), dtype=np.uint8)

    input_height, input_width = image.shape[:2]

    escala_altura_ratio = input_height / altura
    escala_largura_ratio = input_width / largura

    for i in range(scaled_image.shape[0]):
        for j in range(scaled_image.shape[1]):
            x = j * escala_largura_ratio
            y = i * escala_altura_ratio

            if interpolacao == "v":
                scaled_image[i, j] = vizinhoProximo(image, scaled_image, x, y)
            elif interpolacao == "b":
                scaled_image[i, j] = bilinear(image, scaled_image, x, y)
            elif interpolacao == "bc":
                scaled_image[i, j] = bicubica(image, scaled_image, x, y)
            elif interpolacao == "l":
                scaled_image[i, j] = lagrange(image, scaled_image, x, y)
            else:
                raise ValueError("Tipo de interpolacao desconhecido")
    return scaled_image

def rotacionarImagem(image, largura, altura, angulo, interpolacao):
    input_height, input_width = image.shape[:2]
    center_x, center_y = input_width // 2, input_height // 2

    angulo_rad = np.deg2rad(angulo)
    cos_angulo = np.cos(angulo_rad)
    sen_angulo = np.sin(angulo_rad)

    # rotated_image = np.zeros((altura, largura, image.shape[2]), dtype=np.uint8)
    rotated_image = np.zeros_like(image)

    for i in range(input_height):
        for j in range(input_width):
            x = j - center_x
            y = i - center_y

            original_x = cos_angulo * x + sen_angulo * y + center_x
            original_y = -sen_angulo * x + cos_angulo * y + center_y

            if 0 <= original_x < input_width and 0 <= original_y < input_height:
                if interpolacao == "v":
                    rotated_image[i, j] = vizinhoProximo(image, rotated_image, original_x, original_y)
                elif interpolacao == "b":
                    rotated_image[i, j] = bilinear(image, rotated_image, original_x, original_y)
                elif interpolacao == "bc":
                    rotated_image[i, j] = bicubica(image, rotated_image, original_x, original_y)
                elif interpolacao == "l":
                    rotated_image[i, j] = lagrange(image, rotated_image, original_x, original_y)
                else:
                    raise ValueError("Tipo de interpolacao desconhecido")
    return rotated_image

def main(angulo, escala, largura, altura, interpolacao, imagem_entrada, imagem_saida):
    print("\n--- Transformacoes geometricas ---")

    image = readImage(imagem_entrada)
    print("shape da imagem de entrada: ", image.shape)
    showImage("Imagem de entrada", image)

    if angulo:
        result_image = rotacionarImagem(image, largura, altura, angulo * -1, interpolacao)
    if escala:
        result_image = escalarImagem(image, largura, altura, escala, interpolacao)
    
    print("shape da imagem de saida: ", result_image.shape)
    showImage("Imagem de saida", result_image)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Transformações Geométricas em Imagens")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', type=float, help='Ângulo de rotação')
    group.add_argument('-e', type=float, help='Fator de escala')

    parser.add_argument('-d', nargs=2, type=int, metavar=('largura', 'altura'), required=True, help='Dimensões de largura e altura')
    parser.add_argument('-m', type=str, required=True, help='Método de interpolação (v - vizinho mais proximo | b - bilinear | bc - bicubica | l - lagrange)')
    parser.add_argument('-i', type=str, required=True, help='Caminho da imagem de entrada')
    parser.add_argument('-o', type=str, required=True, help='Caminho da imagem de saída')


    args = parser.parse_args()

    if args.a is not None:
        print(f"Ângulo de rotação: {args.a}")
    if args.e is not None:
        print(f"Fator de escala: {args.e}")
    print(f"Dimensões: largura = {args.d[0]}, altura = {args.d[1]}")
    print(f"Método de interpolação: {args.m}")
    print(f"Imagem de entrada: {args.i}")
    print(f"Imagem de saída: {args.o}")

    angulo = args.a
    escala = args.e
    largura = args.d[0]
    altura = args.d[1]
    interpolacao = args.m
    imagem_entrada = args.i
    imagem_saida = args.o
    
    main(angulo, escala, largura, altura, interpolacao, imagem_entrada, imagem_saida)