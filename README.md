# mundo_inteligente
"Mundo inteligente", mundo que utilizando conceitos de algoritmo genético, simula um mundo com herbívoros e carnívoros.

para utilizar, rode no terminal:

pip install pygame==2.6.1

Para rodar, rode python main.py no terminal, ou usando alguma ide, rode o arquivo main.py.

O algoritmo funciona da seguinte forma:
- Individuos herbivoros sao representados por circulos azuis.
- Individuos carnivoros sao representados por circulos vermelhos.
- Plantas sao representados por circulos verdes


Todos os individuos possuem energia limitada, que decai com o passar do tempo.
- Se a energia acabar o individuo morre.
- Herbivoros comem plantas, e carnivoros comem herbivoros, entao:
  - Herbivoros sao presas, e quando veem um predador, corre para o outro lado.
  - Carnivoros sao predadores, e quando veem uma presa, tentam caça-la.
- Se a energia atual do individuo for maior que PORCENTAGEM_PARA_REPRODUCAO (60%), ele esta passivel à reproducao. 
  - Quando se encontra com um individuo da mesma especie, ele reproduz.
  - O filho eh um individuo com caracteristicas parecidas com as dos pais.
  - Na reproducao, a energia atual dos pais diminui, e reseta o tempo para reproducao (cooldown).


Configuracoes de mundo:
- Existe dias e noites, representados pela cor de fundo do mundo (preto = noite, branco = dia)
  - Na noite, a visao dos HERBIVOROS diminui, aumentando a capacidade de caça dos carnivoros.
- Existe uma area delimitada no mundo como um circulo verde. Esta eh a floresta.
  - Na floresta, existe uma chance maior de respawn de comida. (Causa maior concentracao de herbivoros dentro)
  - Dentro da floresta, carnivoros possuem a velocidade deteriorada (50% da velocidade total). (Causa maior dificuldade de caça)