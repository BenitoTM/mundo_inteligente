import pygame
import random
import math

# =========================
# CONFIGURAÇÃO DO FITNESS -> usado para o tamanho visual
# =========================
PESO_DANO = 1.0
PESO_VELOCIDADE = 1.0
PESO_VISAO = 0.02
PESO_ENERGIA = 0.05

VAR_DANO = 0.2
VAR_VELOCIDADE = 0.3
VAR_VISAO = 4
VAR_ENERGIA_MAX = 5

# Calcula os fitness extremos possíveis para normalizar
FITNESS_MIN = (0.5 * PESO_DANO) + (0.5 * PESO_VELOCIDADE) + (50 * PESO_VISAO) + (80 * PESO_ENERGIA)
FITNESS_MAX = (2.0 * PESO_DANO) + (3.0 * PESO_VELOCIDADE) + (200 * PESO_VISAO) + (200 * PESO_ENERGIA)

RAIO_MIN = 6
RAIO_MAX = 20

COR_FUNDO = 255
ANOITECER = True

# =========================
# CONFIGURAÇÕES DO MUNDO
# =========================
ESCALA = 0.3  # 30% do tamanho original
LARGURA = 2400
ALTURA = 1000
FPS = 60

FLORESTA_X = 300
FLORESTA_Y = 500
FLORESTA_RAIO = 300

NUM_PLANTAS = 200
NUM_HERBIVOROS = 140
NUM_CARNIVOROS = 15
TEMPO_PARA_REPRODUCAO = 10

PORCENTAGEM_PARA_REPRODUCAO = 0.6

