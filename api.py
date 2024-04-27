from openai import OpenAI
import json as JSON
import streamlit as st

def get_route_prompt(location, days, itinerary_list):
    prompt = f"""
            i wanna go to {location} for {days} days,
            with this constraint
            - consider to visit place in the same area at one time 
            - please put each location on the title
            - please group into days and time of each days (morning, afternoon, and evening), put description on for each day
            - do not left any empty plan for morning, afternoon, and evening
            answer in json format like this:
            ("Day x" : ("description_day":description of today traveling,
            "morning":[location],"description_morning":explain morning activities,
            "afternoon":[location],"description_afternoon":explain afternoon activities,
            "evening":[location],"description_evening":explain evening activities,))
            
            this is my itinerary list, you can add other location if needed:
            {itinerary_list}
            """
    return prompt

def get_route_reccomendation(location, days):
    prompt = f"""
        i wanna go to {location} for {days} days, recommend me the itinerary
        with this constraint
        - consider to visit place in the same area at one time 
        - please put each location on the title
        - please group into days and time of each days (morning, afternoon, and evening), put description on for each day
        answer in json format like this:
        ("Day x" : ("description_day":description of today traveling,
        "morning":[location],"description_morning":explain morning activities,
        "afternoon":[location],"description_afternoon":explain afternoon activities,
        "evening":[location],"description_evening":explain evening activities,))
        """
    return prompt

def get_chatgpt_ans(prompt,api_key):
    client = OpenAI(api_key=api_key)

    stream = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}],
        stream = True,
        )

    answer = ""

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            answer += chunk.choices[0].delta.content
    
    my_dict = JSON.loads(answer,strict=True)
    return my_dict