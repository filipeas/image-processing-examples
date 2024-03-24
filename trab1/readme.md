# Implementação de um algoritmo de esteganografia em imagens digitais

- Neste trabalho, a esteganografia deve alterar os bits da mensagem a ser oculta 
nos bits menos significativos de cada um dos tres canais de cor da imagem. 
Dessa forma, cada pixel da imagem pode armazenar 3 bits de informacao, tal que 
a imagem pode comportar tres vezes o numero de pixels que ela possui.

- Implemente a tecnica de esteganografia em imagens coloridas por meio da alteracao 
de seus bits menos significativos. O programa deve codificar e decodificar uma 
mensagem de texto levando-se em conta os bits em qualquer um dos tres planos de 
bits menos significativos.

- O processo de codificacao deve converter cada caractere da mensagem para sua palavra binaria 
correspondente (codigo ASCII) e alterar os bits menos significativos da imagem com os bits da 
mensagem. O processo de decodificacao deve recuperar a informacao binaria da imagem e gerar 
a mensagem de texto.

- Para ajudar a determinar se uma imagem contem uma mensagem oculta em seus pixels, mostre 
(separadamente) os planos de bits 0, 1, 2 e 7 de cada canal de cor (vermelho, verde e azul) 
da imagem apos o processo de esteganografia.

## Informações dos parametros
- codificar.py: programa que oculta mensagem de texto na imagem.
- decodificar.py: programa que recupera mensagem de texto da imagem.
- imagem_entrada.png: imagem no formato PNG em que sera embutida a mensagem.
- imagem_saida.png: imagem no formato PNG com mensagem embutida.
- texto_entrada.txt: arquivo-texto contendo mensagem a ser oculta.
- texto_saida.txt: arquivo-texto contendo mensagem recuperada.
- plano_bits: tres planos de bits menos significativos representados pelos valores 0, 1 ou 2.

## Entrada de dados
- Imagens na pasta ``` imgs/ ```.

## Saída de dados
- Imagens no formato PNG.
- Resultados intermediarios podem ser tambem exibidos na tela. (histogramas, Kb da imagem de entrada antes da esteganografia, Kb do texto codificado, Kb da imagem após a esteganografia, print da imagem nos 3 canais nas faixas de bits 0, 1, 2 e 7).

## Antes de executar
- Tenha o python na versão 3.12.2
- Tenha as seguintes libs em sua máquina:
    - sys
    - numpy (pip install numpy)
    - opencv (pip install opencv-python)
    - matplotlib (pip install -U matplotlib)

## Como executar
- Para codificar a mensagem na imagem:
    - ``` python codificar.py <imagem_entrada.png> <texto_entrada.txt> [<plano_bits>] <imagem_saida.png> ```
    - Onde:
        - ``` <imagem_entrada.png> ``` é a imagem de entrada que será usada na esteganografia.
        - ``` <texto_entrada.txt> ``` é o arquivo de texto no formato .txt que será usado para ser escondido na imagem.
        - ``` [<plano_bits] ``` é uma lista de bits a serem usados na codificação do texto. Então é possível mandar mais de um valor. Por exemplo:
            - ``` python codificar.py <imagem_entrada.png> <texto_entrada.txt> 0 1 2 <imagem_saida.png> ```
        - ``` <imagem_saida.png> ``` é a imagem de saída da esteganografia, já com o texto escondido na imagem.

- Para decodificar a mensagem na imagem:
    - ``` python decodificar.py <imagem_saida.png> [<plano_bits>] <texto_saida.txt> ```

- Onde:
    - ``` <imagem_saida.png> ``` é a imagem de saída da codificação, ou seja, a imagem esteganografada.
    - ``` [<plano_bits] ``` é uma lista de bits a serem usados na decodificação do texto na imagem. Tenha certeza de usar os mesmos bits da codificação. Assim como na codificação, é possível mandar mais de um bit. Por exemplo:
        - ``` python decodificar.py <imagem_saida.png> 1 2 <texto_saida.txt> ```
    - ``` <texto_saida.txt> ``` é o arquivo .txt que salvará o texto oculto da imagem, após o processo de decodificação.

## Relatório
### Descrição dos algoritmos e estruturas de dados utilizados
### Considerações adotadas na solução do problema
### Testes executados
### Limitações ou situações especiais não tratadas pelo programa