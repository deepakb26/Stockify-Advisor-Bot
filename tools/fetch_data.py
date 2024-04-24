import json
import time
from bs4 import BeautifulSoup
import re
import requests
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain.llms import OpenAI
from langchain.agents import load_tools, AgentType, Tool, initialize_agent
import yfinance as yf

# import openai
import warnings
import os
warnings.filterwarnings("ignore")

genai = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key=config.api_key)


# llm=OpenAI(temperature=0,
#            model_name="gpt-3.5-turbo-16k-0613")


# Fetch stock data from Yahoo Finance
def get_stock_price(ticker,history=5):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    ticker=ticker+".NS"
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df=df[["Close","Volume"]]
    df.index=[str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date",inplace=True)
    df=df[-history:]
    # print(df.columns)
    
    return df.to_string()

# Script to scrap top5 googgle news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    url=f"https://www.google.com/search?q={search_term}&cr=countryIN"
    url=re.sub(r"\s","+",url)
    return url

def get_recent_stock_news(company_name):
    # time.sleep(4) #To avoid rate limit error
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    g_query=google_query(company_name)
    res=requests.get(g_query,headers=headers).text
    soup=BeautifulSoup(res,"html.parser")
    news=[]
    for n in soup.find_all("div","n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div","IJl0Z"):
        news.append(n.text)

    if len(news)>6:
        news=news[:4]
    else:
        news=news
    news_string=""
    for i,n in enumerate(news):
        news_string+=f"{i}. {n}\n"
    top5_news="Recent News:\n\n"+news_string
    
    return top5_news


# Fetch financial statements from Yahoo Finance
def get_financial_statements(ticker):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    else:
        ticker=ticker
    ticker=ticker+".NS"    
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1]>=3:
        balance_sheet=balance_sheet.iloc[:,:3]    # Remove 4th years data
    balance_sheet=balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet


# #Openai function calling
# function=[
#         {
#         "name": "get_company_Stock_ticker",
#         "description": "This will get the indian NSE/BSE stock ticker of the company",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "ticker_symbol": {
#                     "type": "string",
#                     "description": "This is the stock symbol of the company.",
#                 },

#                 "company_name": {
#                     "type": "string",
#                     "description": "This is the name of the company given in query",
#                 }
#             },
#             "required": ["company_name","ticker_symbol"],
#         },
#     }
# ]


# def get_stock_ticker(query):
#     response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             temperature=0,
#             messages=[{
#                 "role":"user",
#                 "content":f"Given the user request, what is the comapany name and the company stock ticker ?: {query}?"
#             }],
#             functions=function,
#             function_call={"name": "get_company_Stock_ticker"},
#     )
#     message = response["choices"][0]["message"]
#     arguments = json.loads(message["function_call"]["arguments"])
#     company_name = arguments["company_name"]
#     company_ticker = arguments["ticker_symbol"]
#     return company_name,company_ticker

function = [
    {
        "name": "get_company_Stock_ticker",
        "description": "This will get the Indian NSE/BSE stock ticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company."
                },
                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given in the query."
                }
            },
            "required": ["company_name", "ticker_symbol"]
        }
    }
]

# Define the prompt template
prompt_template = """
Given the user request: {query}
What is the company name and the company stock ticker?

Respond in the following format:
Company Name - Ticker Symbol
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["query"])

# Create the LLMChain with the prompt and the Google Gemini API
llm_chain = LLMChain(prompt=prompt, llm=genai)

def get_stock_ticker(query):
    # Run the LLMChain with the user query
    response = llm_chain.run(query)

    # Parse the response to extract the company name and ticker symbol
    try:
        company_name, ticker_symbol = response.split(" - ")
    except ValueError:
        # Handle cases where the response is not in the expected format
        company_name = "Unknown"
        ticker_symbol = "Unknown"

    return company_name, ticker_symbol

# #Simple version with stock stats v1 
# def Anazlyze_stock(query):
#     Company_name, ticker = get_stock_ticker(query)
#     print({"Query": query, "Company_name": Company_name, "Ticker": ticker})

#     # Add your code to fetch stock data, financials, and news

#     # Define the prompt template for stock analysis
#     analyze_stock_prompt = """
#     Given the user request: {query}
#     Provide a detailed stock analysis for {Company_name} (Ticker: {ticker}). Use the available data and provide an investment recommendation.
    
#     Available information:
#     {available_information}
#     """
#     analyze_stock_prompt_template = PromptTemplate(template=analyze_stock_prompt, input_variables=["query", "Company_name", "ticker", "available_information"])
#     analyze_stock_chain = LLMChain(prompt=analyze_stock_prompt_template, llm=genai)

#     available_information = "Placeholder for stock data, financials, and news"
#     analysis = analyze_stock_chain.run(query=query, Company_name=Company_name, ticker=ticker, available_information=available_information)

#     print("\n\nAnalyzing.....\n")
#     print(analysis)
#     return analysis

# utilising search and stock data
def Anazlyze_stock(query):
    Company_name, ticker = get_stock_ticker(query)
    print({"Query": query, "Company_name": Company_name, "Ticker": ticker})

    # Add your code to fetch stock data, financials, and news

    # Define the prompt template for stock analysis
    Company_name,ticker=get_stock_ticker(query)
    print({"Query":query,"Company_name":Company_name,"Ticker":ticker})
    stock_data=get_stock_price(ticker,history=10)
    stock_financials=get_financial_statements(ticker)
    stock_news=get_recent_stock_news(Company_name)
    available_information=f" Stock Data: {stock_data} \n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    analyze_stock_prompt=f'''Give detail stock analysis, Use the available data and provide investment recommendation.
     \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
             User question: {query} \
             You have the following information available about {Company_name}. Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination.Try to Give positives and negatives  : \
              {available_information} '''
             
    analyze_stock_prompt_template = PromptTemplate(template=analyze_stock_prompt, input_variables=["query", "Company_name", "ticker", "available_information"])
    analyze_stock_chain = LLMChain(prompt=analyze_stock_prompt_template, llm=genai)

    available_information = "Placeholder for stock data, financials, and news"
    analysis = analyze_stock_chain.run(query=query, Company_name=Company_name, ticker=ticker, available_information=available_information)

    print("\n\nAnalyzing.....\n")
    
    analysis += ("\n\n"+stock_data+"\n\n")
    analysis+="\n\n  Stock news : \n\n"
    analysis+=stock_news
    # print(stock_news+"\n\n")
    print(analysis)
    return analysis


