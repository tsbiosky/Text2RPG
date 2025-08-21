from google import genai
import PIL.Image
from PIL import Image
from io import BytesIO
from google.genai import types
import base64
from openai import OpenAI
import requests
from prompt_hub import prompt_npc, world_map_prompt
import json
import datetime
import yaml

# Load configuration from YAML file
def load_config(config_file="code/config.yaml"):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        return None
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None

# Load configuration
config = load_config()
if not config:
    print("Failed to load configuration. Exiting.")
    exit(1)

# Extract API keys from config
GEMINI_API_KEY = config.get('gemini_api_key', '')
OPENAI_API_KEY = config.get('openai_api_key', '')
RECRAFT_API_KEY = config.get('recraft_api_key', '')

# Validate API keys
if not GEMINI_API_KEY:
    print("Warning: gemini_api_key not found in config")
if not OPENAI_API_KEY:
    print("Warning: openai_api_key not found in config")
if not RECRAFT_API_KEY:
    print("Warning: recraft_api_key not found in config")

# Load text file as input
def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def upscale_image(scale_factor=2):
    image_path = "../graphics/world/world_map.png"  # Replace with your image path
    image = Image.open(image_path)

    # Define the target size
    target_size = (1536*scale_factor, 1024*scale_factor)

    # Upsample the image
    upsampled_image = image.resize(target_size, Image.LANCZOS)  # LANCZOS for high-quality resampling
    # Save the upsampled image
    upsampled_image.save("../graphics/world/world_map_big.png")

def generate_character_image(prompt,name):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images= 1,
        )
    )
    #print(response)
    for generated_image in response.generated_images:
        image = Image.open(BytesIO(generated_image.image.image_bytes))
        #image.show()
        image.save("../graphics/character/"+name+".png")

    raftclient = OpenAI(
        base_url='https://external.api.recraft.ai/v1',
        api_key=RECRAFT_API_KEY,
    )
    response = raftclient.post(
        path='/images/removeBackground',
        cast_to=object,
        options={'headers': {'Content-Type': 'multipart/form-data'}},
        files={'file': open("../graphics/character/"+name+".png", 'rb')},
    )
    image_url=response['image']['url']
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.save('../graphics/character/'+name+'_vector.png')

image = PIL.Image.open("../graphics/character/down/0.jpeg")

#text_input = 'a picture of character with full body in animation style,The background must be exactly white RGB(255,255,255) . Description: A genius female neuroscientist in her 20s with white hair, sexy figure, white short hair, beautiful legs, scientist.'
print("start extract information")
client = genai.Client(api_key=GEMINI_API_KEY)
text_input = load_text_file("./story.txt")
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt_npc+str(text_input)
)
res=response.text
res=res.replace("```json", "").replace("```", "")
res=json.loads(res)
print("finished extract information")
with open("./output.json", 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print("start world map image")
data=json.load(open("./output.json", 'r', encoding='utf-8'))
world_map_description=data["location"]


#openai
gptclient = OpenAI(api_key=OPENAI_API_KEY)

img = gptclient.images.generate(
    #model="dall-e-2",
    model="gpt-image-1",
    prompt=world_map_prompt+world_map_description,
    n=1,
    size="1536x1024"
)
image_base64 = img.data[0].b64_json
image_bytes = base64.b64decode(image_base64)
with open("../graphics/world/world_map.png", "wb") as f:
    f.write(image_bytes)
print("finished world map image")
print("start character image")
player=data["player"]
generate_character_image(player["outfit"],player["name"])
npc=data["npc"]
for n in npc:
    generate_character_image(n["outfit"],n["name"])
print("finished character image")
