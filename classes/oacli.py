import time, json, sys, os, requests
sys.path.append(os.getcwd())
import utils
from dotenv import load_dotenv
from openai import OpenAI

class OACLI:
    def __init__(self) -> None:
        global client
        
        load_dotenv()

        client = OpenAI()

    def main(self):

        # Analyze image
        if len(sys.argv) > 0:
            prompt = None

            if len(sys.argv) > 2:
                prompt = sys.argv[2]
        
            # Chat
            if sys.argv[1] == 'chat':
                self.chat_completions()
            # Get embeddings
            elif sys.argv[1] == 'embed':
                self.embeddings(prompt)
            # Generate image
            elif sys.argv[1] == 'image':
                self.images(prompt)


    def chat_completions(self):
        system_prompt, user_prompt = None, None

        while system_prompt is None:
            test = input("\nEnter 'y' to use the test system guide:\n\tYou are a fanciful 15th century Italian poet\nOtherwise simply enter your desired prompt\n")
            system_prompt = 'You are a fanciful 15th century Italian poet' if test == 'y' else test

        while user_prompt is None:
            test = input("\nEnter 'y' to use the test prompt:\n\tWrite a short poem about your love for a bread called lembas\nOtherwise simply enter your desired prompt\n")
            user_prompt = 'Write a short poem about your love for a bread called lembas' if test == 'y' else test

        
        filename = input('\nPlease supply a name for generated text:\n')

        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt + '\n--- \nDon\'t add this to the output: try to avoid excessive whitespace \n---'},
            {"role": "user", "content": user_prompt}
        ])


        if filename:
            outputfile = os.path.join('static', 'output', 'generated_' + filename + '.txt')
            with open(outputfile, 'w') as file:
                file.write(f'System prompt: {system_prompt}')
                file.write(f'\nUser prompt: {user_prompt}')
                file.write(f'\n{completion.choices[0].message.content}')
            if os.path.isfile(outputfile):
                print(f'File was saved at {outputfile}')
        print(completion.choices[0].message.content)


    def embeddings(self, prompt = None):
        while prompt is None:
            prompt = input('\nPlease supply text to generate embeddings:')

        embedding = client.embeddings.create(
            model="text-embedding-ada-002",
            input=prompt        
        )

        filename = input(f'\nFor saving in {os.path.join("static", "output")} please supply a file name for generated images and type \'n\' to only display:\n')

        if filename == 'n':
            filename = None

        if filename:
            outputfile = os.path.join('static', 'output', 'embeddings_' + filename + '.txt')
            with open(outputfile, 'w') as file:
                file.write(embedding)
            if os.path.isfile(outputfile):
                print(f'File was saved at {outputfile}')
        else:
            print(embedding)

    def images(self, prompt = None):
        while prompt is None or not isinstance(prompt, str):
            prompt = input('\nPlease supply a prompt to generate images:\n')
        
        filename = input(f'\nFor saving in {os.path.join("static", "output")} please supply a file name for generated images:\n')

        amount = input(f'\nHow many images do you want?\n')
        amount = amount if int(amount) < 3 else 2 # I'm cheap, so...

        size = input(f'\nWhat size do you want them? Choose from: {", ".join(utils.openai_image_sizes)}\n')

        try:
            response = client.images.generate(
                prompt = prompt,
                n = int(amount),
                size = size
            )
        except Exception as e:
            print(e)

        if response.data:
            for i in range(0, len(response.data)):
                if response.data[i] and utils.is_url(response.data[i].url):
                    image = requests.get(response.data[i].url).content
                
                if filename and image:
                    outputfile = os.path.join('static', 'output', f'generated_{filename}_{i}.jpg')
                    with open(outputfile, 'wb') as file:
                        file.write(image)

                    if os.path.isfile(outputfile):
                        print(f'File was saved at {outputfile}')