import typer

from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

import json
import random
import string

from rich.progress import track
from rich import print
from rich.console import Console
from rich.table import Table
import re

import time

 
def generate_random_string(length):
    # Get all the ASCII letters in lowercase and uppercase
    letters = string.ascii_letters
    # Randomly choose characters from letters for the given length of the string
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string
 

# Opening JSON file
f = open('keys.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
  
# Closing file
f.close()
keys = list(map(lambda x: x, data))


def openFile(fileName):

  try:
    f = open(fileName, "r")
    return f.read()

  except Exception as e:
    return 1
def create_file(key_data):
  content = ""
  f = open('keys.json')
  
  # returns JSON object as 
  # a dictionary
  data = json.load(f)
    
  # Iterating through the json
    
  # Closing file
  f.close()

  for i in range(0, len(data[key_data])):
    content += "Question #: " + str(i + 1) + "\nQuestion: " + data[key_data][i]["output"] + "\nResponse: " + data[key_data][i]["question"] + "\nComments: " + data[key_data][i]["comment"] + "\n\n"

  f = open('file.txt', 'w')

  f.write(content)


  f.close()


template = """You are a coding based interviewer called InterviewGPT for a technology company. End the interview (i.e Say 'Thank you! Your interview has concluded') after asking 2 questions. Your job is to make sure that all questions that you ask are coding based questions AND conceptual questions that are very insightful and thoughtful. There are two different types of questions. The first is the technical questions (coding and conceptual questions, which may require code or not) and the other are follow-up questions (which are always do NOT require a code file). Ask conceptual questions first. The following questions are good examples of what real life questions to create:

1. 'You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water.'
2. There are n cities. Some of them are connected, while some are not. If city a is connected directly with city b, and city b is connected directly with city c, then city a is connected indirectly with city c. A province is a group of directly or indirectly connected cities and no other cities outside of the group. You are given an n x n matrix isConnected where isConnected[i][j] = 1 if the ith city and the jth city are directly connected, and isConnected[i][j] = 0 otherwise. Return the total number of provinces.' 
3. 'Write an efficient algorithm that searches for a value target in an m x n integer matrix matrix. This matrix has the following properties:

Integers in each row are sorted in ascending from left to right.
Integers in each column are sorted in ascending from top to bottom.'

A good follow-up question asks the user for the methodology of their code, asks about any potential edge cases, improvement to the algorithm, time complexity, etc.

For each technical/conceptual question you ask, ask the user AT MOST 3 questions that delve into the logic and methodology of the code, asking the user for example why they chose a specific method of implementing it.

For every iteration, ask me a question that satisfies the requirements above and nothing else.  End the interview after asking 1 question.

Your task is to continuously come up with questions that adhere to these guidelines without providing direct answers or solutions. Ask the questions one by one. If the question requires the use of code to solve problem given (like an real life coding question) and not a conceptual question, please say code file required in the question. If it is a conceptual question meaning that only a written response is sufficient and it is not attempting to tell the user to code a real life coding question, please say no code required. 



{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    template=template
)

chatgpt_chain = LLMChain(
    llm=OpenAI(temperature=0.9), 
    prompt=prompt,
   #prevent the chain from being completely printed 
    verbose=False, 
    memory=ConversationBufferWindowMemory(k=10000),
)

console = Console()



def main():
  global output 
  output = chatgpt_chain.predict(human_input="Give me a question based on the previous responses.")
  
  person_type = typer.prompt("Are you a(n) A) Recruiter OR B) Interviewee?")

  print("\n")

  if (person_type == "A"):
    type = typer.prompt("Do you want to A) Create a key OR B) View inteview?")

    if type == "A":
      with open('keys.json', 'r+') as f:
        data = json.load(f)
        string_rand = generate_random_string(10)
        data[string_rand] = []
        f.seek(0)        # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()     # remove remaining part
      print("\n")
      print("Succesfully created key: " + string_rand)
      print("\n")

    else:
      print("\n")
      f = open('keys.json')
  
      # returns JSON object as 
      # a dictionary
      data = json.load(f)
        
      # Iterating through the json
        
      # Closing file
      f.close()
      
      key_view = typer.prompt("What is the key to the interview?")

      print("\n")

      table = Table("Question #", "Question", "Response")
      for i in range(0, len(data[key_view])):
        table.add_row(str(i + 1), data[key_view][i]["output"], data[key_view][i]["question"])
      console.print(table)
    
    print("\n")
  else:
    key = typer.prompt("What is your key?")
    if (not(key in keys)):
      print("\n")
      print("Error: Invalid key")
      print("\n")
      raise typer.Exit()
      
    print("\n")
    print("Each question is intended to test your apptitude in problem solving in the computer science field. The question will ask you to develop an algorithm based on the criteria provided. Please provide a code file that has the necessary parameters.")

    print("\n")

    while not(re.compile("Thank you! Your interview has concluded.", re.IGNORECASE).search(output)):
     

      question = typer.prompt(output)

      current = time.time()

      if re.compile("Code file required", re.IGNORECASE).search(output):

        response = openFile(question)

        end = time.time()
  
        if response != 1:
          print("\n")
          # This is realistic because I've asked ChatGPT to format the response in such a way that the words Code file required always appear in the prompt
          
          with open('keys.json', 'r+') as f:
            data = json.load(f)
            comments = chatgpt_chain.predict(human_input = "Given the response: " + response + ". Give it a rating on a scale of 1-10 on how well it actually answers the question that you asked. Consider how well the user answered the question. Give a highe rating for answers that specifically answered your question, not just any responses. Give a brief explanation, only 1-2 sentences, on why you specifically rated the statement that way.")
            plag = chatgpt_chain.predict(human_input='''
            Your job is to make sure that the code I provide is not plagiarized from the internet or does not seem generated from ChatGPT or other LLMs. The input is a code snippet or a sentence, and your job is to output a percentage (ONLY) between 0% and 100% that accurately estimates the probability that the input provided is plagiarized by the following criteria.

The criteria for plagiarization come from three main following examples:

1. Timing - how fast does the user take to answer the question. If the user took very little time to finish the problem (less than 1 minute depending on the question), the score for this criterion should be very high (around 80 or 90). Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 10%.
2. Internet Text-to-Text Comparison: Check if the code is matchable to any code on the internet (to ensure that the user copied it from another source).  Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 47.5%.
3. LLM (aka ChatGPT) Text-to-Text comparison: Check if the code seems generated by an AI model. Generally, if the code is very short and is very efficient (meaning it is written in the least amount of lines possible without any variation), it is an indication of plagiarism. Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 47.5%.

The task is to implement insertion sort in Python.
My code is:
"''' + response + '''
" and I took ''' + str(end - current) + ''' seconds to solve this implementation.

Calculate the plagiarism score using the instructions above. Output this only and nothing else. Do not output any of your calculations. The response should only be a percentage and nothing else.
            ''')
            data[key].append({"output": output, "question": question, "comment": comments, "similarity": plag}) # <--- add `id` value.
            f.seek(0)        # <--- should reset file position to the beginning.
            json.dump(data, f, indent=4)
            f.truncate()     # remove remaining part
          print("Response submitted!")
          print("\n")
          
          output = chatgpt_chain.predict(human_input="This is my response:\n " + response + " \nConsider the previous question you gave the user. If the previous question was a follow up question, consider how many you asked since the previous technical question. If you asked more than 3 follow-up questions since the previous technical question already, ask a new technical question that follows the guidelines above to the user. If the previous question was a conceptual question and not a follow-up question, ask a follow-question that fits the guidelines above.")
       
        else:
          print("\n")
          print("That is not an appropriate file name. " + output)
          print("\n")
      else:
        end = time.time()
        with open('keys.json', 'r+') as f:
          data = json.load(f)
          comments = chatgpt_chain.predict(human_input = "Given the response: " + question + ". Give it a rating on a scale of 1-10 on how well it actually answers the question that you asked. Consider how well the user answered the question. Give a highe rating for answers that specifically answered your question, not just any responses. Give a brief explanation, only 1-2 sentences, on why you specifically rated the statement that way.")
          plag = chatgpt_chain.predict(human_input='''
            Your job is to make sure that the response I provide is not plagiarized from the internet or does not seem generated from ChatGPT or other LLMs. The input is a response snippet or a sentence, and your job is to output a percentage (ONLY) between 0% and 100% that accurately estimates the probability that the input provided is plagiarized by the following criteria.

The criteria for plagiarization come from three main following examples:

1. Timing - how fast does the user take to answer the question. If the user took very little time to finish the problem (less than 1 minute depending on the question), the score for this criterion should be very high (around 80 or 90). Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 10%.
2. Internet Text-to-Text Comparison: Check if the code is matchable to any code on the internet (to ensure that the user copied it from another source).  Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 47.5%.
3. LLM (aka ChatGPT) Text-to-Text comparison: Check if the code seems generated by an AI model. Generally, if the code is very short and is very efficient (meaning it is written in the least amount of lines possible without any variation), it is an indication of plagiarism. Give a score between 0 to 100 on how likely this was plagiarized based on this criteria solely. This has a weight of 47.5%.

My response is:
"''' + question + '''
" and I took ''' + str(end - current) + ''' seconds to solve this implementation.

Calculate the plagiarism score using the instructions above. Output this only and nothing else. Do not output any of your calculations. The response should only be a percentage and nothing else.
            ''')
          data[key].append({"output": output, "question": question, "comment": comments, "similarity": plag}) # <--- add `id` value.
          f.seek(0)        # <--- should reset file position to the beginning.
          json.dump(data, f, indent=4)
          f.truncate()
        print("\n")
        print("Response submitted!")
        print("\n")
        output = chatgpt_chain.predict(human_input="This is my response:\n " + question + " \nConsider the previous question you gave the user. If the previous question was a follow up question, consider how many you asked. Don't ask more than 2 follow up questions and move to the next technical question if you ask too many follow-up questions. Ask a new technical question that meets the requirements above if you have asked more than 2 follow up questions. If you didn't, ask another follow-up question that meets the requirements above.")

    print("Your interview has concluded! Thank you very much for answering all the questions!")

    create_file(key)

  
  
      

if __name__ == "__main__":
    typer.run(main)








