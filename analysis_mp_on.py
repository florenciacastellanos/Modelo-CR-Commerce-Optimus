from collections import Counter

# Manual classification of all 143 MP_ON conversations
# A = Atraso/demora na entrega (produto chegou tarde, mas sem extravio confirmado; rastreio desatualizado resolvido)
# B = Produto extraviado/perdido em transito (confirmado extraviado ou devolvido ao remetente sem reentrega)
# C = Cancelamento por arrependimento / prazo longo / compra duplicada / nao pode receber
# D = Sistema marcou como entregue mas comprador nao recebeu / entrega em local errado / terceiro recebeu
# E = Produto com defeito / produto errado / entrega incompleta

classifications = [
    'C', # 1 Lilian - cancelamento antes envio
    'A', # 2 Emerson - aguardou, entregue
    'A', # 3 usuario frete - entregue
    'D', # 4 Thalita - entregue local errado
    'C', # 5 Javier - cancelamento viagem
    'D', # 6 usuario - marcado entregue, nao recebeu
    'C', # 7 Luila - cancelamento, devolveu
    'A', # 8 Andre Luiz - atraso pneus, entregue depois
    'B', # 9 usuario - nao entregue, reembolso
    'E', # 10 Vania - chegou danificado
    'D', # 11 usuario - sistema diz entregue, nao recebeu
    'A', # 12 comprador - atraso, aguardou
    'C', # 13 Maico - vendedor nao enviou, cancelamento
    'C', # 14 usuario - prazo longo, cancelamento
    'D', # 15 Caroline - consta entregue, nao recebeu
    'B', # 16 comprador - nao recebeu, reembolso R$134
    'A', # 17 Carina - atraso guarda-roupa, reembolso
    'A', # 18 comprador - urgente, caso encerrado
    'A', # 19 Marilia - entrega frustrada, entregue depois
    'A', # 20 compradora - nao recebeu chuveiro, entregue depois
    'C', # 21 Graziele - cancelamento compra duplicada
    'A', # 22 comprador - prazo entrega, entregue
    'A', # 23 Diendro - atraso, reembolso por nao entrega
    'C', # 24 Andre - cancelamento apos envio celular
    'A', # 25 usuario - prazo incerto, entregue
    'D', # 26 usuario - entregue a terceiro
    'A', # 27 usuario - nao recebeu, confirmou recebimento
    'A', # 28 Clarice - porta atraso, entregue
    'C', # 29 usuario - perfume duplicado, cancelamento
    'B', # 30 Maria Caroline - panela, transportadora nao achou endereco, extraviado
    'B', # 31 Taina - produto nao chegou, reembolso
    'D', # 32 usuario - consta entregue mas nao recebeu
    'C', # 33 Bruna - entrega dezembro vs novembro, reembolso
    'A', # 34 usuario - caiaque atraso, entregue
    'C', # 35 Kesia - guarda-roupa compra por engano
    'A', # 36 usuario - quadros atraso, entregue
    'B', # 37 usuario - produto em devolucao ao remetente, reembolso
    'D', # 38 Celio - celular marcado entregue, nao recebeu
    'C', # 39 Rafael - ninguem em casa, mudanca endereco, cancelamento
    'C', # 40 Klinton - Samsung, vendedor nao enviou, cancelamento
    'A', # 41 Ariadne - rastreio incerto, entregue
    'C', # 42 Ana Luiza - geladeira nao frost free, cancelamento
    'C', # 43 usuario - mudanca endereco, cancelamento
    'D', # 44 usuario - entregue mas ninguem recebeu
    'C', # 45 usuario - arrependimento
    'B', # 46 Ana Paula - perfume, 3 tentativas, extraviado, reembolso
    'C', # 47 Maykell - cancelamento, vendedor nao envia
    'C', # 48 Heithor - cancelamento, decidiu ficar
    'C', # 49 Lisandro - smartwatch, cancelamento
    'A', # 50 Kassem - ar-condicionado atraso, entregue
    'C', # 51 comprador - arrependimento
    'A', # 52 comprador - nao recebeu, recebeu depois
    'D', # 53 usuario - fritadeira, marcado entregue, nao confirmou
    'C', # 54 Jaiane - prazo dezembro (presente), cancelamento
    'A', # 55 Claudia - ar-cond, entrega frustrada, reembolso
    'D', # 56 usuario - marcado entregue 13/11, familiar recebeu
    'A', # 57 comprador - chapas, frete, entregue
    'B', # 58 Gizelia - fogao, vendedor particular, reembolso
    'C', # 59 usuario - perfume, cancelamento imprevisto
    'B', # 60 Octavio - fora prazo, reembolso pix
    'E', # 61 usuario - secador nao era o esperado
    'B', # 62 usuario - smartphone, nao recebeu, reembolso
    'C', # 63 usuario - cancelamento enviado
    'C', # 64 comprador - frete CEP nao atendido, cancelamento
    'B', # 65 Guilherme - extraviado, reembolso Pix
    'B', # 66 Wanderson - adesivo, rastreio sem update, reembolso
    'A', # 67 usuario - atraso, aguardou reembolso
    'D', # 68 Victor - marcado entregue, nao reconhece assinatura, reembolso
    'E', # 69 usuario - lanterna danificada, devolucao
    'C', # 70 Sandra - tablet, devolucao nao quer mais
    'A', # 71 usuario - atraso, aguardar 01/12
    'A', # 72 usuario - Smart TV atraso, entregue
    'A', # 73 Joao Carlos - atraso, entregue 14/11
    'A', # 74 Bruno - Multiprocessador, entregue 25/11
    'B', # 75 Joice - Samsung A26, transportadora nao achou, reembolso
    'C', # 76 Gabriela - Smart TV, prazo longo, cancelamento
    'D', # 77 comprador - marcado entregue, sem rastreio, aguardando
    'D', # 78 Rafaela - perfume, marcado entregue, nao recebeu, reembolso
    'A', # 79 usuario - produto entregue depois ok
    'C', # 80 Mirella - lavadora, atraso, cancelamento
    'A', # 81 usuario Samsung - aguardar rastreio
    'E', # 82 Amarilio - produto incompleto, reembolso parcial
    'B', # 83 Reinaldo - ar cond, devolucao remetente, reembolso
    'A', # 84 Luis - atraso rastreio, entregue
    'D', # 85 comprador - vasos, entregue, nao reconhecia destinatario, resolvido
    'C', # 86 comprador - atraso, cancelamento
    'C', # 87 Tatiane - armario, cancelamento urgencia
    'D', # 88 comprador - geladeira marcada entregue, nao recebeu, reembolso
    'B', # 89 Aguinaldo - secador, nao entregue, reembolso
    'D', # 90 usuario - alguem assinou em seu nome
    'C', # 91 usuario - endereco incorreto, cancelamento
    'A', # 92 Jorismar - atraso, entregue 15/11
    'C', # 93 comprador - area de risco, cancelamento
    'A', # 94 comprador - frete, entregue
    'D', # 95 Francisca - marcado entregue, nao confirmou
    'D', # 96 usuario - marcado entregue, cancelamento reembolso
    'D', # 97 usuario - marcado entregue, nao recebeu, reembolso
    'C', # 98 usuario - cancelamento em transito
    'C', # 99 Gleice - geladeira, cancelamento impossibilidade, resolveu receber
    'D', # 100 Joao Marcos - sem rastreio, nao recebeu
    'D', # 101 usuario - Kit Real, entregue a Marcelo portaria, confirmou
    'B', # 102 comprador - prazo passou, reembolso
    'B', # 103 usuario - fogao, adiado, reembolso
    'A', # 104 usuario - fritadeira, investigacao, entregue
    'C', # 105 Kelly - produto atrasado, cancelamento
    'C', # 106 usuario - mala, cancelamento arrependimento
    'C', # 107 Wagner - atraso, recusou entrega, reembolso
    'C', # 108 Danilo - prazo longo, cancelamento
    'A', # 109 Alexandro - aspirador, entregue 25/11
    'B', # 110 Felipe - Smart TV, extraviado, reembolso
    'D', # 111 comprador - poltrona, fiscais, marcado entregue, encerrado
    'C', # 112 Emerson - dois pedidos, cancelamento duplicata
    'A', # 113 Giselle - prazo 5 dez, entregue 27/11
    'E', # 114 Madalena - porta cor errada
    'B', # 115 Quelivania - fritadeira, devolucao remetente, reembolso
    'A', # 116 Gilson - colcao atraso, entregue
    'A', # 117 comprador - mesa frete, entregue
    'A', # 118 Rhuan - geladeira, transportadora horario, entregue
    'B', # 119 comprador - rastreio nao atualiza, extraviado, reembolso
    'A', # 120 comprador - aguardando Correios, retirou
    'B', # 121 usuario - bebedouro, extraviado, reembolso
    'A', # 122 Maria - sem rastreio, aguardando
    'A', # 123 Anderson - JBL, confirmou recebimento
    'A', # 124 Teresa - serra atraso, entregue
    'A', # 125 Thais - atraso, entregue
    'A', # 126 usuario - atraso, entregue, confirmou
    'C', # 127 usuario - nao pode esperar, cancelamento
    'A', # 128 Ingrid - colcao atraso, entregue
    'B', # 129 usuario - perdeu dia trabalho, extraviado, reembolso
    'A', # 130 Edson - Smart TV, confirmou recebimento
    'D', # 131 Maria Nicaelly - entregue a Carlos Nascimento
    'B', # 132 usuario - vendedor nao responde, devolucao remetente, reembolso
    'A', # 133 usuario - bateria notebook, atraso, entregue
    'A', # 134 Yego - confirmou recebimento
    'A', # 135 comprador - atraso, entregue
    'E', # 136 usuario - Game Pass, codigos incompletos
    'C', # 137 usuario - forno pendente, decidiu recusar
    'C', # 138 usuario - vendedor nao despachou, cancelamento
    'C', # 139 Jonas - nao recebeu, cancelamento
    'C', # 140 Vitor - compra sem querer, cancelamento
    'B', # 141 usuario - liquidificador, local diferente, extraviado
    'D', # 142 usuario - sanduicheira, verificou assinatura, confirmou
]

counts = Counter(classifications)
total = 143
print(f'Total: {total}')
for cat, count in sorted(counts.items()):
    pct = round(count/total*100, 1)
    print(f'{cat}: {count} ({pct}%)')
total_classified = sum(counts.values())
print(f'Sum check: {total_classified}')
