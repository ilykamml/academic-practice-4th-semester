import datetime
from typing import TYPE_CHECKING, List, Set
import feedparser

if TYPE_CHECKING:
    from user_class import User


class RSSSource:

    def __init__(self, url: str):
        self.url = url
        self.last_entry = None
        self.subscribers = set()
        self.processed_entries = self.processed_entries = {}

    def add_subscriber(self, user: "User"):
        self.subscribers.add(user)

    def remove_subscriber(self, user: "User"):
        self.subscribers.discard(user)

    def fetch_entries(self) -> list:
        feed = feedparser.parse(self.url)
        if feed.bozo:
            return []
        return feed.entries
    
    def filter_new_entries(self, entries: list) -> list:
        new_entries = []
        now = datetime.now()
        cutoff_time = now - datetime.timedelta(days=7)
        self.processed_entries = {
            entry_id: time for entry_id, time in self.processed_entries.items()
            if time > cutoff_time
        }
        for entry in entries:
            entry_id = entry.get('id')
            if entry_id not in self.processed_entries:
                new_entries.append(entry)
                self.processed_entries[entry_id] = datetime.now()
        return new_entries

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
    
    def get_sources(self) -> List[RSSSource]:
        return self.sources.values()
    
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