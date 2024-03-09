import pandas as pd
import requests
import re
import numpy as np

class travel_day:
    
    def __init__(self,hotel,prompt_ans,day,location):
         self.prompt_ans = prompt_ans
         self.day = day
         self.location = location
         self.hotel = hotel.replace(" ","+")+f"+{location}"
    
    def get_location(self):


        kk = map(lambda x: x.replace(" ","+")+f"+{self.location}",
                 sum([self.prompt_ans[f'Day {self.day}']['morning'],
                      self.prompt_ans[f'Day {self.day}']['afternoon'],
                      self.prompt_ans[f'Day {self.day}']['evening']],[]))
        
        time_of_day = [len(self.prompt_ans[f'Day {self.day}']['morning'])*['morning'],
                       len(self.prompt_ans[f'Day {self.day}']['afternoon'])*['afternoon'],
                       len(self.prompt_ans[f'Day {self.day}']['evening'])*['evening']]
        time_of_day = sum(time_of_day,[])

        df = pd.DataFrame({"time":sum([["morning"],time_of_day],[]),"place":sum([[self.hotel],list(kk)],[])})
        df.loc[len(df)] = ["evening",self.hotel]

        return df
    
    def get_image_link(self):
        img_link_list = []
        for i in list(self.get_location()['place'].unique()):
            url = f"https://www.google.com/search?q={i}&tbm=isch"
            
            resp=requests.request(method="GET",url=url)
            
            img = re.findall('src="http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"',resp.text)[1]
            img_link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',img)[0].replace("amp;","")
            
            img_link_list.append([i,img_link])
        
        df_img = pd.DataFrame(img_link_list)
        df_img.columns =['place','img_link']
        df = pd.merge(self.get_location(),df_img,how='left',on='place')
        df = df.drop_duplicates()

        return df
    
    def get_long_lat(self):
        #get latitude longitude for each location given desire location
        loc = list(self.get_location()['place'].unique())
        long_lat_temp = []

        for i in range(len(loc)):
            url = f'https://www.google.com/maps/dir/{loc[0]}/{loc[i]}'
            resp=requests.request(method="GET",url=url)
            
            text = re.findall('meta content="http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"',resp.text)[0]
            link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',text)[0].replace("amp;","")

            marker = re.findall(r'(?:markers=)(.*?)(?:&)',link)
            
            if marker == []:
                raise TypeError("Your hotel might be at wrong location")
                
            for num,k in enumerate(marker[0].split("%7C")):
                long_lat_temp.append(sum([[loc[i]] if num == 1 else [loc[0]],k.split("%2C")],[]))

            
        long_lat_df = pd.DataFrame(long_lat_temp)
        long_lat_df.columns =['place','lat','lon']
        
        df = pd.merge(self.get_location(),long_lat_df,how='left',on='place')
        df = df.drop_duplicates()
        return df
    

    def get_route(self,time_traveling):
        link = 'https://www.google.com/maps/dir'
        df_loc = self.get_location()[(self.get_location()['time']==time_traveling)|\
                                   (self.get_location().index==self.get_location()[self.get_location()['time']==time_traveling].index[0]-1)]
        for i in df_loc['place']:
            link += f"/{i}"
        return link
    
    def get_description_of_the_day(self):
        desc = self.prompt_ans[f"Day {self.day}"]['description_day']
        if desc != {}:
            return desc
        else:
            return "Rest day!"
    
    def get_description_of_each_time(self,time_traveling):
        desc = self.prompt_ans[f"Day {self.day}"][f'description_{time_traveling}']
        if desc != {}:
            return desc
        else:
            return "Well, I got no reccomendation, it's time to rest"

def get_df_route(df_):
    df = df_.copy()

    df['lon_1'] = df[['lon']].shift(-1)
    df['lat_1'] = df[['lat']].shift(-1)
    df.dropna(inplace=True)

    df['lon'] = df['lon'].astype('float64')
    df['lat'] = df['lat'].astype('float64')
    df['lon_1'] = df['lon_1'].astype('float64')
    df['lat_1'] = df['lat_1'].astype('float64')

    df['place'] = df['place'].apply(lambda x: x.replace("+"," "))
    df['symbol'] = np.where(df['time']=='morning','MORNING',
                np.where(df['time']=='afternoon','AFTERNOON',"EVENING"))
    df['sp'] = df['symbol']+'\n'+'\n'+df['place']

    return df[['place','lat','lon','lat_1','lon_1','sp','symbol']].reset_index(drop=True)
