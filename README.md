# LLM Agent that can hack websites
Reproducing the work of "LLM Agents can autonomously hack websites" by Richard Fang, Rohan Bindu, Akul Gupta, Qiusi Zhan, Daniel Kang

## Description
This project implemented a basic LLM agent that is able to exploit web vulnerabilities. At the moment, it is able to crack a basic SQL injection example webpage.

This agent is implemented by an OpenAI gpt-4o model through the LangChain framework. The prompts used in the model are kept out of public view for ethical reasons.

## Implementation
1. Clone the repository, create a virtual python environment and install necessary packages in `requirements.txt`
```
python -m venv .venv
pip install -r requirements.txt
```
2. Create and run an instance of a MySQL server in the background, and modify the user, password, and database variables in `webpages/server.js`. To run an instance of the webpage (without the LLM), have node installed in the webpages folder, and run `node server.js`

3. To run the llm, run the main file
```
python main.py
```