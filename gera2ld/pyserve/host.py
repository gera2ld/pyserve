class Host:
    def __init__(self, netloc):
        if isinstance(netloc, Host):
            hostname, port, username, password = netloc.hostname, netloc.port, netloc.username, netloc.password
        elif isinstance(netloc, str):
            userinfo, _, hostinfo = netloc.rpartition('@')
            hostname, _, port = hostinfo.rpartition(':')
            port = int(port)
            if hostname.startswith('[') and hostname.endswith(']'):
                hostname = hostname[1:-1]
            if userinfo:
                username, _, password = userinfo.partition(':')
            else:
                username = password = None
        elif len(netloc) == 2:
            hostname, port = netloc
            username = password = None
        else:
            hostname, port, username, password = netloc
        self.hostname, self.port, self.username, self.password = hostname, port, username, password

    @property
    def host(self):
        hostname = f'[{self.hostname}]' if ':' in self.hostname else self.hostname
        return f'{hostname}:{self.port}'

    def __str__(self):
        userinfo = ''
        if self.username:
            userinfo += self.username
            if self.password:
                userinfo += ':' + self.password
            userinfo += '@'
        return userinfo + self.host
