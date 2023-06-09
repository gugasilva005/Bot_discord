import discord
from discord.ext import commands, tasks
from decouple import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')

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
    guild = member.guild
    role = discord.utils.get(guild.roles, name='Pretendente') #Substituição do cargo para 'Pretendente'

    if role is not None:
        await member.add_roles(role)
        print(f'Added role {role.name} to {member.name}')
    else:
        print(f'Role not found in server {guild.name}. Make shure that role exists.')

@bot.command(name='ajuda')
async def send_hello(ctx):
    name = ctx.author.name
    response = 'Olá ' + name + f', me chame {bot.user.name} e preciso que me forneça o seu e-mail academico' \
                f' para que possamso verificar se você é aluno de Engenharia de Computação do IFPB de Campina Grande.'
    
    await ctx.send(response)


TOKEN = config('TOKEN')
bot.run(TOKEN)