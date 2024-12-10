from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rss_class import RSSSource

class User:

    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username
        self.subscribes = set()

    def add_sub(self, rss: "RSSSource"):
        rss.add_subscriber(self)
        self.subscribes.add(rss)

    def del_sub(self, rss: "RSSSource"):
        if rss in self.subscribes:
            self.subscribes.discard(rss)
            rss.remove_subscriber(self)
    
    def __str__(self):
        st = f'\n---\n{self.username}\n{self.id}'
        for sub in self.subscribes:
            st += f'\n{sub.url}'
        return st


class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, id: int, username: str):
        if not self.user_exists(id):
            self.users[id] = User(id, username)

    def get_user(self, user_id: int) -> User | None:
        return self.users.get(user_id)
    
    def remove_user(self, user_id: int):
        if self.user_exists(user_id):
            del self.users[user_id]

    def user_exists(self, user_id: int) -> bool:
        return user_id in self.users
    
    def __str__(self, *args, **kwds):
        st = ''
        for user in self.users:
            st += f'{self.users[user]}'
        return st