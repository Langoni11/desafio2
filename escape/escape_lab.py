"""
Laboratório: Luz, Percepção e Digitalização

Questão: "Como a quantização de cores e a discretização espacial (aliasing)
comprometeriam a imersão visual do jogador na nossa caverna?"

Resposta:
Na caverna, a imagem é dominada por sombras e gradientes suaves de luz (tochas,
brilho nas paredes). A quantização de intensidade (atividade 4) reduz o número
de níveis de cinza disponíveis: ao truncar para 4 tons, o gradiente contínuo
vira degraus bruscos (color banding). Justamente nas regiões escuras, onde o
olho é sensível a pequenas variações, esses blocos aparecem como faixas
artificiais e destroem a sensação de profundidade e de penumbra.

A discretização espacial (atividade 3) descarta informação ao reduzir a
resolução: detalhes finos, como texturas de pedra, bordas e inimigos
distantes, somem ou se fundem. Ao ampliar de volta com INTER_NEAREST, o que
sobra são blocos quadrados e bordas serrilhadas (aliasing), e a informação
perdida não volta mais (processo irreversível). O jogador passa a perceber a
"malha" de pixels em vez de uma pedra ou uma criatura, o que quebra a ilusão
de que está em um ambiente real.

Além disso, a atividade 2 mostra que a percepção de cor depende da biologia: se
a paleta do jogo depender de verde e vermelho para distinguir elementos
importantes, jogadores daltônicos perdem informação. Combinados, esses efeitos
fazem a caverna parecer artificial e menos legível, comprometendo a imersão.
"""

import os

import cv2
import numpy as np


CAMINHO_IMAGEM = "imagem.jpg"


