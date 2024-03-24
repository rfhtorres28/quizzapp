import requests


def make_api_request():

    url = ' http://127.0.0.1:5000/names'
     
    data = {"name":"Ringgoset"}
    #response = requests.delete(url)

    #response = requests.get(url) #-for retrieving operation 
    #response = requests.post(url, json=data)  
    #response = requests.put(url, json=data) #for updating data

    if response.status_code == 200:
        print('API response')
        print(response.json())

    else:
        print(f'{response.status_code}')



if __name__ =='__main__':
    make_api_request()