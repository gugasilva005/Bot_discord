import asyncio
import discord
from key import token
from discord.ext import commands, tasks
from funcoes import funcao_le_arquivos, enviar_email, bane_usuario, distribui_cargos, encontra_nome_planilha
from funcoes import altera_apelido
import random

TOKEN = token.get('TOKEN')


CANAL_ID = 1119012172647891068 # ID DO CANAL DE AUTENTICAÇÃO
GUILD_ID = 1116672058353516614 # ID DO SERVIDOR
ROLE_ID = 1116702722318684161 # ID DO CARGO - PRETENDENTE


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True
bot = commands.Bot(intents=intents, command_prefix="!")


class VerificacaoState:
    def __init__(self, email):
        self.email = email
        self.codigo = None
        self.tentativas = 3


@bot.event
###### FUNCAO QUE LIGA O BOT #########
async def on_ready():
    print(f'{bot.user.name} está online')


@bot.event
########## FUNCAO PARA VERIFICAR SE A MENSAGEM NAO É DO PROPRIO BOT ##########
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CANAL_ID:
        await bot.process_commands(message) #processse todos os comandos


@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name='Pretendente')
    channel = discord.utils.get(guild.channels, name='canal-de-autenticação')
    usuario = member.name

    texto_boas_vindas = f"Olá, {usuario} para realizar autenticação e ter acesso ao restante dos servidores, digite seu email acadêmico abaixo.\n" \
                        f"Para alunos: exemplo@academico.ifpb.edu.br\n" \
                        f"Para professores: exemplo@ifpb.edu.br\n" \
                        f"Caso não tenha e-mail acâdemico verifique o Card abaixo"

    link = 'https://www.youtube.com/watch?v=U2yQ5MqlhUU'
    texto_link = 'Como obter meu e-mail acadêmico'
    embed = discord.Embed(
        title='Como criar e-mail acadêmico',
        description='Video explicando o procedimento para criar o e-mail institucional',
        colour=65280
    )

    embed.set_image(url='https://i.ytimg.com/vi/U2yQ5MqlhUU/maxresdefault.jpg')

    embed.add_field(name='LINK', value=link)

    # Envia Texto de Boas vindas e Embed com link para criar email academico
    await channel.send(texto_boas_vindas)
    await channel.send(embed=embed)

    # Define os cargos de pretendente
    if role is not None:
        await member.add_roles(role)
        print(f'Added role {role.name} to {member.name}')
    else:
        print(f'Role not found in server {guild.name}. Make sure the role exists.')


    # Inicia as tentativas para enviar o e-mail
    tentativas_email = 0
    email = ""
    ban = False
    while True:
        channel_id = CANAL_ID
        channel = bot.get_channel(channel_id)
        if tentativas_email == 3:
            ban = True
            break
        else:
            try:
                resposta_email = await bot.wait_for('message', check=lambda x: x.author == member, timeout= 900)
                tentativas_email += 1
                email_a_verificar = str(resposta_email.content).lower()
                if "@academico.ifpb.edu.br" in email_a_verificar or "@ifpb.edu.br" in email_a_verificar:

                    le_planilha_alunos = funcao_le_arquivos('alunos.csv', 'E-mail academico', email_a_verificar)
                    le_planilha_professores = funcao_le_arquivos('professores.csv', 'E-mail', email_a_verificar)
                    codigo_verificacao = {}

                    email = (str(email_a_verificar)).lower()
                    print(email)

                    if le_planilha_alunos == True or le_planilha_professores == True:
                        # Gera uma sequencia de numeros aleatorios de 6 digitos para mandar via email
                        sequencia = ''.join(random.choices('0123456789', k=6))

                        # Envia o e-mail com a sequencia de numeros para o endereço ja verificado
                        enviar_email(email, sequencia)

                        # Salva o código gerado e o email do destinatario
                        codigo_verificacao[email] = VerificacaoState(email)
                        codigo_verificacao[email].codigo = sequencia

                        # Envia uma mensagem no discord avisando o envio do email de verificacao com a sequencia de numeros
                        mensagem_que_envia_codigo_email = f'Verificação enviada para o e-mail {email}. Insira o código recebido para confirmar.'
                        print('email enviado')

                        await channel.send(mensagem_que_envia_codigo_email)

                        for attemps in range(3):
                            # Alterei e coloquei o .id
                            resposta_codigo = await bot.wait_for('message', check=lambda x: x.author.id == member.id, timeout= 900)
                            # Verificação de fato do código enviado e recebido
                            codigo = resposta_codigo.content
                            print('E-mail consta dentro do banco de dados')
                            if codigo_verificacao[email].codigo == codigo:
                                mensagem_autenticacao_ok = f'Autenticação bem sucedida para o email {email}!'
                                del codigo_verificacao[email]
                                print(mensagem_autenticacao_ok)
                                await channel.send(mensagem_autenticacao_ok)
                                break
                            else:
                                codigo_verificacao[email].tentativas -= 1
                                if codigo_verificacao[email].tentativas == 0:
                                    mensagem_falha_autenticar_codigos_limite = f'Autenticação falha para o email: {email}!'
                                    del codigo_verificacao[email]
                                    print('erro')
                                    await channel.send(mensagem_falha_autenticar_codigos_limite)
                                    ban = True
                                    break
                                else:
                                    mensagem_tente_novamente_codigo = f'Código incorreto. Tenha certeza que o código fornecido esta correto.'
                                    print(mensagem_tente_novamente_codigo)
                                    await channel.send(mensagem_tente_novamente_codigo)
                        break
                    else:
                        mensagem_email_fora_planilha = 'O E-mail informado não consta em nosso banco de dados'
                        print(mensagem_email_fora_planilha)
                        await channel.send(mensagem_email_fora_planilha)

                else:
                    mensagem_email_fora_dos_padroes = 'Ocorreu um erro, o e-mail informado não segue os padrões'
                    print(mensagem_email_fora_dos_padroes)
                    await channel.send(mensagem_email_fora_dos_padroes)
            except asyncio.TimeoutError:
                ban = True
                print('ban_teste')
                break
                
    if ban == True: # arrumar condicional
        await bane_usuario(member)
        print('Banimento')
    else:
        planilha = ''
        if "@academico.ifpb.edu.br" in email:
            planilha = 'alunos.csv'
        elif "@ifpb.edu.br" in email:
            planilha = 'professores.csv'
        nome = encontra_nome_planilha(email, planilha)
        print('Alterar cargos')
        print(nome)
        await distribui_cargos(member, email)
        await altera_apelido(member, nome)

bot.run(TOKEN)


# Falta apenas colocar a biblioteca datetime