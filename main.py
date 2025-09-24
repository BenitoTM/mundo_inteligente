import pygame
import random
import math
from class_carnivoro import Carnivoro
from class_herbivoro import Herbivoro
from config import (
    LARGURA, ALTURA, FPS, ESCALA,
    NUM_PLANTAS, NUM_HERBIVOROS, NUM_CARNIVOROS,
    PORCENTAGEM_PARA_REPRODUCAO, FLORESTA_X, FLORESTA_Y, FLORESTA_RAIO
)

COR_FUNDO = 255
ANOITECER = True

# =========================
# CLASSE PLANTA
# =========================
class Planta:
    def __init__(self, x = None, y = None):
        if x == None:
            self.x = random.randint(0, LARGURA)
        else:
            self.x = x
        if y == None:
            self.y = random.randint(0, ALTURA)
        else:
            self.y = y
        self.raio = 5

    def desenhar(self, screen):
        pygame.draw.circle(screen, (0, 200, 0), (int(self.x), int(self.y)), self.raio * (ESCALA*2))




# =========================
# FUNÇÕES DO JOGO
# =========================

def criar_plantas():
    return [Planta() for _ in range(NUM_PLANTAS)]

def criar_herbivoros():
    return [Herbivoro() for _ in range(NUM_HERBIVOROS)]

def criar_carnivoros():
    return [Carnivoro() for _ in range(NUM_CARNIVOROS)]

def spawn_planta_aleatoria():
    if random.random() < 0.1:  # 10% de chance de nascer na zona
        # gera posição dentro do círculo
        angulo = random.uniform(0, 2 * math.pi)
        r = FLORESTA_RAIO * math.sqrt(random.random())
        x = FLORESTA_X + r * math.cos(angulo)
        y = FLORESTA_Y + r * math.sin(angulo)
    else:
        # posição aleatória normal no mapa
        x = random.randint(0, LARGURA)
        y = random.randint(0, ALTURA)
    return Planta(x, y)

def atualizar_mundo(carnivoros, herbivoros, plantas):
    herbivoros_comidos = []

    # Atualiza carnivoros
    for c in carnivoros:
        c.mover()
        alvo_comido = c.buscar_presa(herbivoros)
        if alvo_comido:
            herbivoros_comidos.append(alvo_comido)

        if c.energia > c.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and c.reproducao_cooldown <= 0:
            filho = c.buscar_reproducao(carnivoros)
            if filho:
                carnivoros.append(filho)

    for h in herbivoros_comidos:
        if h in herbivoros:
            herbivoros.remove(h)

    # Atualiza herbívoros
    for h in herbivoros:
        h.mover()
        h.fugir_de_predador(carnivoros)
        planta_comida = h.buscar_comida(plantas)
        if h.energia > h.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and h.reproducao_cooldown <= 0:
            filho = h.buscar_reproducao(herbivoros)
            if filho:
                herbivoros.append(filho)
        if planta_comida:
            plantas.remove(planta_comida)
            plantas.append(spawn_planta_aleatoria())  # nova planta aparece em outro lugar

    # Remove os mortos
    carnivoros[:] = [c for c in carnivoros if c.esta_vivo()]
    herbivoros[:] = [h for h in herbivoros if h.esta_vivo()]

def desenhar_mundo(screen, herbivoros, plantas, carnivoros):
    global COR_FUNDO, ANOITECER

    screen.fill((abs(COR_FUNDO), abs(COR_FUNDO), abs(COR_FUNDO)))  # fundo branco
    if ANOITECER:
        COR_FUNDO -= 1
        if COR_FUNDO <= 0:
            ANOITECER = False
    else:
        COR_FUNDO += 1
        if COR_FUNDO == 255:
            ANOITECER = True

    perda_de_visao = ((COR_FUNDO - 0) / (255 - 0)) * (1 - 0.5) + 0.5 # escala de 0 - 100

    # Desenha plantas
    for p in plantas:
        p.desenhar(screen)

    # Cria surface temporária para os raios de visão
    vision_surface = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # Desenha herbívoros
    for h in herbivoros:
        h.desenhar(screen, vision_surface)
        h.visao_atual = h.dna.visao * perda_de_visao

    for c in carnivoros:
        c.desenhar(screen, vision_surface)

    # Blita a surface transparente sobre a tela principal
    screen.blit(vision_surface, (0, 0))

    #contador de herbivoros
    font = pygame.font.SysFont(None, 36)
    texto1 = font.render(f"Herbívoros: {len(herbivoros)}", True, (0, 0, 0))
    screen.blit(texto1, (20, 20))

    texto2 = font.render(f"Carnívoros: {len(carnivoros)}", True, (0, 0, 0))
    screen.blit(texto2, (20, 50))

    texto3 = font.render(f"Porcentagem dia: {int(((COR_FUNDO - 0) / (255 - 0))*100)}", True, (0, 0, 0))
    screen.blit(texto3, (20, 80))

    pygame.draw.circle(screen, (150, 255, 150), (int(FLORESTA_X), int(FLORESTA_Y)), int(FLORESTA_RAIO), 2)

# =========================
# LOOP PRINCIPAL
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Mundo Genético - Herbívoros e Plantas")
    clock = pygame.time.Clock()

    plantas = criar_plantas()
    herbivoros = criar_herbivoros()
    carnivoros = criar_carnivoros()

    rodando = True
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Atualizar lógica
        atualizar_mundo(carnivoros, herbivoros, plantas)

        # Desenhar
        desenhar_mundo(screen, herbivoros, plantas, carnivoros)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
