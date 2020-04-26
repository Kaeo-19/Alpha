"""
Copyright 2019 Kaeo-19


Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import json
import logging
import datetime


try:
    import speech_recognition as sr
    import aiml
    import requests
    import nltk
    from nltk.corpus import stopwords as sw #Stopwords dataset from nltk.
    from noaa_sdk import noaa
except ImportError as e:
    logging.critical("Missing one or more required libraries! Run pip3 install -r requirements.txt \n {}".format(str(e)))


class utils:
    def m() -> str:
        """
        m() -> str.
        Microphone function, gets audio input from microphone and returns a striing
        """
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.adjust_for_ambient_noise(source)
            logger.info("Microphone Active! Waiting for prompt!")
            audio = r.listen(source)

        s = r.recognize_google(audio) #Send the audio to google
        result = s.lower()
        return result
    
class bot:
    def bot(conf):
        """
        bot(conf)
        Bot.
        """
        with open('cphrases.json', 'r+') as aliases:
            phrases = json.loads(aliases.read())
        
        if conf['aiml_bot'] is True:
            logging.info("Loading the aiml kernel and files!")
            k = aiml.Kernel()
            k.learn('main.xml')
            k.respond('load aiml b')
            
        else:
            logger.warn("Aiml bot is disabled!")

        print(conf['bot_name'])
        print(conf['description'])

        #There are two forms of input, audio or terminal. There are two stored forms, the raw response (rresponse), and the parsed response used for just command words (response)
        stopwords = set(sw.words('english'))
        while True:
            if conf['audio'] is True:
                logging.warn("Microphone is active! Listening...")
                rresponse = utils.m()
            else:
                rresponse = input("## ")

            response = rresponse.split(' ') 
            logging.info("Command: {}".format(response))
            for w in stopwords:
                if w in response:
                    response.remove(w)
                        
            for phrase in phrases['greet_phrases']:
                if phrase in response:
                    x = datetime.datetime.now().hour
                    if x > 0 and x <= 12:
                        print("Program your generic response for the morning time here")
                    elif x > 12 and x < 18:
                        print("Programing afternoon response")
                    else:
                        print("Program night response")
                        
                    
            if "nearby" in response:
                logging.debug("Running command! \n {}".format(rresponse))
                #Fetch nearby locations
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
                r = requests.get(url + 'query=' + rresponse + '&key=' + conf['maps_api_key'])
                res = r.json()
                res = res['results']
                if conf['audio'] is True:
                    resp = res[0]['name'] + '. address is ' + res[0]['formatted_address']
                    synth(resp)
                else:
                    print(res[0]['name'] + '. Address is ' + res[0]['formatted_address'])


            if "weather" in response:
                logging.debug("Ran weather command with: {}".format(response))
                try:
                    wind_direction = {
                        "N": "North",
                        "E": "East",
                        "S": "South",
                        "W": "West",
                        "SE": "south east",
                        "SW": "south west",
                        "NW": "north west",
                        "NE": "north east",
                        "NNE": "north north east",
                        "NNW": "north north west",
                        "SSE": "south south east",
                        "SSW": "south south west",
                    }
                
                    res = noaa.NOAA().get_forecasts(conf['zipcode'], conf['country'], True)
                    if res[0]['temperatureUnit'] is "F":
                        temp_unit = "farenheit"
                    elif res[0]['temperatureUnit'] is "C":
                        temp_unit = "celcius"
                    else:
                        temp_unit = "unknown"

                    wind_direction = wind_direction[str(res[0]["windDirection"])] #Useless type conversion, there to help make things flow better conceptually though.
                        
                    res = res[0]['shortForecast'] + ". the temperature is " + str(res[0]['temperature']) + " degrees " + temp_unit + ", with wind speeds of " + res[0]['windSpeed'] + " heading " + wind_direction
                        
                    if conf['audio'] is True:
                        synth(res)
                    else:
                        print(res)
                except KeyboardInterrupt as e:
                    logger.warn("Command canceled! \n {}".format(e))
                    

            else:
                if conf['audio'] is True:
                    synth(str(k.respond(rresponse)))
                else:
                    print(k.respond(rresponse))

if __name__ == '__main__':
    
    try:
        with open('general_settings.json') as conf:
            conf = json.loads(conf.read())
    except FileNotFoundError as e:
        print("Configuration file missing!")

    logging.basicConfig(format='[' + conf['bot_name'] + ']' + '[' + '%(asctime)s' + ']' + ' %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    bot.bot(conf)
                    
