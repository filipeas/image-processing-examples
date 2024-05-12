# Algoritmos de alinamento automático de imagens de documentos

Um problema frequente que ocorre no processo de digitalizacao  é o desalinhamento do documento, ou seja, o posicionamento do papel com uma inclinacao diferente do eixo do digitalizador. A corre cao da inclinacao  é fundamental para o adequado funcionamento de sistemas de reconhecimento o ́tico de caracteres.

Dois algoritmos para deteccao e correcao de inclinacao de documentos devem ser implementados neste trabalho, um baseado em projecao horizontal e outro baseado na transformada de Hough.

## Técnica baseada em projeçao horizontal

A deteccao de inclinacao baseada em projecao horizontal é realizada variando o aˆngulo testado e proje- tando a quantidade de pixels pretos em cada linha linha de texto. O angulo escolhido é aquele que otimiza uma funcao objetivo calculada sobre o perfil da projecao horizontal. Um exemplo de funcao objetivo é a soma dos quadrados das diferen ̧cas dos valores em células adjacentes do perfil de projecao.

## Técnica baseada na transformada de hough

A deteccao de inclinacao da imagem baseada na transformada de Hough assume que os caracteres de texto estao alinhados. As linhas formadas pelas regio ̃es de texto sa ̃o localizadas por meio da transformada de Hough, a qual converte pares de coordenadas (x,y) da imagem em curvas nas coordenadas polares (ρ, θ).

- Dica do prof.: Para a tecnica baseada em transformada Hough, aplique inicialmente um detector de bordas (por exemplo, Sobel) na imagem de entrada para gerar um mapa de bordas, o qual podera ser utilizado pela transformada para encontrar linhas na imagem.

## Entrada de dados
- Imagens na pasta ``` imgs/ ```.

## Saída de dados
- O codigo deve retornar o angulo (em graus) detectado para alinhar a imagem de entrada com respeito ao eixo horizontal, bem como a imagem apos a correcao do angulo de inclinacao.

## Antes de executar
- Tenha o python na versão 3.12.2
- Tenha as seguintes libs em sua máquina:
    - sys
    - numpy (pip install numpy)
    - opencv (pip install opencv-python)
    - matplotlib (pip install -U matplotlib)
    - Tesseract OCR

## Como executar
- Para executar o programa faça:
    - ``` python alinhar.py imagem_entrada.png modo imagem_saida.png ```
        Onde:
            - **alinhar.py**: programa que realiza o alinhamento da imagem.
            - **imagem_entrada.png**: imagem no formato PNG antes do alinhamento.
            - **modo**: tecnica utilizada no alinhamento da imagem (0: projecao horizontal e 1: transformada de hough).
            - **imagem_saida.png**: imagem no formato PNG apo ́s o alinhamento.

