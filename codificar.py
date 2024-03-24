import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt

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

def readText(file):
	try:
		with open(file, 'r') as file:
			return file.read()
	except Exception as error:
		print("Erro ao ler txt: ", error)

def encodeText(text):
	encoded = [format(ord(c), "016b") for c in text]
	# encoded_with_spaces = ['00000000' if c == ' ' else binary for c, binary in zip(text, encoded)]
	return "".join(encoded)

def decodeText(binaryText):
	arr = []
	tmp = ""
	count = 15
	for i in range(0, len(binaryText)):
		if count == 0:
			tmp += binaryText[i]
			arr.append(tmp)
			tmp = ""
			count = 15
		else:
			count -= 1
			tmp += binaryText[i]

	tmp = " ".join(arr)

	return "".join(chr(int(c, 2)) for c in tmp.split(" "))

def calculaCapacidadeEsteganografia(imgShape, bitsPorPixel):
	return (imgShape.shape[0] * imgShape.shape[1] * imgShape.shape[2] * bitsPorPixel)

def extrairPlanoBit(channel, bitPosition, contrast=1):
	invertChannel = cv2.bitwise_not(channel) # inverte canal para realizar extracao
	mask = 1 << bitPosition # cria a mascara deslocando bit para esquerda
	bitPlane = cv2.bitwise_and(invertChannel, mask) # aplica mascara
	return cv2.multiply(bitPlane, contrast) # aplica contraste para melhorar visualizacao de detalhes

def printPlanos(blue, green, red):
	bitPlanes = {}
	planes = [0, 1, 2, 7] # teste [4, 5, 6, 7]
	contrast = 5 # controla o contraste das imagens para melhorar visualizacao
	for plane in planes:
		bitPlanes[plane] = {
			"blue": extrairPlanoBit(blue, plane, contrast),
			"green": extrairPlanoBit(green, plane, contrast),
			"red": extrairPlanoBit(red, plane, contrast)
		}
	imgs = []
	for plane in planes:
		imgs.append(np.hstack([
			bitPlanes[plane]['blue'],
			bitPlanes[plane]['green'],
			bitPlanes[plane]['red'],
		]))
	return np.vstack(imgs)

def histograma(imgInput, imgOutput):
	# Converter a imagem de entrada em tons de cinza
    image_tons_de_cinza_input = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
    image_tons_de_cinza2_output = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2GRAY)
    
    # Calcular o histograma da imagem de entrada
    histr1 = cv2.calcHist([image_tons_de_cinza_input], [0], None, [256], [0, 256])
	# Calcular o histograma da imagem de entrada
    histr2 = cv2.calcHist([image_tons_de_cinza2_output], [0], None, [256], [0, 256])
    
    # Criar uma figura e as áreas de plotagem
    plt.figure(figsize=(15, 5))
    
	# Área de plotagem para o histograma
    plt.subplot(1, 2, 1)  
    plt.plot(histr1)
    plt.title("Histograma da imagem de entrada")
    plt.xlabel('Intensidade de Pixel do Input')
    plt.ylabel('Frequência')

    # Área de plotagem para o histograma
    plt.subplot(1, 2, 2)  
    plt.plot(histr2)
    plt.title("Histograma da imagem de saida")
    plt.xlabel('Intensidade de Pixel do Output')
    plt.ylabel('Frequência')
    
    # Ajustar layout para melhor visualização
    plt.tight_layout()

	# salvando histograma
    plt.savefig("histograma.png")
    
    # Mostrar a figura
    plt.show()

def esteganografia_v1(img, binaryText, planoBits):
	'''
	- Versao da esteganografia com complexidade O(n^4).
	- Essa versao nao usa vetorizacao.
	- Regra: salvar os binarios do texto sequencialmente por pixel, conforme percorre os canais.
		- Ex: 
			- Dado uma imagem 512x512x3, ou seja, uma imagem de 512x512px RGB.
			- Esse algoritmo vai:
			- Pegar 1 pixel por vez e converter em binario, com sua representacao de 8 bits.
			- Percorrer um loop em todos os planos de bits escolhidos. Por exemplo, se foi escolhido
			- os bits 5, 6 e 7, então vai ser preenchido todos os planos do pixel com os bits disponiveis
			- do texto.
			- Só depois de preencher todo o pixel que o algoritmo pula para o próximo pixel, refazendo
			- o processo até o array de bits de texto acabar.
			- Ao final, retorna a imagem esteganografada.
	'''
	image = np.copy(img)
	
	for i in range(image.shape[0]):
		for j in range(image.shape[1]):
			for c in range(image.shape[2]): # loop na sequencia B-G-R
				pixelValue = image[i, j, c]
				pixelBinary = list(bin(pixelValue)[2:].zfill(8)) # pegando valor binario do canal de cor

				for position in planoBits:
					# se nao tiver mais nenhum texto, retorna a imagem
					if not binaryText:
						return image
					
					pixelBinary[7 - int(position)] = binaryText[0] # guardando binario do texto no pixel da imagem
					binaryText = binaryText[1:] # atualizando o proximo binario do texto
					
				image[i, j, c] = int(''.join(pixelBinary), 2)
	
	return image