def carregar_imagem():
    img = cv2.imread(CAMINHO_IMAGEM)
    if img is None:
        print(f"'{CAMINHO_IMAGEM}' não encontrada; usando imagem sintética.")
        h, w = 400, 600
        x = np.linspace(0, 255, w, dtype=np.uint8)
        y = np.linspace(0, 255, h, dtype=np.uint8)
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:, :, 0] = x[np.newaxis, :]            # azul varia na horizontal
        img[:, :, 1] = y[:, np.newaxis]            # verde varia na vertical
        img[:, :, 2] = 255 - x[np.newaxis, :]      # vermelho varia ao contrário
        cv2.circle(img, (w // 2, h // 2), 100, (40, 200, 230), -1)
    return img


def mostrar(titulo, imagem):
    cv2.imshow(titulo, imagem)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# 1. A Forja de Luz (Sistema RGB Aditivo)
# ---------------------------------------------------------------------------
def atividade_1():
    tela = np.zeros((400, 400, 3), dtype=np.uint8)  # breu total

    raio = 90
    # Cada círculo é desenhado em uma máscara 2D e atribuído a um único canal (BGR).
    mascara_azul = np.zeros((400, 400), dtype=np.uint8)
    mascara_verde = np.zeros((400, 400), dtype=np.uint8)
    mascara_vermelha = np.zeros((400, 400), dtype=np.uint8)

    cv2.circle(mascara_vermelha, (170, 170), raio, 255, -1)  # topo esquerdo
    cv2.circle(mascara_verde, (230, 170), raio, 255, -1)     # topo direito
    cv2.circle(mascara_azul, (200, 230), raio, 255, -1)      # base

    tela[:, :, 0] = mascara_azul      # canal B
    tela[:, :, 1] = mascara_verde     # canal G
    tela[:, :, 2] = mascara_vermelha  # canal R

    # Justificativa: o sistema RGB é ADITIVO. A tela emite luz, e as intensidades
    # de cada canal se somam. Onde há sobreposição, os canais ativos se combinam:
    #   Verde + Azul             = (255, 255, 0) -> ciano
    #   Vermelho + Azul          = (255, 0, 255) -> magenta
    #   Vermelho + Verde         = (0, 255, 255) -> amarelo
    #   Vermelho + Verde + Azul  = (255, 255, 255) -> branco
    # Os três tipos de cone da retina (S, M, L) são estimulados em conjunto,
    # e o cérebro interpreta essa mistura como a cor correspondente.
    mostrar("1 - RGB aditivo", tela)


# ---------------------------------------------------------------------------
# 2. A Maldição do Labirinto (Daltonismo)
# ---------------------------------------------------------------------------
def atividade_2(img):
    daltonico = img.copy()
    daltonico[:, :, 1] = 0  # zera o canal verde (BGR: índice 1 = G)
    lado_a_lado = np.hstack((img, daltonico))
    mostrar("2 - Original (esq.) vs sem canal verde (dir.)", lado_a_lado)


# ---------------------------------------------------------------------------
# 3. O Efeito Retro (Amostragem e Discretização Espacial)
# ---------------------------------------------------------------------------
def atividade_3(img):
    altura, largura = img.shape[:2]
    pequena = cv2.resize(img, None, fx=0.05, fy=0.05)  # achata a resolução
    restaurada = cv2.resize(pequena, (largura, altura),
                            interpolation=cv2.INTER_NEAREST)
    # A informação descartada na redução não pode ser recuperada: o INTER_NEAREST
    # apenas replica pixels, gerando blocos (aliasing).
    mostrar("3 - Aliasing (INTER_NEAREST)", restaurada)


# ---------------------------------------------------------------------------
# 4. Visão Noturna (Quantização de Intensidade)
# ---------------------------------------------------------------------------
def atividade_4(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    quantizada = (cinza // 64) * 64  # apenas 4 níveis: 0, 64, 128, 192
    mostrar("4 - Quantização (color banding)", np.hstack((cinza, quantizada)))


# ---------------------------------------------------------------------------
# 5. O Enigma do Espelho (Óptica Geométrica)
# ---------------------------------------------------------------------------
def atividade_5():
    tela = np.zeros((300, 300, 3), dtype=np.uint8)
    meio = 150

    cv2.line(tela, (meio, 0), (meio, 299), (255, 255, 255), 2)  # espelho
    cv2.line(tela, (0, 0), (meio, meio), (0, 255, 255), 2)      # raio incidente (amarelo, BGR)

    recorte = tela[:, :meio].copy()          # região esquerda
    espelhado = cv2.flip(recorte, 1)         # espelhamento horizontal
    tela[:, meio:] = espelhado               # cola no lado direito

    cv2.line(tela, (meio, 0), (meio, 299), (255, 255, 255), 2)  # redesenha o espelho

    # O raio refletido é simétrico ao incidente em relação à normal (perpendicular
    # ao espelho): ângulo de incidência = ângulo de reflexão.
    mostrar("5 - Lei da reflexão", tela)


# ---------------------------------------------------------------------------
# 6. O Artesão Digital (Pixel Art na Matriz)
# ---------------------------------------------------------------------------
def atividade_6():
    tela = np.full((16, 16, 3), 30, dtype=np.uint8)  # cinza chumbo

    PRETO = [0, 0, 0]
    BRANCO = [255, 255, 255]
    AMARELO = [0, 255, 255]   # BGR
    ROSA = [180, 105, 255]    # BGR

    tela[5:14, 4:12] = PRETO      # corpo/cabeça
    tela[3:5, 4:6] = PRETO        # orelha esquerda
    tela[3:5, 10:12] = PRETO      # orelha direita
    tela[10:13, 12:14] = PRETO    # rabo
    tela[8:11, 6:10] = BRANCO     # focinho
    tela[7, 5] = AMARELO          # olho esquerdo
    tela[7, 10] = AMARELO         # olho direito
    tela[8, 7:9] = ROSA           # nariz

    grande = cv2.resize(tela, (320, 320), interpolation=cv2.INTER_NEAREST)
    mostrar("6 - Gato em pixel art", grande)


if __name__ == "__main__":
    imagem = carregar_imagem()
    atividade_1()
    atividade_2(imagem)
    atividade_3(imagem)
    atividade_4(imagem)
    atividade_5()
    atividade_6()
