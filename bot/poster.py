import re
import asyncio
from datetime import datetime
from aiogram.utils.exceptions import BotBlocked
from aiohttp import ClientSession
from .app import get_time, scheduler, BOT_USERNAME, logger
from models import link, want, user, blacklist
from .markup import markup
from .utils import send_message


wants_list = []

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}


def compose_links():
    Links = link.get_all_active()
    result = {}

    if not Links:
        return result
    
    for Link in Links:
        if Link.url not in result:
            result[Link.url] = {'url': Link.url, 'users': [], 'wants': []}

        if Link.owner_id not in result[Link.url]['users']:
            if not user.is_active(Link.owner_id):
                continue
            
            result[Link.url]['users'].append(Link.owner_id)

    remove_links = []
    for res_link in result:
        if not result[res_link]['users']:
            remove_links.append(res_link)

    for rem_link in remove_links:
        del result[rem_link]

    return result


# def compose_want(want_raw: dict):
#     want = {
#         'want': {
#             'id': int(want_raw['id']),
#             'lang': str(want_raw['lang']),
#             'name': str(want_raw['name']).strip(),
#             'description': str(want_raw['description']).strip(),
#             'create_date': str(want_raw['dateCreate']),
#             'expire_date': str(want_raw['dateExpire']),
#             'price_limit': int(float(want_raw['priceLimit'])),
#             'possible_price_limit': int(float(want_raw['possiblePriceLimit'])),
#             'category_name': str(want_raw['categoryName']),
#             'parent_category_name': str(want_raw['parentCategoryName']),
#         },
#         'user': {
#             'id': int(want_raw['userId']),
#             'name': str(want_raw['userName']).strip(),
#             'wants': int(want_raw['userWants']),
#             'active_wants': int(want_raw['userActiveWants']),
#             'hired_percent': int(want_raw['userWantsHiredPercent']),
#             'avatar': str(want_raw['userAvatar']).replace('\\', '') if 'noprofilepicture.gif' not in want_raw['userAvatar'] else '',
#             'badges': [badge['id'] for badge in want_raw["userBadges"]]
#         }
#     }

#     return want


async def get_want(session: ClientSession, link: dict):
    async with session.post(link['url'], headers=HEADERS) as response:
        if response.status == 200:
            response_data = await response.json()
            wants_raw = response_data['data']['wants']
            composed_wants = []

            for want_raw in wants_raw:
                want_date = datetime.strptime(want_raw['dateCreate'], '%Y-%m-%d %H:%M:%S')
                want_time = int(want_date.timestamp())
                want_time_diff = get_time() - (want_time + 10800)

                if want_time_diff / 3600 >= 1:
                    want.create(want_raw['id'], link['url'])
                    continue

                if not want.get(want_raw['id']):
                    Want = want.create(want_raw['id'], link['url'])
                    if Want:
                        # composed_wants.append(compose_want(want_raw))
                        composed_wants.append(want_raw)
                        

            for composed_want in composed_wants:
                link['wants'].append(composed_want)
                
            global wants_list
            wants_list.append(link)

        else:
            await logger(3, 'poster > get_want', 'Ёп тваю мать блять, что тут происходит', f'Респонс статус: {response.status}')


async def get_wants(links: dict):
    global wants_list
    wants_list = []

    async with ClientSession() as session:
        tasks = []
        for link in links:
            task = asyncio.ensure_future(get_want(session, links[link]))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def send_wants():
    links = compose_links()
    sended_messages = 0

    if not links:
        return False
    
    await get_wants(links)
    for want_link in wants_list:
        for user_id in want_link['users']:
            if not user.is_active(user_id):
                continue

            for want_ in want_link['wants']:
                if blacklist.get_by_owner(user_id, want_['userName'].lower()):
                    continue

                Link = link.get_by_owner_url(user_id, want_link['url'])
                User = user.get(user_id)
                message_text = str(User.template)
                message_text = message_text.replace('[link_name]', Link.name)
                message_text = message_text.replace('[title]', want_["name"])
                message_text = message_text.replace('[desc]', want_["description"][:500] + '...')
                message_text = message_text.replace('[parent_cat]', want_["parentCategoryName"])
                message_text = message_text.replace('[cat]', want_["categoryName"])
                message_text = message_text.replace('[user]', want_["userName"])
                message_text = message_text.replace('[user_link]', f'<a href="https://kwork.ru/user/{want_["name"]}">ссылка</a>')
                message_text = message_text.replace('[budget]', str(want_["priceLimit"].split('.')[0]))
                message_text = message_text.replace('[accept_budget]', str(want_["possiblePriceLimit"]))
                message_text = message_text.replace('[hired]', str(want_["userWantsHiredPercent"]))
                message_text = message_text.replace('[offers]', str(want_["userWants"]))
                message_text = message_text.replace('[active_offers]', str(want_["userActiveWants"]))

                if BOT_USERNAME in message_text:
                    continue

                # message_text = re.sub(r'[^a-zA-Z0-9]' , '', message_text)

                # if len(message_text) > 500:
                    # message_text = message_text[:1021] + '...'

                try:
                    await send_message(
                        chat_id=user_id,
                        text=message_text,
                        disable_web_page_preview=True,
                        reply_markup=markup.want(want_["id"])
                    )

                    want.send(want_['id'])
                    sended_messages += 1
                    if sended_messages >= 20:
                        await asyncio.sleep(1)
                        sended_messages = 0

                except:
                    user.set_active(user_id, False)
    
    # scheduler.remove_job('sender')
    # print(f'Poster: {len(wants_list)} - {datetime.now()}')


scheduler.add_job(send_wants, 'interval', seconds=30, id='sender')
