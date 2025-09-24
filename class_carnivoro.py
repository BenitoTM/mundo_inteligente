import pygame
import random
import math
from config import (DNA, ALTURA, LARGURA, PESO_DANO, PESO_VISAO, PESO_ENERGIA, PESO_VELOCIDADE, FITNESS_MAX, FITNESS_MIN, RAIO_MAX, RAIO_MIN, FPS, PORCENTAGEM_PARA_REPRODUCAO, ESCALA, TEMPO_PARA_REPRODUCAO, VAR_DANO, VAR_VISAO, VAR_VELOCIDADE, VAR_ENERGIA_MAX)

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