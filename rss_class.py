from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user_class import User


class RSSSource:

    def __init__(self, url: str):
        self.url = url
        self.last_entries = []
        self.subscribers = set()

    def add_subscriber(self, user: "User"):
        self.subscribers.add(user)

    def remove_subscriber(self, user: "User"):
        self.subscribers.discard(user)

    def __str__(self):
        st = f'\n---\n{self.url}'
        for sub in self.subscribers:
            st += f'\n{sub.username}'
        return st
        


class RSSManager:
    def __init__(self):
        self.sources = {}

    def add_source(self, url: str):
        if not self.link_exists(url):
            self.sources[url] = RSSSource(url)

    def get_source(self, url: str) -> RSSSource | None: 
        return self.sources.get(url)
    
    def remove_source(self, url: str):
        if self.link_exists(url):
            del self.sources[url]

    def link_exists(self, url: str) -> bool:
        return url in self.sources
    
    def __str__(self, *args, **kwds):
        st = ''
        for source in self.sources:
            st += f'{self.sources[source]}'
        return st