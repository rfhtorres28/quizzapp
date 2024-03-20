import requests


def make_api_request():

    url = ' http://127.0.0.1:5000/question'
     
    data = {"content":"What is the meaning of E in FET?", 'options': [
            {'question_id':'q1', 'letter': 'a', 'content': 'Effect', 'is_correct':True},
            {'question_id':'q1', 'letter': 'b', 'content': 'Electric Field', 'is_correct':False},
            {'question_id':'q1', 'letter': 'c', 'content': 'Eddy Current', 'is_correct':False}

    ] }
    #response = requests.delete(url)

    #response = requests.get(url) #-for retrieving operation 
    #response = requests.post(url, json=data)  
    response = requests.put(url, json=data) #for updating data

    if response.status_code == 200:
        print('API response')
        print(response.json())

    else:
        print(f'{response.status_code}')



if __name__ =='__main__':
    make_api_request()