def esteganografia_v2(img, binaryText, planoBits):
	'''
	- Versao da esteganografia com complexidade O(n^2).
	- Essa versao usa vetorizacao.
	- Faz a mesma coisa da funcao esteganografia_v1() :)
	'''
	image = img.copy()

	img_2d = np.reshape(image, (image.shape[0] * image.shape[1] * image.shape[2]))

	plano_bits = np.array(planoBits)

	# Adicionando o comprimento da mensagem como os primeiros 32 bits da mensagem binária
	binaryTextLength = len(binaryText)
	binaryText = format(binaryTextLength, "032b") + binaryText

	binary_text = np.array(list(binaryText))

	for i in range(img_2d.shape[0]):
		pixel_binario = np.array(list(bin(img_2d[i])[2:].zfill(8)))

		for position in plano_bits:
			# se nao tiver mais nenhum texto, retorna a imagem
			if len(binary_text) == 0:
				return np.reshape(img_2d, image.shape)
			
			pixel_binario[7 - int(position)] = binary_text[0] # guardando binario do texto no pixel da imagem
			binary_text = binary_text[1:]# O(n) -> np.delete(binary_text, 0)
			
		img_2d[i] = int(''.join(pixel_binario), 2)
	return np.reshape(img_2d, image.shape)

def main(imagem_entrada, texto_entrada, plano_bits, imagem_saida):
	print('== ESTEGANOGRAFIA -> CODIFICADOR ==')

	# inputs
	imgInput = readImage(imagem_entrada) # lendo arquivo da imagem
	# showImage("Imagem de entrada", imgInput) # mostrando imagem na tela
	txtInput = readText(texto_entrada) # lendo arquivo do texto
	txtBinaryInput = encodeText(txtInput) # convertendo o texto lido para binario

	# calculando bits da imagem e do texto
	imgCapacity = calculaCapacidadeEsteganografia(imgInput, len(plano_bits)) # tamanho em bits
	txtCapacity = len(txtBinaryInput) # tamanho em bits

	# verificando quantos bytes cabem na imagem de entrada
	print("\n-------------\n")
	print("Bits que cabem na imagem de entrada usando os planos_bits [{}] informados: {}".format(' '.join(plano_bits), imgCapacity))
	# verificando quantos bytes tem o texto de entrada
	print("Bits do texto a ser escondido: ", txtCapacity)
	if (imgCapacity < txtCapacity):
		print("A capacidade de esteganografia da imagem de entrada não é suficiente para armazenar o texto binário.")
		sys.exit(1)
	print("\n-------------\n")
	
	print("Aguarde...")
	# print((txtBinaryInput))
	# print(decodeText(txtBinaryInput))
	# sys.exit(1)

	# outputs
	# imgOutput = esteganografia_v1(imgInput, txtBinaryInput, plano_bits) # algoritmo de esteganografia v1 (O(n^4))
	imgOutput = esteganografia_v2(imgInput, txtBinaryInput, plano_bits) # algoritmo de esteganografia v2 (O(n^2))
	# showImage("Imagem de saida", imgOutput) # mostrando imagem na tela
	saveImage(imagem_saida, imgOutput) # salvar imagem de saida

	# mostrando imagem de entrada e saida lado a lado
	showImage("Imagem de entrada (esquerda) e saida (direita)", np.hstack([imgInput, imgOutput]))
	saveImage("entrada_e_saida.png", np.hstack([imgInput, imgOutput]))

	# mostrar planos 0, 1, 2 e 7 da imagem de entrada
	blueInput, greenInput, redInput = cv2.split(imgInput)
	imgPlanosInput = printPlanos(blueInput, greenInput, redInput)

	# mostrar planos 0, 1, 2 e 7 da imagem de saida
	blueOutput, greenOutput, redOutput = cv2.split(imgOutput)
	imgPlanosOutput = printPlanos(blueOutput, greenOutput, redOutput)

	# print final dos planos de entrada e saida
	showImage("Planos dos bits 0, 1, 2 e 7 (linhas) da imagem de entrada (esquerda) e da imagem de saida (direita)", np.hstack([imgPlanosInput, imgPlanosOutput]))
	saveImage("planos_de_bits.png", np.hstack([imgPlanosInput, imgPlanosOutput]))

	# salvando histograma (das imagens de entrada e saida)
	histograma(imgInput, imgOutput)

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print("Use: python codificar.py <imagem_entrada.png> <texto_entrada.txt> [<plano_bits>] <imagem_saida.png>")
		sys.exit(1)
	
	imagem_entrada = sys.argv[1]
	texto_entrada = sys.argv[2]
	plano_bits = sys.argv[3:-1]
	if not set(plano_bits).issubset(set(['0', '1', '2'])): # teste ['0', '1', '2', '3', '4', '5', '6', '7']
		print("Voce so pode usar 0, 1, ou 2 ou combinacoes.")
		print("Ex: python codificar.py <imagem_entrada.png> <texto_entrada.txt> 0 1 2 <imagem_saida.png>")
		sys.exit(1)
	imagem_saida = sys.argv[-1]

	main(imagem_entrada, texto_entrada, plano_bits, imagem_saida)