# =========================
# CLASSE DNA
# =========================
class DNA:
    def __init__(self, dano=None, velocidade=None, visao=None, energia_max=None):
        # Se não foi passado nada, cria valores iniciais aleatórios
        self.dano = dano if dano is not None else random.uniform(50, 200)
        self.velocidade = velocidade if velocidade is not None else random.uniform(0.5, 3.0)
        self.visao = visao if visao is not None else random.uniform(50, 150)
        self.energia_max = energia_max if energia_max is not None else random.uniform(80, 200)

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
# CLASSE HERBÍVORO
# =========================
class Herbivoro:
    def __init__(self):
        self.dna = DNA()
        self.x = random.randint(0, LARGURA)
        self.y = random.randint(0, ALTURA)
        self.visao_atual = self.dna.visao
        self.energia = self.dna.energia_max
        self.raio = self.calcular_raio_por_fitness()
        self.direcao = random.uniform(0, 2*math.pi)  # Ângulo inicial
        self.reproducao_cooldown = 0  # contador de segundos até poder reproduzir de novo

    def calcular_fitness(self):
        return (
                self.dna.dano * PESO_DANO +
                self.dna.velocidade * PESO_VELOCIDADE +
                self.visao_atual * PESO_VISAO +
                self.dna.energia_max * PESO_ENERGIA
        )

    def calcular_raio_por_fitness(self): #usado para calcular tamanho do ind
        fitness = self.calcular_fitness()
        # Normaliza o fitness para [0,1]
        normalizado = (fitness - FITNESS_MIN) / (FITNESS_MAX - FITNESS_MIN)
        normalizado = max(0, min(1, normalizado))  # garante entre 0 e 1
        return RAIO_MIN + normalizado * (RAIO_MAX - RAIO_MIN)

    def mover(self):
        # Movimento aleatório (exploração)
        self.direcao += random.uniform(-0.2, 0.2)
        self.x += self.dna.velocidade * math.cos(self.direcao)
        self.y += self.dna.velocidade * math.sin(self.direcao)

        # Manter dentro dos limites do mundo
        self.x = max(0, min(self.x, LARGURA))
        self.y = max(0, min(self.y, ALTURA))

        # Energia diminui com o tempo (e mais rápido se ele é rápido)
        self.energia -= 0.05 * self.dna.velocidade

        # Atualiza o cooldown da reprodução
        if self.reproducao_cooldown > 0:
            self.reproducao_cooldown -= 1 / FPS  # diminui em segundos

    def buscar_comida(self, plantas):
        alvo = None
        menor_distancia = self.visao_atual  # só vê até a distância de visão

        for planta in plantas:
            dist = math.dist((self.x, self.y), (planta.x, planta.y))
            if dist < menor_distancia:
                menor_distancia = dist
                alvo = planta

        # Se encontrou uma planta dentro do raio de visão, vai em direção a ela
        if alvo:
            self.direcao = math.atan2(alvo.y - self.y, alvo.x - self.x)

            # Se já está em cima da planta, come
            if menor_distancia < self.raio + alvo.raio:
                self.comer()
                return alvo  # retorna a planta comida

        return None

    def buscar_reproducao(self, herbivoros):
        alvo = None
        menor_distancia = self.visao_atual  # só vê até a distância de visão

        for h in herbivoros:
            if h is self:
                continue
            dist = math.dist((self.x, self.y), (h.x, h.y))
            if dist < menor_distancia and h.energia > h.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and self.energia > self.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO:
                menor_distancia = dist
                alvo = h

        # Se encontrou uma planta dentro do raio de visão, vai em direção a ela
        if alvo:
            self.direcao = math.atan2(alvo.y - self.y, alvo.x - self.x)

            # Se já está em cima da planta, come
            if menor_distancia < self.raio + alvo.raio:
                # Reproduz apenas se o parceiro também tem energia suficiente
                if alvo.energia > alvo.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and self.energia > self.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO:
                    return self.reproduzir(alvo)

        return None

    def reproduzir(self, outro_pai):
        pior_dano = min(self.dna.dano, outro_pai.dna.dano)
        melhor_dano = max(self.dna.dano, outro_pai.dna.dano)

        pior_velocidade = min(self.dna.velocidade, outro_pai.dna.velocidade)
        melhor_velocidade = max(self.dna.velocidade, outro_pai.dna.velocidade)

        pior_visao = min(self.dna.visao, outro_pai.dna.visao)
        melhor_visao = max(self.dna.visao, outro_pai.dna.visao)

        pior_energia_max = min(self.dna.energia_max, outro_pai.dna.energia_max)
        melhor_energia_max = max(self.dna.energia_max, outro_pai.dna.energia_max)

        dna_filho = DNA(
            dano = random.uniform(pior_dano - VAR_DANO, melhor_dano + VAR_DANO),
            velocidade = random.uniform(pior_velocidade - VAR_VELOCIDADE, melhor_velocidade + VAR_VELOCIDADE),
            visao = random.uniform(pior_visao - VAR_VISAO, melhor_visao + VAR_VISAO),
            energia_max = random.uniform(pior_energia_max - VAR_ENERGIA_MAX, melhor_energia_max + VAR_ENERGIA_MAX)
        )

        filho = Herbivoro()

        filho.dna = dna_filho
        filho.x = self.x
        filho.y = self.y
        filho.reproducao_cooldown = 100
        filho.energia = filho.dna.energia_max

        self.energia *= 0.5
        self.reproducao_cooldown = TEMPO_PARA_REPRODUCAO/2
        outro_pai.energia *= 0.5
        outro_pai.reproducao_cooldown = TEMPO_PARA_REPRODUCAO/2
        return filho


    def comer(self):
        self.energia = self.dna.energia_max
        if self.reproducao_cooldown >= 5:
            self.reproducao_cooldown -= 5

    def esta_vivo(self):
        return self.energia > 0

    def desenhar(self, screen, vision_surface):
        # Desenha o raio de visão semi-transparente na surface temporária
        pygame.draw.circle(
            vision_surface,
            (150, 150, 150, 40),  # cinza claro com alpha
            (int(self.x), int(self.y)),
            int(self.visao_atual * ESCALA)
        )

        raio_atual = self.get_raio_atual() * ESCALA
        # Desenha o herbívoro (azul)
        pygame.draw.circle(screen, (0, 0, 255), (int(self.x), int(self.y)), int(raio_atual))

    def get_raio_atual(self):
        # Escala do tamanho base (fitness) de acordo com a energia restante
        percentual_energia = self.energia / self.dna.energia_max  # vai de 0 a 1
        percentual_energia = max(0.2, percentual_energia)  # nunca menor que 20% do tamanho
        return self.raio * percentual_energia

    def fugir_de_predador(self, carnivoros):
        predador = None
        menor_distancia = self.visao_atual  # só vê até a distância de visão

        for c in carnivoros:
            dist = math.dist((self.x, self.y), (c.x, c.y))
            if dist < menor_distancia:
                menor_distancia = dist
                predador = c

        # Se encontrou uma predador dentro do raio de visão, vai contra sua direção
        if predador:
            self.direcao = math.atan2(predador.y - self.y, predador.x - self.x) + math.pi

