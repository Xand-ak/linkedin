
from langchain.llms import Ollama
from langchain.agents import initialize_agent
from agent import SearchAPI

llm = Ollama(model="deepseek-r1:14b")  # Correct model name for Ollama

agent = initialize_agent(
    tools=SearchAPI.tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

response1 = agent.run("Find companies in Germany based in Berlin")
response2 = agent.run("Show me software engineers in Canada skilled in Python")
response3 = agent.run("List remote full-time AI jobs for entry-level candidates")

print(response1)
print(response2)
print(response3)
