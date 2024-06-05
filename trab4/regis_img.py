import numpy as np
import cv2
import pytesseract
import sys
import argparse
import matplotlib.pyplot as plt
from scipy.spatial import distance

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

def igualarTamanho(imagem1, imagem2):
    altura1, largura1 = imagem1.shape[:2]
    altura2, largura2 = imagem2.shape[:2]

    nova_altura = max(altura1, altura2) * 2
    nova_largura = max(largura1, largura2) * 2

    imagem1_preenchida = np.zeros((nova_altura, nova_largura, 3), dtype=np.uint8)
    imagem2_preenchida = np.zeros((nova_altura, nova_largura, 3), dtype=np.uint8)

    imagem1_preenchida[0:altura1, 0:largura1] = imagem1
    imagem2_preenchida[0:altura2, 0:largura2] = imagem2

    return imagem1_preenchida, imagem2_preenchida

def encontrarDescritores(imageA, imageB, descritor):
    if descritor == 's':
        detector = cv2.SIFT_create()
    elif descritor == 'su':
        # detector = cv2.xfeatures2d.SURF_create()
        raise ValueError("Método privado")
    elif descritor == 'b':
        star = cv2.xfeatures2d.StarDetector_create()
        ptsA = star.detect(imageA, None)
        ptsB = star.detect(imageB, None)
        brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
        ptsA, descritoresA = brief.compute(imageA, ptsA)
        ptsB, descritoresB = brief.compute(imageB, ptsB)
        return ptsA, ptsB, descritoresA, descritoresB
    elif descritor == 'o':
        detector = cv2.ORB_create()
    else:
        raise ValueError("Descritor informado não é suportado.")
    
    ptsA, descritoresA = detector.detectAndCompute(imageA, None)
    ptsB, descritoresB = detector.detectAndCompute(imageB, None)
    
    return ptsA, ptsB, descritoresA, descritoresB

def matchDescritores(descritoresA, descritoresB, descritor, limiar):
    if descritor == 's':
        limiar = 1000 * limiar
        norm = cv2.NORM_L2
    elif descritor == 'b' or descritor == 'o':
        limiar = 255 * limiar
        norm = cv2.NORM_HAMMING
    
    bf = cv2.BFMatcher(norm, crossCheck=True)
    matches = bf.match(descritoresA, descritoresB)
    num_valid_matches = [m for m in matches if m.distance < limiar]
    num_valid_matches = sorted(num_valid_matches, key=lambda x: x.distance)
    print("qtd de matches: ", len(num_valid_matches))
    return num_valid_matches

def estimarHomografia(ptsA, ptsB, matches, max_points=4):
    if len(ptsA) < max_points or len(ptsB) < max_points:
        raise ValueError("Precisa de pelo menos 4 pontos para calcular a homografia")

    src = np.float32([ptsA[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst = np.float32([ptsB[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    
    return M

def alinhaImagem(imageA, imageB, M):
    hA, wA = imageA.shape[:2]
    hB, wB = imageB.shape[:2]
    # return cv2.warpPerspective(imageA, M, (wB + wA, hB))
    return cv2.warpPerspective(imageA, M, (wB, hB))

def criarPanorama(imagemAlinhada1, imagemAlinhada2):
    return np.hstack((imagemAlinhada1, imagemAlinhada2))

def main(limiar, descritor, imagemA, imagemB, imagem_saida):
    print("\n--- Registro de Imagens ---")

    imageA = readImage(imagemA)
    imageB = readImage(imagemB)
    imageA, imageB = igualarTamanho(imageA, imageB)
    print(imageA.shape, imageB.shape)
    showImage("Imagem de entrada A", imageA)
    showImage("Imagem de entrada B", imageB)

    # 1) Converte a imagem para tons de cinza
    gray_imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    gray_imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    # print(gray_imageA.shape, gray_imageB.shape)
    # showImage("Imagem de entrada A gray_imageA", gray_imageA)
    # showImage("Imagem de entrada B gray_imageB", gray_imageB)

    # 2) encontrar pontos de interesse e descritores invariantes locais para o par de imagens
    ptsA, ptsB, descritoresA, descritoresB = encontrarDescritores(imageA, imageB, descritor)
    print(len(ptsA), len(ptsB), descritoresA.shape, descritoresB.shape, type(descritoresA), type(descritoresB))
    
    # 3) computar distancias (similaridades) entre cada descritor das duas imagens
    # e
    # 4) selecionar as melhores correspondencias para cada descritor de imagem (usando limiar)
    good_matches = matchDescritores(descritoresA, descritoresB, descritor, limiar)

    # 5) executar a tecnica RANSAC para estimar a matriz de homografia
    M = estimarHomografia(ptsA, ptsB, good_matches)
    print(M, M.shape)
    
    # 6) aplicar uma projecao de perspectiva (cv2.warpPerspective) para alinhar as imagens
    imagemAlinhada1 = alinhaImagem(imageA, imageB, M)
    imagemAlinhada2 = alinhaImagem(imageB, imageA, M)
    # print(imagemAlinhada1.shape)
    # print(imagemAlinhada2.shape)
    showImage("Imagem de saida", imagemAlinhada1)
    showImage("Imagem de saida", imagemAlinhada2)
    ## panorama = criarPanorama(imagemAlinhada1, imageB)
    ## showImage("Imagem de saida", panorama)

    # # 7) unir as imagens alinhadas e criar a imagem panoramica
    # # Combinar as duas imagens
    merged1 = cv2.addWeighted(imagemAlinhada1, 0.5, imageB, 0.5, 0)
    # merged2 = cv2.addWeighted(imagemAlinhada2, 0.0, imageA, 1.1, 0)
    # # merged = cv2.add(imagemAlinhada1, imageB)
    showImage("Imagem mergeada 1", merged1)
    # showImage("Imagem mergeada 2", merged2)
    # Exibir imagens
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1), plt.imshow(imageA[:, :, ::-1]), plt.title('Imagem de Origem')
    plt.subplot(1, 3, 2), plt.imshow(imageB[:, :, ::-1]), plt.title('Imagem de Destino')
    plt.subplot(1, 3, 3), plt.imshow(merged1[:, :, ::-1]), plt.title('Imagens Combinadas')
    plt.show()

    # 8) desenhar retas entre pontos correspondentes no par de imagens
    # Exibir a imagem com os matches
    img_matches = cv2.drawMatches(imageA, ptsA, imageB, ptsB, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.figure(figsize=(10, 5))
    plt.imshow(img_matches)
    plt.title("Correspondência de Descritores com Limiar")
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Registro de Imagens")

    parser.add_argument('-l', type=float, required=True, help='Limiar da correpondência')
    parser.add_argument('-d', type=str, required=True, help='Descritor (s - SIFT | su - SURF | b - BRIEF | o - ORB)')
    parser.add_argument('-a', type=str, required=True, help='Caminho da imagem de entrada A')
    parser.add_argument('-b', type=str, required=True, help='Caminho da imagem de entrada B')
    parser.add_argument('-o', type=str, required=True, help='Caminho da imagem de saída')

    args = parser.parse_args()

    print(f"Limiar de correspondência: {args.l}")
    print(f"Descritor: {args.d}")
    print(f"Imagem de entrada A: {args.a}")
    print(f"Imagem de entrada B: {args.b}")
    print(f"Imagem de saída: {args.o}")

    limiar = args.l
    descritor = args.d
    imagemA = args.a
    imagemB = args.b
    imagem_saida = args.o
    
    main(limiar, descritor, imagemA, imagemB, imagem_saida)