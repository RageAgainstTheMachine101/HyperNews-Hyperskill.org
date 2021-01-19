import json
import datetime as dt

from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect


with open(settings.NEWS_JSON_PATH) as data:
    news = json.load(data)

template_start = '''<h4>{date}</h4>
<ul>
'''
template_list = '''  <li><a target="_blank" href="/news/{news_id}/">{title}</a></li>'''
template_end = '''</ul>'''


def to_main_view(request):
    return redirect('/news')


class MainView(View):
    def get(self, request, *args, **kwargs):
        blocks = {}
        templated_blocks = []
        news_list = []
        search = request.GET.get('q')

        for n in news:
            if search:
                if search not in n['title']:
                    continue

            created = n['created'].split()[0]

            if created in blocks.keys():
                blocks[created].append(n)
            else:
                blocks[created] = []
                blocks[created].append(n)

        for block in blocks:
            for n in blocks[block]:
                news_list.append(template_list.format(news_id=n['link'], title=n['title']))

            current = template_start.format(date=block) + ''.join(news_list) + template_end
            templated_blocks.append(current)
            news_list = []

        sorted_result = ''.join(sorted(templated_blocks, reverse=True))

        return render(request, "main.html", context={"blocks": sorted_result})


class NewsView(View):
    def get(self, request, news_id=None, *args, **kwargs):
        req_news = "Oops!"

        for piece in news:
            if news_id == piece.get('link'):
                req_news = piece
                break

        return render(
            request, 'news.html', context={"req_news": req_news}
        )


class CreateView(View):
    max_id = max(int(piece.get('link')) for piece in news)
    news_id = max_id + 1

    def get(self, request, news_id=None, *args, **kwargs):
        return render(request, "create_news.html", context={})

    def post(self, request, *args, **kwargs):
        news_title = request.POST.get('title')
        news_text = request.POST.get('text')

        with open(settings.NEWS_JSON_PATH, 'w') as data:
            news.append({'created': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         'text': news_text,
                         'title': news_title,
                         'link': self.news_id})
            json.dump(news, fp=data)

        return redirect('/news')
