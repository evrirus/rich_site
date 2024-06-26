from django.shortcuts import render
from utils import coll, get_district_by_id, get_house_by_id
from icecream import ic

# Create your views here.
def index(request):
    data = {
        'title': "Rich Machine",
    }
    return render(request, 'homePage/index.html', data)

# def profile(request):
#     ic(request.user.username)
    # user = coll.find_one({'user_id': 899827113})
    
    # houses_id = user['house']['houses']
    # houses = []
    # for x in houses_id:
    #     house_info = get_house_by_id(x['id'])
    #     district_info = get_district_by_id(house_info['district_id'])
    #     house_info['district_info'] = district_info
    #     houses.append(house_info)
    
    # data = {
    #     "nickname": user.get('nickname'),
    #     "money": user.get('money'),
    #     "donate_balance": user.get('donate_balance'),
    #     "job": user.get('job', {}).get('title') if user.get('job', {}).get('title') else 'Безработный',
    #     "car": user.get('car'),
    #     "yacht": user.get('yacht'),
    #     "houses": houses,
    #     "couple": None,
    #     "registration": user.get('registration'),
    #     "language": user.get('language'),
    #     "active": user.get('active'),
    #     "username": user.get('username')
    # }
    # data = {'nickname': {'name': request.user.username}}
    
    # return render(request, 'homePage/profile.html', data)