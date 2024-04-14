import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt

def showImage(title, img):
	cv2.imshow(title, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def showFFTShift(fft_shift):
    magnitude_spectrum = 20 * np.log(np.abs(fft_shift))
    # Normaliza o espectro de magnitude para a faixa de 0-255
    magnitude_spectrum_normalized = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
    # Converte o espectro de magnitude para o tipo uint8
    magnitude_spectrum_uint8 = np.uint8(magnitude_spectrum_normalized)
    showImage("Imagem em FFT", magnitude_spectrum_uint8)

    return magnitude_spectrum_uint8

def saveImage(name, img):
	print("Salvando arquivo {}...".format(name))
	cv2.imwrite(name, img)

def etapa_1(filepath):
    # (i) abrir uma imagem de entrada convertida para escala de cinza.
    try:
        return cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    except Exception as error:
        print("Erro ao ler imagem: ", error)

def etapa_2(image):
    # (ii) aplicar a transformada rápida de Fourier.
    fft = np.fft.fft2(image)
    return etapa_3(fft)

def etapa_3(fft):
    # (iii) centralizar o espectro de frequencia.
    return np.fft.fftshift(fft)

def cria_mascara_passa_baixa(magnitude_spectrum_img, radius):
    rows, cols = magnitude_spectrum_img.shape
    center = (cols // 2, rows // 2)

    mask = np.zeros((rows, cols, 4), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return cv2.bitwise_and(magnitude_spectrum_img, mask[:, :, 0])

def cria_mascara_passa_alta(magnitude_spectrum_img, radius):
    rows, cols = magnitude_spectrum_img.shape
    center = (cols // 2, rows // 2)

    mask = magnitude_spectrum_img.copy()
    cv2.circle(mask, center, radius, 0, -1)
    return mask

def etapa_4(
    magnitude_spectrum_img, 
    high_low_radius = 60, 
    lower_band_radius = 10, 
    upper_band_radius = 60
    ):
    # (iv) criar os nucleos (mascaras) para os diferentes filtros com as mesmas 
    # dimensoes das imagens, tal que os raios dos cırculos definem as frequencias 
    # que serao atenuadas/preservadas.

    passa_baixa = cria_mascara_passa_baixa(magnitude_spectrum_img, high_low_radius)
    passa_alta = cria_mascara_passa_alta(magnitude_spectrum_img, high_low_radius)
    passa_faixa = cria_mascara_passa_baixa(cria_mascara_passa_alta(magnitude_spectrum_img, lower_band_radius), high_low_radius)
    rejeita_faixa = np.bitwise_or(passa_alta, cria_mascara_passa_baixa(magnitude_spectrum_img, lower_band_radius))

    # printando resultados
    plt.subplot(221), plt.imshow(passa_baixa, cmap='gray')
    plt.title('Passa-Baixa'), plt.xticks([]), plt.yticks([])
    plt.subplot(222), plt.imshow(passa_alta, cmap='gray')
    plt.title('Passa-Alta'), plt.xticks([]), plt.yticks([])
    plt.subplot(223), plt.imshow(passa_faixa, cmap='gray')
    plt.title('Passa-Faixa'), plt.xticks([]), plt.yticks([])
    plt.subplot(224), plt.imshow(rejeita_faixa, cmap='gray')
    plt.title('Rejeita-Faixa'), plt.xticks([]), plt.yticks([])
    plt.suptitle("filtros (nucleos)")
    plt.show()

    return passa_baixa, passa_alta, passa_faixa, rejeita_faixa

def etapa_5(fft_shift, filtro):
    # (v) aplicar cada filtro por meio da multiplicação entre o espectro de 
    # frequencia e a mascara do filtro.
    resultado_filtro = fft_shift * filtro

    return resultado_filtro

def compressao_por_remocao_de_coeficientes(fft_shift_filtrado, threshold):
    fft_copy = fft_shift_filtrado.copy()
    magnitude = np.abs(fft_copy)
    fft_copy[magnitude < int(threshold)] = 0
    return fft_copy

def etapa_6(fft_shift_filtrado, title):
    # (vi) aplicar a transformada inversa de Fourier para converter o espectro de 
    # frequencia filtrada de volta para o domınio espacial, gerando a imagem filtrada.
    resultado = np.abs(np.fft.ifft2(np.fft.ifftshift(fft_shift_filtrado)))

    # Normaliza o espectro de magnitude para a faixa de 0-255
    resultado_normalized = cv2.normalize(resultado, None, 0, 255, cv2.NORM_MINMAX)
    # Converte o espectro de magnitude para o tipo uint8
    resultado_uint8 = np.uint8(resultado_normalized)

    # printando resultados
    showImage(title, resultado_uint8)

    return resultado_uint8

def etapa_7(
    title,
    gray_image,
    resultado_passa_baixa, 
    resultado_passa_alta, 
    resultado_passa_faixa, 
    resultado_rejeita_faixa):
    # (vii) visualizar e analisar os resultados.
    hist_gray_image = cv2.calcHist([np.uint8(gray_image)], [0], None, [256], [0, 256])
    hist_passa_baixa = cv2.calcHist([np.uint8(resultado_passa_baixa)], [0], None, [256], [0, 256])
    hist_passa_alta = cv2.calcHist([np.uint8(resultado_passa_alta)], [0], None, [256], [0, 256])
    hist_passa_faixa = cv2.calcHist([np.uint8(resultado_passa_faixa)], [0], None, [256], [0, 256])
    hist_rejeita_faixa = cv2.calcHist([np.uint8(resultado_rejeita_faixa)], [0], None, [256], [0, 256])

    # printa resultados
    plt.figure(figsize=(10, 8))

    plt.subplot(221), plt.imshow(gray_image, cmap='gray')
    plt.title('Imagem original'), plt.xticks([]), plt.yticks([])
    plt.subplot(222), plt.plot(hist_gray_image, color='black')
    plt.title('Histograma - Imagem original'), plt.xlim([0, 256])

    plt.show()

    plt.figure(figsize=(10, 8))

    plt.subplot(221), plt.imshow(resultado_passa_baixa, cmap='gray')
    plt.title('Passa-Baixa' + title), plt.xticks([]), plt.yticks([])
    plt.subplot(222), plt.plot(hist_passa_baixa, color='black')
    plt.title('Histograma - Passa-Baixa' + title), plt.xlim([0, 256])
    
    plt.subplot(223), plt.imshow(resultado_passa_alta, cmap='gray')
    plt.title('Passa-Alta' + title), plt.xticks([]), plt.yticks([])
    plt.subplot(224), plt.plot(hist_passa_alta, color='black')
    plt.title('Histograma - Passa-Alta' + title), plt.xlim([0, 256])

    plt.show()
    
    plt.figure(figsize=(10, 8))
    
    plt.subplot(221), plt.imshow(resultado_passa_faixa, cmap='gray')
    plt.title('Passa-Faixa' + title), plt.xticks([]), plt.yticks([])
    plt.subplot(222), plt.plot(hist_passa_faixa, color='black')
    plt.title('Histograma - Passa-Faixa' + title), plt.xlim([0, 256])
    
    plt.subplot(223), plt.imshow(resultado_rejeita_faixa, cmap='gray')
    plt.title('Rejeita-Faixa' + title), plt.xticks([]), plt.yticks([])
    plt.subplot(224), plt.plot(hist_rejeita_faixa, color='black')
    plt.title('Histograma - Rejeita-Faixa' + title), plt.xlim([0, 256])
    
    plt.show()

def main(imagem_entrada, threshold):
    print("--- Análise do uso de FFT em imagens digitais ---")
    
    # etapa 1 (le a imagem e converte para tons de cinza)
    gray_image = etapa_1(imagem_entrada)
    showImage("Imagem Original (em tons de cinza)", gray_image)
    # salvando imagens p/ relatorio
    saveImage("imagem_original.png", gray_image)

    # etapa 2 e 3 (converter dominio espacial para fft)
    fft_shift = etapa_2(gray_image)
    magnitude_spectrum = showFFTShift(fft_shift)
    # salvando imagens p/ relatorio
    saveImage("imagem_FFT.png", gray_image)
    
    # etapa 4 (cria os filtros)
    passa_baixa, passa_alta, passa_faixa, rejeita_faixa = etapa_4(magnitude_spectrum)
    # salvando imagens p/ relatorio
    saveImage("filtro_passa_baixa.png", passa_baixa)
    saveImage("filtro_passa_alta.png", passa_alta)
    saveImage("filtro_passa_faixa.png", passa_faixa)
    saveImage("filtro_rejeita_faixa.png", rejeita_faixa)

    # etapa 5 (aplica filtro na imagem)
    fft_shift_filtrado_passa_baixa = etapa_5(fft_shift, passa_baixa)
    fft_shift_filtrado_passa_alta = etapa_5(fft_shift, passa_alta)
    fft_shift_filtrado_passa_faixa = etapa_5(fft_shift, passa_faixa)
    fft_shift_filtrado_rejeita_faixa = etapa_5(fft_shift, rejeita_faixa)

    # etapa 6 (converter de fft para dominio espacial)
    resultado_filtrado_passa_baixa = etapa_6(fft_shift_filtrado_passa_baixa, "Passa-Baixa")
    resultado_filtrado_passa_alta = etapa_6(fft_shift_filtrado_passa_alta, "Passa-Alta")
    resultado_filtrado_passa_faixa = etapa_6(fft_shift_filtrado_passa_faixa, "Passa-Faixa")
    resultado_filtrado_rejeita_faixa = etapa_6(fft_shift_filtrado_rejeita_faixa, "Rejeita-Faixa")
    # salvando imagens p/ relatorio
    saveImage("filtro_passa_baixa_SEM_COMPRESSAO.png", resultado_filtrado_passa_baixa)
    saveImage("filtro_passa_alta_SEM_COMPRESSAO.png", resultado_filtrado_passa_alta)
    saveImage("filtro_passa_faixa_SEM_COMPRESSAO.png", resultado_filtrado_passa_faixa)
    saveImage("filtro_rejeita_faixa_SEM_COMPRESSAO.png", resultado_filtrado_rejeita_faixa)

    # etapa 6 com aplicacao de compressao
    resultado_filtrado_passa_baixa_compress = etapa_6(compressao_por_remocao_de_coeficientes(fft_shift_filtrado_passa_baixa, threshold), "Passa-Baixa Com Compressao")
    resultado_filtrado_passa_alta_compress = etapa_6(compressao_por_remocao_de_coeficientes(fft_shift_filtrado_passa_alta, threshold), "Passa-Alta Com Compressao")
    resultado_filtrado_passa_faixa_compress = etapa_6(compressao_por_remocao_de_coeficientes(fft_shift_filtrado_passa_faixa, threshold), "Passa-Faixa Com Compressao")
    resultado_filtrado_rejeita_faixa_compress = etapa_6(compressao_por_remocao_de_coeficientes(fft_shift_filtrado_rejeita_faixa, threshold), "Rejeita-Faixa Com Compressao")
    # salvando imagens p/ relatorio
    saveImage("filtro_passa_baixa_COM_COMPRESSAO.png", resultado_filtrado_passa_baixa_compress)
    saveImage("filtro_passa_alta_COM_COMPRESSAO.png", resultado_filtrado_passa_alta_compress)
    saveImage("filtro_passa_faixa_COM_COMPRESSAO.png", resultado_filtrado_passa_faixa_compress)
    saveImage("filtro_rejeita_faixa_COM_COMPRESSAO.png", resultado_filtrado_rejeita_faixa_compress)

    # etapa 7 (plotar histogramas)
    etapa_7(" sem Compressão", gray_image, resultado_filtrado_passa_baixa, resultado_filtrado_passa_alta, resultado_filtrado_passa_faixa, resultado_filtrado_rejeita_faixa)
    etapa_7(" com Compressão", gray_image, resultado_filtrado_passa_baixa_compress, resultado_filtrado_passa_alta_compress, resultado_filtrado_passa_faixa_compress, resultado_filtrado_rejeita_faixa_compress)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Use: python fft.py <imagem_entrada.png> threshold")
        sys.exit(1)
    imagem_entrada = sys.argv[1]
    threshold = sys.argv[2]
    
    main(imagem_entrada, threshold)