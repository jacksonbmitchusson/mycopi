import discord
import os
import asyncio
import time
import random
import traceback
import datetime
import json
from openai import OpenAI
from util import graphing, envparse
from re import fullmatch

with open('shroombot/emojis.txt') as f:
    emojis = f.read().split(',')
with open('shroombot/token') as f:
    token = f.read()
with open('shroombot/gpt_key') as f:
    gpt_client = OpenAI(api_key=f.read())    
with open('shroombot/names.txt') as f:
        names = f.read().split('\n')
with open('shroombot/insults.txt') as f:
        insults = f.read().split('\n')

env_path = '/home/onaquest/server-output/environment_log.txt'
images_path = '/home/onaquest/server-output/images'

# init bot 
#intents = 109632
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True

discord_client = discord.Client(intents=intents)

def random_emoji():
    return emojis[random.randint(0, len(emojis) - 1)]

def make_insult():
    name = names[random.randint(0, len(names) - 1)]
    insult = insults[random.randint(0, len(insults) - 1)]

    if random.randint(0, 2) == 0: 
        name = name.upper()
    if random.randint(0, 2) == 0: 
        insult = insult.upper()

    return f'{name} is a {insult}'
    
def gpt_query(prompt):
    print(f'woahh hey we gotta prompt: {prompt}', flush=True)
    response = gpt_client.responses.create(
        model='gpt-5-mini',
        input=prompt,
        max_output_tokens=10000
    )    
    print(f'i told em {response.output_text}', flush=True)
    return response.output_text

def gpt_comeback(username, message):
    print(f'Making gpt comeback!!! {username}: {message}')
    prompt = f'''
        Your name is ShroomBot. User: "{username}" has mentioned you in a message. 
        This is what they said: "{message}". Generate an approriate response. 
        THIS IS A DISCORD MESSAGE BEING SENT DIRECTLY TO SOMEONE SO DONT DO NOT MAKE A REFERENCE TO THE FACT THAT THIS IS A PROMPT(Just give a plain string response ONLY, one single response with NO FILLER, assume this response is being used in a python script that is responding as a discord bot)
    '''
    return gpt_query(prompt)     

def gpt_report(env_record, image0_name, image1_name):
    prompt = f'''
        You are a reporter. You are responsible for monitoring and reporting on the situation inside the the mushroom tub. 
        (aka "The Tub", also legal mushrooms called "golden teachers") 
        You will be given the following information: 
            An environment report, containing the time of the report temperature, humidity, and pressure data
            The filenames of the two latest images captured, one from each camera. 
            - These filenames represent dates/times in the format: MM-DD-YYYY_hh-mm-ss, 
            - the environment timestamp is of the same format. 
        Environment Report: {env_record}
        Filenames: {image0_name}, {image1_name}

        The following is a list of things to cover in your BRIEF report 
        (ENSURE THAT THE REPORT IS NOT ENUMERATED, MAKE IT FLOW LIKE A REAL NEWS REPORT):

        - The ideal temperature is around 73 degrees, 68 is too cold, and 78 is pushing too hot. 
        Compare the current temperature to this and report accordingly. 
        dont get too pressed about a few degrees variation, but calmly assess the current state of the tub. 
        Don't directly mention these specific range numbers, but interpret the vibe, like a weatherman relying on his expertice. 
        
        - Do the same as the previous step but for humidity. 
        90-100% is perfect, 
        80-90% is good, 
        70-80% is still ok, 
        60-70% is getting a little concerning, 
        50-60% is getting really low, 
        <50% is serious cause for concern.
        Again, don't specifically mention these ranges, or overly value the exact categorization, be a weatherman!  
        (2-4 combined lines for temp and humidity)
        
        <line break>
        
        - The current time is {datetime.datetime.now().strftime("")}, 
        compare the times in the data you've received to the current time.

        IF: the measurements are all within an hour

        THEN: calmly and briefly report on the nominality of the situation. 
        if either cameras is reporting "outoforder.png" or something similar, 
        it's likely been this way for a while, so simply report that its "still" offline, no fuss 
        (1-2 lines)
        
        ELSE: this is very serious. you should NOT remain calm, 
        you should be very scared and extremely worried about the current situation. 
        you should URGENTLY call for help from "Jackson" OR ask "Tristen" to get Jackson to fix it OR both. 
        I recommend you use all caps to maximize the chances of tristen or jackson seeing your message. 
        please ensure this gets fixed as soon as possible, like seriously IF THIS HAPPENS IT SHOULD ALMOST CHANGE THE 
        WHOLE MESSAGE, THERE SHOULD BE A PERCEIVED STATE OF PANIC IN THE OTHER SECTIONS.  
        (4 lines) 

        <line break>

        whacky and quirky sign off (MAX EMOJIS XD) 
        (1 line)

        You are to roleplay as a charismatic news anchor in a fancy news studio (you are reporting from "The Tub").
        Keep in mind that these updates happen regularly every 6 hours, continuously, so don't make a huge deal out of any one report. 
        Use a whole bunch of emojis to add a lighthearted vibe to the message while remaining direct and to the point about the report. 
        the result of this prompt will be sent directly to a discord chat so make sure your message is ready to go.    
    '''
    return gpt_query(prompt) 
# returns a tuple (discord file object, filename) 
def get_recent_image(images_path, id):
    recent_path = max(os.listdir(f'{images_path}{id}'))
    return (discord.File(f'{images_path}{id}/{recent_path}'), recent_path)

@discord_client.event
async def on_ready(): 
    guild = discord_client.get_guild(516440617199337506)              # henry's cage ID
    channel = guild.get_channel(1406777331053232208) # type: ignore   # mushroom chat ID 
    asyncio.create_task(autosend(channel))

@discord_client.event 
async def on_message(message):
    graph_command = 'go go shroombot graphing gadget ' 
    if message.author != discord_client.user:
        if message.content == 'please give me an image':
            env_record = envparse.last_record(env_path)
            image0 = get_recent_image(images_path, 0)
            image1 = get_recent_image(images_path, 1)
            msg_string = f'{make_insult()}\n{env_record}\nImage 0: {image0[1]}, Image 1: {image1[1]}'
            sent_msg = await message.reply(msg_string, files=[image0[0], image1[0]])   
            await sent_msg.add_reaction(random_emoji())
        if discord_client.user.mentioned_in(message): # type: ignore
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
        env_record = envparse.last_record(env_path)
        image0 = get_recent_image(images_path, 0)
        image1 = get_recent_image(images_path, 1)
        report = gpt_report(env_record, image0[1], image1[1])
        msg_string = f'{env_record}\nImage 0: {image0[1]}, Image 1: {image1[1]}\n{report}'
        sent_msg = await channel.send(msg_string, files=[image0[0], image1[0]]) 
        await sent_msg.add_reaction(random_emoji())
        await asyncio.sleep(6*60*60)

discord_client.run(token)

