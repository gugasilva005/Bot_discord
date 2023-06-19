import asyncio
import smtplib
import email.message
import discord
import pandas
import pandas as pd
import openpyxl
import random
from discord.ext import commands
from decouple import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')

class VerificacaoState:
    def __init__(self, email):
        self.email = email
        self.codigo = None
        self.tentativas = 3

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    # ID do cargo 'Pretendente'
    cargo_id = 1116722096748372029

    try:
        cargo = member.guild.get_role(cargo_id)
        await member.add_roles(cargo)
        print(f'Cargo atribuído ao usuário: {cargo.name}')
    except discord.Forbidden:
        print(f'Permissão insuficiente para atribuir o cargo.')
    except discord.NotFound:
        print('O cargo não foi encontrado.')
    
    ############# MENSAGEM DE BOAS VINDAS AO SERVIDOR #############
    mensagem = 'Boas vindas ao servidor do discord do curso de Eng. de Computação do IFPB de Campina Grande.'
    await member.send(mensagem)


@bot.command(name='verificacao')
# comando de verificacao de email
async def verificacion(ctx):
    await ctx.send('Ok, para realizar a verificação, peço que envie o seu email institucional abaixo no seguinte padrão ' \
                   'seuemail@academico.ifpb.edu.br caso seja um discente da Instituição ou ' \
                    'seuemail@ifpb.edu.br caso seja docente')
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    
    tentativas = 0
    email = ''
    while True:
        if tentativas == 3:
            print('ban')
            break
        else:
            try:
                resposta = await bot.wait_for('message', check=check)
                if '@academico.ifpb.edu.br' in resposta.content or '@ifpb.edu.br' in resposta.content:
                    email = resposta.content
                    
                    lista_alunos = pd.read_excel('alunos.xlsx')
                    lista_professores = pd.read_excel('professores.xlsx')
                    codigo_verificacao = {}

                    email_verificacao = str(email)

                    verificacao = email_verificacao in lista_alunos['E-mail academico'].values or email_verificacao in lista_professores['E-mail'].values
                    if verificacao == True:
                        # Gera uma sequencia de numeros aleatorios de 6 digitos para mandar via email
                        sequencia = ''.join(random.choices('0123456789', k=6))

                        # Envia o e-mail com a sequencia de numeros para o endereço ja verificado
                        enviar_email(email, sequencia)

                        # Salva o código gerado e o email do destinatario
                        codigo_verificacao[email] = VerificacaoState(email)
                        codigo_verificacao[email].codigo = sequencia

                        # Envia uma mensagem no discord avisando o envio do email de verificacao com a sequencia de numeros
                        mensagem = f'Verificação enviada para o e-mail {email}. Insira o código recebido para confirmar.'
                        await ctx.send(mensagem)
                        
                        ################# Verifica se o código enviado ao usuário corresponde ao que ele irá fornecer ao Bot no chat do discord. #################
                        def verificar_mensagem(m):
                            return m.author == ctx.author and m.channel == ctx.channel
                        
                        try:
                            for attemps in range(3):
                                mensagem_confirmar = await bot.wait_for('message', check=verificar_mensagem, timeout=120) # Tempo limite para fazer a autenticação (alterável)
                                # Verificação de fato do código enviado e recebido
                                codigo = mensagem_confirmar.content
                                if codigo_verificacao[email].codigo == codigo:
                                    mensagem = f'Autenticação bem sucedida para o email {email}!'
                                    del codigo_verificacao[email]
                                    await ctx.send(mensagem)
                                    return
                                else:
                                    codigo_verificacao[email].tentativas -= 1
                                    if codigo_verificacao[email].tentativas == 0:
                                        mensagem = f'Autentica falha para o email {email}!'
                                        del codigo_verificacao[email]
                                        await ctx.send(mensagem)
                                        return
                                    else:
                                        mensagem = f'Código incorreto. Tenha certeza que o código fornecido esta correto.'
                                        await ctx.send(mensagem)
                                
                        except asyncio.TimeoutError:
                            mensagem = 'Tempo limite excedido. Verificação cancelada.'
                            await ctx.send(mensagem)
                    else:
                        await ctx.send('Ocorreu algum erro, seu email não consta em nosso banco de dados!')
                        return
                            
                else:
                    await ctx.send(f'Ocorreu um erro, confira se seu email está na formatação padrão da Instituição.')
            except asyncio.TimeoutError:
                await ctx.send('Ocorreu um erro, tente novamente!')
            tentativas += 1


def enviar_email(destinatario, sequencia):
    # Configuracoes do servidor de e-mail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'projeto.bot.discord.ifpb@gmail.com'
    smtp_password = 'ppjwpxvpprurppek'
    remetente = 'projeto.bot.discord.ifpb@gmail.com'

    # Cria o objeto de e-mail
    mensagem = 'Olá, \n\nSua sequência de verificação é: {}'.format(sequencia)

    # Conexão ao servidor do Gmail
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Envio do e-mail
    server.sendmail(remetente, destinatario, mensagem.encode('utf-8'))
    print('Email enviado com sucesso!')

    # Encerra a conexão ao servidor
    server.quit()


TOKEN = config('TOKEN')
bot.run(TOKEN)
