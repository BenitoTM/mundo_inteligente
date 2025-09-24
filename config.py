import random

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

# =========================
# CONFIGURAÇÕES DO MUNDO
# =========================
ESCALA = 0.3 #30% do tamanho original
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
        self.dano = dano if dano is not None else random.uniform(50, 200)
        self.velocidade = velocidade if velocidade is not None else random.uniform(0.5, 3.0)
        self.visao = visao if visao is not None else random.uniform(50, 150)
        self.energia_max = energia_max if energia_max is not None else random.uniform(80, 200)
