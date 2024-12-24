import requests

def postrequest():
    url = "http://127.0.0.1:8000/api/get_profile/"
    token = "3e3c9b5af858140a22ce5591f716c42a62571f6e"


    headers = {
        'Authorization': f'Token {token}'
    }

    response = requests.post(url, headers=headers)

    print("Статус-код:", response.status_code)
    print("Ответ:", response.json())

if __name__ == '__main__':
    postrequest()