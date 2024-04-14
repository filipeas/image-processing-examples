# Análise do uso de FFT (Fast Furier Transform) em imagens digitais

- O objetivo deste trabalho é aplicar a transformada rápida de Fourier (do ingles, Fast Fourier Transform - FFT) em imagens digitais, explorando o processamento de imagens no domínio de frequencia.

- Aplique os filtros passa-baixa, passa-alta, passa-faixa e rejeita-faixa em imagens monocromaticas por meio do espectro de Fourier. A componente de frequencia-zero deve ser transladada para o centro do espectro. Diferentes valores de nucleos dos filtros devem ser experimentados e analisados.

- O processo de filtragem no domınio da frequencia é resumido por meio dos seguintes passos: 
    - (i) abrir uma imagem de entrada convertida para escala de cinza; 
    - (ii) aplicar a transformada rapida de Fourier;
    - (iii) centralizar o espectro de frequencia; 
    - (iv) criar os nucleos (mascaras) para os diferentes filtros com as mesmas dimensoes das imagens, tal que os raios dos cırculos definem as frequencias que serao atenuadas/preservadas;
    - (v) aplicar cada filtro por meio da multiplicacão entre o espectro de frequencia e a mascara do filtro;
    - (vi) aplicar a transformada inversa de Fourier para converter o espectro de frequencia filtrada de volta para o domınio espacial, gerando a imagem filtrada;
    - (vii) visualizar e analisar os resultados.

- Para o processo de compressao no dominio de frequncia, diferentes estrategias podem ser aplicadas as imagens, tal como a remocao de coeficientes cujas magnitudes sao menores do que um determinado limiar (atribuindo-se valores iguais a 0 a eles). Apresente os histogramas das imagens antes e apos a compressao.

## Entrada de dados
- Imagens na pasta ``` imgs/ ```.

## Saída de dados
- Imagens no formato **PNG** na raíz do projeto, junto com histogramas e filtros.

## Antes de executar
- Tenha o python na versão 3.12.2
- Tenha as seguintes libs em sua máquina:
    - sys
    - numpy (pip install numpy)
    - opencv (pip install opencv-python)
    - matplotlib (pip install -U matplotlib)

## Como executar
- Para executar o programa faça:
    - ``` python fft.py <imagem_entrada.png> threshold ```
        - Onde:
            - imagem_entrada.png: é o caminho até a imagem a ser usada no experimento.
            - threshold: é o limiar de compressão usado na imagem.

## Relatório
- Acesse o arquivo relatório.pdf para ver mais detalhes relatadas durante o processo de implementação.