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
    
    if 'palavrão' in message.content:
        await message.channel.send(f'Por favor, {message.author.name} não ofenda os demais usuários!')

        await message.delete()
    
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji)
    if reaction.emoji == '👍':
        role = user.guild.get_role(1116722141803589803)
        await user.add_roles(role)
    elif reaction.emoji == '💩':
        role = user.guild.get_role(1116722096748372029)
        await user.add_roles(role)


@bot.command(name='oi')
async def send_oi(ctx):
    name = ctx.author.name

    response = 'Olá, '+ name

    await ctx.send(response)

@bot.command(name='calcular')
async def calculate_expression(ctx, *expression):
    expression = ''.join(expression)
    
    response = eval(expression)

    await ctx.send(f'A resposta é: {str(response)}')


TOKEN = config('TOKEN')
bot.run(TOKEN)