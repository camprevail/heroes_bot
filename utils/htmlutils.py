import sys, aiohttp, asyncio, traceback

async def make_request(client, url):
    async with client.get(url) as response:
        try:
            content = await response.read()
            return url, content
        except:
            traceback.print_exc(file=sys.stdout)


async def fetch(conn, urls):
    async with aiohttp.ClientSession(connector=conn) as client:
        tasks = [asyncio.create_task(make_request(client, url)) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {k[0]: k[1] for k in results} # returns dict of urls and images.


def getinfo(soup):
    """
    Parses each build in the BeautifulSoup object into a dict.
    Example buildsinfo json:
        {
            "Symbiote Build": {
                "recommend": "Recommended",
                "recommend_color": (0, 255, 0),
                "code": "[T1131223,Abathur]",
                "levels": {
                    "Level 1": {
                        "visuals": [
                            "heroes_build_talent_tier_yes",
                            "heroes_build_talent_tier_no",
                            "heroes_build_talent_tier_no",
                            "heroes_build_talent_tier_no"
                        ],
                        "url": "http://static.icy-veins.com/images/heroes/icons/large/storm_ui_icon_arthas_howlingblast.jpg"
                    },
                    "Level 4: {
    """

    builds = soup.find_all('div', 'heroes_build') # list of builds
    buildsinfo = {}

    for b in builds:
        name = b.find('div', 'heroes_build_header').h3.text.strip()
        recommend = b.find('div', 'heroes_build_header').span.text.strip()
        code = b.find(class_ = 'talent_build_copy_button').input.get('value')
        buildsinfo[name] = {'recommend': recommend}
        if recommend == 'Recommended':
            buildsinfo[name]['recommend_color'] = (0, 255, 0)
        elif recommend == 'Situational':
            buildsinfo[name]['recommend_color'] = (255, 177, 0)
        elif recommend == 'Not recommended':
            buildsinfo[name]['recommend_color'] = (255, 70, 70)
        elif recommend == 'Beginner':
            buildsinfo[name]['recommend_color'] = (0, 255, 255)

        buildsinfo[name]['levels'] = {}
        buildsinfo[name]['code'] = code
        for t in b.find_all('div', 'heroes_build_talent_tier'): # iterate through the levels
            level = t.find(class_='heroes_build_talent_tier_subtitle').text
            buildsinfo[name]['levels'][level] = {}
            visuals = t.find(class_='heroes_build_talent_tier_visual').findChildren('span')
            buildsinfo[name]['levels'][level]['visuals'] = []
            for v in visuals:
                buildsinfo[name]['levels'][level]['visuals'].append(v.get('class')[0])
            buildsinfo[name]['levels'][level]['url'] = 'http:' + t.find(class_='heroes_build_talent_tier_recommended').img.get('src')
    return buildsinfo