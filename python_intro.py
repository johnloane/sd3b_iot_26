import pyttsx3
import os
import google.genai as genai
from dotenv import load_dotenv, find_dotenv
from google.genai import types

def main():
    #hello_world()
    #speak("IoT is the best. I can't wait for class next week")
    #get_int()
    #agree()
    #find_name()
    #phone_book()
    talk_to_gemini()
    
    
def talk_to_gemini():
    _ = load_dotenv(find_dotenv())
    gemini_api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
    system_prompt = "You are a friendly and supportive lecturer in Dundalk Institute of Technology. You are also succinct."
    user_prompt = input("What do you want to know: ")
    llm_model = "gemini-3.5-flash"
    chat = client.chats.create(model=llm_model)
    response = chat.send_message(
    system_prompt+user_prompt)
    print(response.text)


    
      
def hello_world():
    print("Hello, world")
    
    
def speak(to_say:str):
    engine = pyttsx3.init()
    engine.say(to_say)
    engine.runAndWait()
    
    
def get_int():
    while True:
        try:
            number = int(input("Please enter an integer: "))
            print(number)
            return
        except ValueError:
            print("Not an integer")
            
            
def agree():
    response = input("Do you agree? ")
    response = response.lower()
    if response in ["y", "yes", "agree", "confirm"]:
        print("Agrees")
    else:
        print("Does not agree")
        
        
def test_range():
    numbers = list(range(101))
    print(numbers)
    for i in numbers:
        if(i%2 == 0):
            print(i)
            break
    

def find_name():
    names = ["Pijus", "Leonas", "Anastasija", "Kornel"]
    name_to_search = input("Who are you looking for?")
    for name in names:
        if name == name_to_search:
            print("Found")
            break
    else:
        print("Not found")
        
def phone_book():
    people = {"Pijus":"+3531234", "Leonas":"08912345"}
    name = input("Please enter name:")
    if name in people:
        print(f"Number: {people[name]}")
   
if __name__ == "__main__":
    main()