
import random

def jogar(nome):
    tentativas = 15
    numero_aleatorio = random.randint(1, 20)
    usuario = int (input(f"{nome},tente adivinhar o número (de 0 a 20):  "))


    while usuario != numero_aleatorio and tentativas > 0:
    
        if usuario != numero_aleatorio:
            print("Quase acertou, tente novamente!")
        if numero_aleatorio % 2 == 0:
         print("DICA: É par")
        else:
         print ("DICA: É impar")
     
        usuario = int (input(f"{nome},tente novamente:  "))
        tentativas -= 1
    
    if usuario  == numero_aleatorio:
        print(f"PARABÉNS {nome}, você acertou!")
        return 10
    else:
    
        print(f"PARABÉNS {nome}, você não acertou! O número era {numero_aleatorio}.")
        return 0

jogador1_nome = input("Digite o nome do Jogador 1: ")
jogador2_nome = input("Digite o nome do Jogador 2: ")

pont_jog1 = jogar(jogador1_nome)
pont_jog2 = jogar(jogador2_nome)

        
if pont_jog1 > pont_jog2:
    print(f"{jogador1_nome} ganhou com {pont_jog1} pontos!")
elif pont_jog2 > pont_jog1:
    print(f"{jogador2_nome} ganhou com {pont_jog2} pontos!") 
else:   
    print(f"O jogo terminou empatado!")    