# =========================
# CLASSE CARNIVORO
# =========================

class Carnivoro:
    def __init__(self):
        self.dna = DNA()
        self.x = random.randint(0, LARGURA)
        self.y = random.randint(0, ALTURA)
        self.energia = self.dna.energia_max
        self.velocidade_atual = self.dna.velocidade
        self.raio = self.calcular_raio_por_fitness()
        self.direcao = random.uniform(0, 2*math.pi)  # Ângulo inicial
        self.reproducao_cooldown = 0  # contador de segundos até poder reproduzir de novo


    def calcular_fitness(self):
        return (
                self.dna.dano * PESO_DANO +
                self.velocidade_atual * PESO_VELOCIDADE +
                self.dna.visao * PESO_VISAO +
                self.dna.energia_max * PESO_ENERGIA
        )

    def calcular_raio_por_fitness(self): #usado para calcular tamanho do ind
        fitness = self.calcular_fitness()
        # Normaliza o fitness para [0,1]
        normalizado = (fitness - FITNESS_MIN) / (FITNESS_MAX - FITNESS_MIN)
        normalizado = max(0, min(1, normalizado))  # garante entre 0 e 1
        return RAIO_MIN + normalizado * (RAIO_MAX - RAIO_MIN)

    def mover(self):
        # Movimento aleatório (exploração)
        self.direcao += random.uniform(-0.2, 0.2)
        self.x += self.velocidade_atual * math.cos(self.direcao)
        self.y += self.velocidade_atual * math.sin(self.direcao)

        # Manter dentro dos limites do mundo
        self.x = max(0, min(self.x, LARGURA))
        self.y = max(0, min(self.y, ALTURA))

        # Energia diminui com o tempo (e mais rápido se ele é rápido)
        self.energia -= 0.05 * self.velocidade_atual

        # Atualiza o cooldown da reprodução
        if self.reproducao_cooldown > 0:
            self.reproducao_cooldown -= 1 / FPS  # diminui em segundos

    def buscar_presa(self, herbivoros):
        alvo = None
        menor_distancia = self.dna.visao  # só vê até a distância de visão

        for h in herbivoros:
            dist = math.dist((self.x, self.y), (h.x, h.y))
            if dist < menor_distancia:
                menor_distancia = dist
                alvo = h

        # Se encontrou uma planta dentro do raio de visão, vai em direção a ela
        if alvo:
            self.direcao = math.atan2(alvo.y - self.y, alvo.x - self.x)

            # Se já está em cima da planta, come
            if menor_distancia < self.raio + alvo.raio:
                self.comer()
                return alvo  # retorna o herbivoro que foi comido

        return None

    def buscar_reproducao(self, carnivoros):
        alvo = None
        menor_distancia = self.dna.visao  # só vê até a distância de visão

        for c in carnivoros:
            if c is self:
                continue
            dist = math.dist((self.x, self.y), (c.x, c.y))
            if dist < menor_distancia and c.energia > c.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and self.energia > self.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO:
                menor_distancia = dist
                alvo = c

        # Se encontrou um carnivoro dentro do raio de visão, vai em direção a ele
        if alvo:
            self.direcao = math.atan2(alvo.y - self.y, alvo.x - self.x)

            # Se já está em cima da planta, come
            if menor_distancia < self.raio + alvo.raio:
                # Reproduz apenas se o parceiro também tem energia suficiente
                if alvo.energia > alvo.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO and self.energia > self.dna.energia_max * PORCENTAGEM_PARA_REPRODUCAO:
                    return self.reproduzir(alvo)

        return None

    def reproduzir(self, outro_pai):
        pior_dano = min(self.dna.dano, outro_pai.dna.dano)
        melhor_dano = max(self.dna.dano, outro_pai.dna.dano)

        pior_velocidade = min(self.dna.velocidade, outro_pai.dna.velocidade)
        melhor_velocidade = max(self.dna.velocidade, outro_pai.dna.velocidade)

        pior_visao = min(self.dna.visao, outro_pai.dna.visao)
        melhor_visao = max(self.dna.visao, outro_pai.dna.visao)

        pior_energia_max = min(self.dna.energia_max, outro_pai.dna.energia_max)
        melhor_energia_max = max(self.dna.energia_max, outro_pai.dna.energia_max)

        dna_filho = DNA(
            dano = random.uniform(pior_dano - VAR_DANO, melhor_dano + VAR_DANO),
            velocidade = random.uniform(pior_velocidade - VAR_VELOCIDADE, melhor_velocidade + VAR_VELOCIDADE),
            visao = random.uniform(pior_visao - VAR_VISAO, melhor_visao + VAR_VISAO),
            energia_max = random.uniform(pior_energia_max - VAR_ENERGIA_MAX, melhor_energia_max + VAR_ENERGIA_MAX)
        )

        filho = Carnivoro()

        filho.dna = dna_filho
        filho.x = self.x
        filho.y = self.y
        filho.reproducao_cooldown = 100
        filho.energia = filho.dna.energia_max

        self.energia *= 0.5
        self.reproducao_cooldown = TEMPO_PARA_REPRODUCAO
        outro_pai.energia *= 0.5
        outro_pai.reproducao_cooldown = TEMPO_PARA_REPRODUCAO

        return filho


    def comer(self):
        self.energia = self.dna.energia_max

    def esta_vivo(self):
        return self.energia > 0

    def desenhar(self, screen, vision_surface):
        # Desenha o raio de visão semi-transparente na surface temporária
        pygame.draw.circle(
            vision_surface,
            (150, 150, 150, 40),  # cinza claro com alpha
            (int(self.x), int(self.y)),
            int(self.dna.visao * ESCALA)
        )

        raio_atual = self.get_raio_atual() * ESCALA
        # Desenha o herbívoro (azul)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), int(raio_atual))

    def get_raio_atual(self):
        # Escala do tamanho base (fitness) de acordo com a energia restante
        percentual_energia = self.energia / self.dna.energia_max  # vai de 0 a 1
        percentual_energia = max(0.2, percentual_energia)  # nunca menor que 20% do tamanho
        return self.raio * percentual_energia

    def get_velocidade(self):
        global FLORESTA_RAIO, FLORESTA_Y, FLORESTA_X
        dentro_floresta = math.dist((self.x, self.y), (FLORESTA_X, FLORESTA_Y)) <= FLORESTA_RAIO
        if dentro_floresta:
            self.velocidade_atual = self.dna.velocidade * 0.5

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
    global FLORESTA_RAIO, FLORESTA_Y, FLORESTA_X
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
    global COR_FUNDO, ANOITECER, FLORESTA_X, FLORESTA_Y, FLORESTA_RAIO

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
