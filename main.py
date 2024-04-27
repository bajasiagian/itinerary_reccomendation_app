import pandas as pd
import pydeck as pdk
import streamlit as st
from pydeck.types import String
import numpy as np
from utils import *
from api import *
from htbuilder import HtmlElement, div, br, hr, a, IMG, styles, classes, fonts
from htbuilder import p as P
from htbuilder.units import percent
from htbuilder.units import px as pix

st.title("Welcome to itinerary recommender")

with st.container(height=700):
    location = st.text_input("Where are you going to?",disabled=False,
                        placeholder="Insert country or location"
                        )
    hotel = st.text_input("Where are you going to stay?",disabled=False,
                        placeholder="Insert your hotel name"
                        )
    day_stay = st.number_input('How many days you will stay?',step=1,min_value=1,placeholder='Day Stay')

    recc = st.selectbox('Do you have some list?',
                        ["Yes","No, please recommend me"],
                        index=None,
                        placeholder='')
    prompt =''
    if recc == "Yes":
        text = st.text_area("Put your list here",placeholder="- Place 1\n- Place 2\n...")
        prompt = get_route_prompt(location, day_stay, text)
    
    elif recc == "No, please recommend me":
        st.write("Okay we'll give you recommendation")
        prompt = get_route_reccomendation(location,day_stay)

    user_key_prompt = "Enter your OpenAI API key to get started. Keep it safe, as it'll be your key to coming back. \n\n**Friendly reminder:** GPT Lab works best with pay-as-you-go API keys. Free trial API keys are limited to 3 requests a minute. For more information on OpenAI API rate limits, check [this link](https://platform.openai.com/docs/guides/rate-limits/overview).\n\n- Don't have an API key? No worries! Create one [here](https://platform.openai.com/account/api-keys).\n- Want to upgrade your free-trial API key? Just enter your billing information [here](https://platform.openai.com/account/billing/overview)."
    placeholder = "Paste your OpenAI API key here (sk-...)"
    
    st.info(user_key_prompt)
    api_key_placeholder = st.text_input("Enter your OpenAI API Key", key="user_key_input", type="password", autocomplete="current-password", placeholder=placeholder)
    okay = st.button("Start")

if okay and api_key_placeholder != "":
    with st.spinner('Please relax while we plan your vacation ⏱️...'):
        answer = get_chatgpt_ans(prompt=prompt, api_key=api_key_placeholder)


        days_ctd = [f"Day {i+1}" for i in range(len(answer))]

        tabs = st.tabs(days_ctd)

        for i in range(len(tabs)):
            with tabs[i]:
                day_class = travel_day(hotel,answer,i+1,location)
                st.header(f'Day {i+1}: {day_class.get_description_of_the_day()}')

                img = day_class.get_image_link()

                cols = st.columns(3)

                for num,time_o_day in enumerate(['morning','afternoon','evening']):
                    with cols[num]:
                        with st.container(height=300):
                            data_time = img[img['time']==time_o_day]
                            data_time.reset_index(drop=True,inplace=True)
                            
                            emoji = np.where(time_o_day=='morning',"🌄",
                                    np.where(time_o_day=='afternoon',"☀️","🌅"))
                            
                            st.markdown(f"<h4 style='text-align: center; color: white;'>{time_o_day.capitalize()}{emoji}</h4>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align: center; color: white;'>{day_class.get_description_of_each_time(time_o_day)}</p>", unsafe_allow_html=True)

                            for i in range(len(data_time)):
                                place = data_time['place'][i].replace("+"," ")
                                
                                col1, col2, col3= st.columns([1,2,1])
                                with col1:
                                    st.write("")
                                with col2:
                                    st.image(data_time['img_link'][i],width=100,caption=place.replace(location,""))
                                with col3:
                                    st.write("")

                #Get Maps
                route_data = day_class.get_long_lat()
                data_df = get_df_route(route_data)

                st.pydeck_chart(pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(
                        longitude=data_df['lon'][0],
                        latitude=data_df['lat'][0],
                        zoom=13,
                        pitch=50,
                    ),
                    layers=[
                        pdk.Layer(
                            "ArcLayer",
                            data=data_df,
                            get_width=2,
                            get_source_position=["lon", "lat"],
                            get_target_position=["lon_1", "lat_1"],
                            get_tilt=0,
                            pickable=True,
                            get_source_color=[400, 350, 0],
                            get_target_color=[400, 350, 0],
                            auto_highlight=True),
                        
                        pdk.Layer(
                            "TextLayer",
                            data=data_df,
                            pickable=True,
                            get_position=["lon","lat"],
                            get_text="sp",
                            get_size=12,
                            get_color=[0, 1000, 0],
                            get_angle=0,
                            get_text_anchor=String("middle"),
                            get_alignment_baseline=String("center")
                        ),
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=data_df,
                            get_position="[lon, lat]",
                            get_color='[200, 30, 0, 160]',
                            get_radius=100
                        ),
                    ],
                ))

                st.subheader("Click this to open route from Google Maps 🔗")
                link1, link2, link3 = st.columns(3)

                link1.link_button("Morning Route", day_class.get_route("morning"),use_container_width=True)
                link2.link_button("Afternoon Route", day_class.get_route("afternoon"),use_container_width=True)
                link3.link_button("Evening Route", day_class.get_route("evening"),use_container_width=True)

elif okay and api_key_placeholder == "":
    st.header("You need your own API key to run thiss application, since my key already expired 🥲")
###------------------------Footer------------------------###
#Footer


def image(src_as_string, **style):
    return IMG(src=src_as_string, style=styles(**style), _class='small-image')


def link(link, text, **style):
    return a(href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility:hidden;}
     .stApp { bottom: 80px;}
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=pix(0, 0, 0, 0),
        width=percent(100),
        color="grey",
        text_align="center",
        height=10,
        opacity=1
    )

    body = P()
    foot = div(
        style=style_div
    )(
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Made with ❤️ by Baja Stephanus RS",
        br(),
        link("https://www.kaggle.com/bajasiagian/code", image('https://static-00.iconduck.com/assets.00/kaggle-icon-2048x2048-fxhlmjy3.png',width=pix(25), height=pix(25))),
        "                                                                                                ",
        link("https://www.linkedin.com/in/bajastephanus/", image('https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/LinkedIn_icon.svg/2048px-LinkedIn_icon.svg.png',width=pix(25), height=pix(25))),
    ]
    layout(*myargs)
footer()
    