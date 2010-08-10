import os, re, string, random
from redis import Redis


class Tedis(object):
    """
    A class providing some simple tools to use when testing code that uses Redis
    as a queue, specifically with ResQ.

    The idea is that a user can provide a list of items with specially formatted
    text, such that the code can do replacements in the text according to rules
    given inside the placeholders.

    Example Usage::
        >>> from tedis import Tedis

        >>> template = "There are {{int:6}} items left in the {{ str:10 }} shopping cart{{str:15}}"
        >>> tester = Tedis(server = 'localhost:6379', redis_key = 'bacon')
        >>> tester.load(template, 10000)
        >>> tester.dump()
        >>> tester.close()

    The class will then write the given number of elements to the Redis server
    making each random so that testing can be more reliable.

    """

    def __init__(self, server = 'localhost:6379',  password = None, redis_key = 'test'):
        super(Tedis, self).__init__()
        self._set_redis(server)
        self.redis_key = redis_key
        if password:
            self.redis.auth(password)

    def _set_redis(self, server):
        if isinstance(server, basestring):
            self.dsn = server
            host, port = server.split(':')
            self.redis = Redis(host = host, port = int(port))
        elif isinstance(server, Redis):
            self.dsn = '%s:%s' % (server.host, server.port)
            self.redis = server
        else:
            raise Exception("I don't know what to do with %s" % str(server))

    def _save_to_redis(self, payload):
        """Save a payload to redis."""
        self.redis.rpush(self.redis_key, payload)

    def _format_payload(self, template):
        """Using a user-provided template, format a payload with the replacements."""
        placeholders = self._find_placeholders(template)
        for ph_detail in placeholders:
            if ph_detail['type'] == 'int':
                template = template.replace(ph_detail['original_string'], self._create_random_int(ph_detail['size']), 1)
            if ph_detail['type'] == 'str':
                template = template.replace(ph_detail['original_string'], self._create_random_string(ph_detail['size']), 1)
        return template

    def _create_random_string(self, size):
        """Creates a random string of the given size."""
        # implement string types
        return ''.join(random.choice(string.letters) for i in range(size))

    def _random_with_N_digits(self, size):
        range_start = 10**(size-1)
        range_end = (10**size)-1
        return str(random.randint(range_start, range_end))

    def _create_random_int(self, size):
        """Created a random integer of the given size."""
        return self._random_with_N_digits(size)

    def _find_placeholders(self, template):
        """Finds the placeholders in the user-provided template."""
        variable_regex = re.compile('(\{\{\s?([A-Za-z0-9\:]+)\s?\}\})', re.MULTILINE)
        matches = variable_regex.findall(template)
        placeholders = []
        for match in matches:
            parts = match[1].split(':')
            ph_detail = {}
            ph_detail['original_string'] = match[0]
            ph_detail['type'] = parts[0]
            ph_detail['size'] = int(parts[1])
            placeholders.append(ph_detail)
        return placeholders

    def load(self, template, size):
        """
        This is the public method the user calls to stuff a bunch of crap
        into his/her redis server by providing a template and the number of
        items to create.

        """
        for i in range(size):
            payload = self._format_payload(template)
            self._save_to_redis(payload)

    def dump(self):
        """Remove all keys and values from the Redis DB."""
        self.redis.flushdb()

    def close(self):
        """Close the underlying redis connection."""
        self.redis.connection.disconnect()
    