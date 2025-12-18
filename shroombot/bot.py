import discord
import os
import asyncio
import time
import random
import traceback
from openai import OpenAI
from util import graphing, envparse
from re import fullmatch

names = ...
insults = ...

emojis = ...
with open('shroombot/emojis.txt') as f:
    emojis = f.read().split(',')

token = ...
with open('shroombot/token') as f:
    token = f.read()

gpt_client = ... 
with open('shroombot/gpt_key') as f:
    gpt_client = OpenAI(api_key=f.read())

env_path = '/home/onaquest/server-output/environment_log.txt'
images_path = '/home/onaquest/server-output/images'

# init bot 
#intents = 109632
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True

discord_client = discord.Client(intents=intents)

def get_insult_supplies():   
    global names
    global insults 
    with open('shroombot/names.txt') as f:
        names = f.read().split('\n')
    with open('shroombot/insults.txt') as f:
        insults = f.read().split('\n')

def random_emoji():
    return emojis[random.randint(0, len(emojis) - 1)]

def make_insult():
    get_insult_supplies()
    name = names[random.randint(0, len(names) - 1)]
    insult = insults[random.randint(0, len(insults) - 1)]

    if random.randint(0, 2) == 0: 
        name = name.upper()
    if random.randint(0, 2) == 0: 
        insult = insult.upper()

    return f'{name} is a {insult}'

def get_recent_env():
    with open(env_path) as f:
        return f.read().split('\n')[-1]
    
def gpt_comeback(username, message):
    print(f'Making gpt comeback!!! {username}: {message}')
    input_string = f'Your name is ShroomBot. User: "{username}" has mentioned you in a message. This is what they said: "{message}". Generate an approprite response, if they are nice be nice, if they are neutral be neutral, if they are mean you HAD BETTER be mean back. (I AM NOT ENCOURAGING HARASSMENT, BUT LEAN SLIGHTLY TOWARD ARGUMENTITAVE), this is just banter, but dont be lame about it!! it has to be cool! i need you to respond to the people in the discord but it CAN NOT BE LAME!!! you need to match energy IT IS IMPERITIVE THAT YOU MATCH ENERGY, Generate an approprite response, if they are nice be nice, if they are neutral be neutral, if they are mean you HAD BETTER be mean back, PLEASE ***MATCH ENERGY***. OK LAST PART, THIS IS THE MOST IMPORTANT, YOU ABSOLUTELY *****MUST***** RESPOND LIKE DR. SUESS (I KNOW YOU CANT PRODUCE THE EXACT DR SUESS, BUT JUST TRY TO EMULATE THE STYLE), YOU ***GOTTA*** WORK IN SOME KIND OF RHYMING OR ALLITERATION IF YOU SAY \"Sorry—I can\'t write in the exact voice of Dr. Seuss\" SO HELP ME GOD I WILL NEVER BE OKAY WITH IT PLEASE DONT SAY THAT JUST FUCKING GIVE AN ANSWER TO THE PROMPT THIS IS A DISCORD MESSAGE BEING SENT DIRECTLY TO SOMEONE SO DONT DO NOT MAKE A REFERENCE TO THE FACT THAT THIS IS A PROMPT(Just give a plain string response ONLY, one single response with NO FILLER, assume this response is being used in a python script that is responding as a discord bot)'
    response = gpt_client.responses.create(
        model='gpt-5-mini',
        input=input_string
    )    
    return response.output_text

# returns discord file object 
def get_recent_image(images_path, id):
    recent_path = max(os.listdir(f'{images_path}{id}'))
    return discord.File(f'{images_path}{id}/{recent_path}')

@discord_client.event
async def on_ready(): 
    guild = discord_client.get_guild(516440617199337506) # henry's cage ID
    channel = guild.get_channel(1406777331053232208) # mushroom chat ID 
    asyncio.create_task(autosend(channel))

@discord_client.event 
async def on_message(message):
    graph_command = 'go go shroombot graphing gadget ' 
    if message.author != discord_client.user:
        if message.content == 'please give me an image':
            sent_msg = await message.reply(f'{make_insult()}\n{envparse.last_record(env_path)}', files=[get_recent_image(images_path, 0), get_recent_image(images_path, 1)])   
            await sent_msg.add_reaction(random_emoji())
        if message.content.startswith('shroombot add insult:') and len(message.content.split(':')) > 1:
            added_insult = message.content.split(':')[1].strip()
            with open('shroombot/insults.txt', 'a') as f:
                f.write(f'\n{added_insult}')
            sent_msg = await message.reply(f'ok i did it. i added {added_insult}')
            sent_msg.add_reaction('🐱‍🏍')
        if discord_client.user.mentioned_in(message):
            print('mentioned!')
            await message.reply(gpt_comeback(message.author, message.content))           
        if message.content.startswith(graph_command):
            options = ['Temperature', 'Humidity', 'Pressure']
            options_string = '|'.join(options)
            usage = f'Usage: \'{graph_command} [{options_string}] [hours]\''
            try:
                arguments = message.content[len(graph_command):].split(' ')
                selection = arguments[0] 
                hours_str = arguments[1]
                if fullmatch(r'[0-9]+((.[0-9]+)?)', hours_str) and selection in options:
                    hours_diff = float(hours_str)
                    range = graphing.get_relative_range(hours_diff)
                    image_file = discord.File(graphing.make_graph(env_path, range, selection), 'graph.png')
                    await message.reply(f'{make_insult()}', file=image_file)
                else:
                    await message.reply(f'DUMBASS! Usage: \'{graph_command} [{options_string}] [hours]\'')
            except Exception as e:
                trace = traceback.format_exc()
                await message.reply(f'something fucked up. it was probably your fault tbh.\nException: {e}\n{usage}\nstack trace:{trace}')

async def autosend(channel):
    await discord_client.wait_until_ready()
    time.sleep(0.5)
    while not discord_client.is_closed():
        sent_msg = await channel.send(f'{make_insult()}\n{envparse.last_record(env_path)}', files=[get_recent_image(images_path, 0), get_recent_image(images_path, 1)]) 
        await sent_msg.add_reaction(random_emoji())
        await asyncio.sleep(8*60*60)

get_insult_supplies()

discord_client.run(token)

