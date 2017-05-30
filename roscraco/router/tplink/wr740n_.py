from roscraco.router.tplink.base import TplinkBase, RouterBase
import urllib, hashlib, sys, base64, re
from roscraco.exception import RouterFetchError, RouterParseError
from roscraco.router.tplink.base import TrafficStats
from roscraco.router.tplink.wr740n import Tplink_WR740N as OLD_Tplink_WR740N

class Tplink_WR740N_(OLD_Tplink_WR740N):
    def _prepare_base64_auth_string(self):
        auth_string = '{0}:{1}'.format(self.username, hashlib.md5(self.password.encode('utf-8')).hexdigest())
        if sys.version_info[0] >= 3:
            auth_string = bytes(auth_string, 'ascii')
        encoded = base64.b64encode(auth_string)
        if sys.version_info[0] >= 3:
            encoded = encoded.decode('ascii')
        return encoded
    
    @property
    def url_encode(self):
        auth_string = '{0}:{1}'.format(self.username, hashlib.md5(self.password.encode('utf-8')).hexdigest())
        auth_string = bytes(auth_string, 'ascii')
        encoded = base64.b64encode(auth_string)
        encoded = encoded.decode('ascii')
        return encoded
    
    @property
    def url_base_self():
        return 'http://%s:%d/userRpm/LoginRpm.htm?Save=Save' % (self.host, self.port)

    def _perform_http_request(self, *args, **kwargs):
        kwargs['headers'] = [
            ('Accept-Encoding', 'gzip,deflate'),
            ('Referer', self.url_base_),
            ('Cookie', 'Authorization=' + urllib.parse.quote('Basic {0}'.format(self.url_encode))),
        ]
        return RouterBase._perform_http_request(self, *args, **kwargs)

    def connect(self, timeout=7.0):
        req = urllib.request.Request(self.url_base_)

        req.add_header('Accept-Encoding', 'gzip,deflate')
        req.add_header('Referer', 'http://{0}'.format(self.host + '/'))
        req.add_header('Cookie', 'Authorization=' + urllib.parse.quote('Basic {0}'.format(self.url_encode)))

        regex = re.compile(r'{0}:{1}'.format(self.host, self.port)+'/(.*?)/userRpm/Index.htm')
        search_object = regex.findall(str(urllib.request.urlopen(req, timeout=timeout).read()))
        return search_object

    def get_router_info(self):
        search_object = self.connect()
        if not search_object:
            raise RouterFetchError("< HTTPError 401: 'N/A' >")

        setattr(Tplink_WR740N_, 'url_base', 'http://{0}:{1}'.format(self.host, self.port) + '/' + search_object[0] + '/userRpm/')
        return super().get_router_info()

    def get_traffic_stats(self):
        return _parse_traffic_stats(self._get_status_array('statistList'))

def _parse_traffic_stats(data_array):
    data_array = data_array[:4]
    if len(data_array) != 4:
        raise RouterParseError('Unexpected stats size: %d' % len(data_array))
    data_array = map(lambda x: int(x.replace(',', '')), data_array)
    return TrafficStats(*data_array)
