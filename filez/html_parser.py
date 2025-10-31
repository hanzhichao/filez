from html.parser import HTMLParser

SINGLE_TAGS = ['br', 'hr', 'img', 'input', 'param', 'meta', 'link']


class HtmlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.data = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SINGLE_TAGS:
            return self.handle_startendtag(tag, attrs)
        self.stack.append(dict(tag=tag, attrs=dict(attrs), children=[], text=''))

    def handle_endtag(self, tag):
        self.data = current = self.stack.pop()
        if self.stack:
            parent = self.stack[-1]
            parent['children'].append(current)

    def handle_startendtag(self, tag, attrs):
        if self.stack:
            parent = self.stack[-1]
            parent['children'].append(dict(tag=tag, attrs=dict(attrs), children=[], text=''))

    def handle_data(self, data):
        if not data.strip():
            return
        if self.stack:
            self.stack[-1]['text'] = data.strip()
