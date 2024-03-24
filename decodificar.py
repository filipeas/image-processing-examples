import sys
import numpy as np
import cv2

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

def saveText(name, text):
	with open(name, "w") as file:
		file.write(text)
		file.close()

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

def decodificar_esteganografia_v1(image, planoBits):
	binaryText = ""
	# findDelimiter = False
	lengthBits = "" # armazenar os 32 bits que representam o comprimento da msg

	for i in range(image.shape[0]):
		for j in range(image.shape[1]):
			for c in range(image.shape[2]): # loop na sequencia B-G-R
				pixelValue = image[i, j, c]
				pixelBinary = bin(pixelValue)[2:].zfill(8)
				
				for position in planoBits:
					bit = pixelBinary[7 - int(position)]

					if len(lengthBits) < 32:
						lengthBits += bit
					else:
						binaryText += bit
	
	messageLength = int(lengthBits, 2)

	return binaryText[:messageLength]

def main(imagem_saida, plano_bits, texto_saida):
	print('== ESTEGANOGRAFIA -> DECODIFICADOR ==')

	# inputs
	imgOutput = readImage(imagem_saida) # lendo arquivo da imagem
	showImage("Imagem de saida", imgOutput) # mostrando imagem na tela

    # output
	binaryText = decodificar_esteganografia_v1(imgOutput, plano_bits) # decodificando a esteganografia
	outputText = decodeText(binaryText) # decodificando o texto binário
	# print("texto decodificado:\n", outputText) # mostrando no terminal o texto
	saveText(texto_saida, outputText) # salvando .txt

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print("Use: python decodificar.py <imagem_saida.png> [<plano_bits>] <texto_saida.txt>")
		sys.exit(1)
	
	imagem_saida = sys.argv[1]
	plano_bits = sys.argv[2:-1]
	if not set(plano_bits).issubset(set(['0', '1', '2'])): # teste ['0', '1', '2', '3', '4', '5', '6', '7']
		print("Voce so pode usar 0, 1, ou 2 ou combinacoes.")
		print("Ex: python codificar.py <imagem_entrada.png> <texto_entrada.txt> 0 1 2 <imagem_saida.png>")
		sys.exit(1)
	texto_saida = sys.argv[-1]

	main(imagem_saida, plano_bits, texto_saida)