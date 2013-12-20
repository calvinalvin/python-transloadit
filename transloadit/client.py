import hashlib
import hmac
import urlparse
import httplib
import mimetypes
from datetime import datetime, timedelta

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO


try:
  from django.utils import simplejson as json
except ImportError:
  import simplejson as json


BASE_API = 'http://api2.transloadit.com/assemblies'
FILE_BOUNDARY = '----------Python_Transloadit_Client_Boundary_$'
CRLF = '\r\n'


class TransloaditClient(object):
  def __init__(self, key, secret, api=None):
    self.key = key
    self.secret = secret
    if api:
      self.api = api
    else:
      self.api = BASE_API

  def _sign_request(self, params):
    return hmac.new(self.secret, json.dumps(params),
      hashlib.sha1).hexdigest()

  def _send_post_request(self, files, **fields):
    parts = urlparse.urlparse(self.api)
    content_type, body = self._encode_post_request(fields, files)
    req = httplib.HTTP(parts[1])
    req.putrequest('POST', parts[2])
    req.putheader('Content-Type', content_type)
    req.putheader('Content-Length', str(len(body)))
    req.endheaders()
    req.send(body)
    errcode, errmsg, headers = req.getreply()
    return json.loads(req.file.read())

  def _send_get_request(self, assembly_id):
    parts = urlparse.urlparse(self.api)
    req = httplib.HTTP(parts[1])
    req.putrequest('GET', parts[2] + '/' + assembly_id)
    req.endheaders()
    errcode, errmsg, headers = req.getreply()
    f = req.getfile()
    data = f.read() # Get the raw HTML
    f.close()
    return json.loads(data)

  def _encode_post_request(self, fields, files):
    body = StringIO()

    for key, value in fields.iteritems():
      body.write('--%s%s' % (FILE_BOUNDARY, CRLF))
      body.write('Content-Disposition: form-data; name="%s"%s' % (key, CRLF))
      body.write(CRLF)
      body.write(value)
      body.write(CRLF)

    if files:
      for key, filename, value in files:
        content_type = self._get_content_type(filename)
        body.write('--%s%s' % (FILE_BOUNDARY, CRLF))
        body.write('Content-Disposition: form-data;' + \
          ' name="%s"; filename="%s"%s' % (key, filename, CRLF))
        body.write('Content-Type: %s%s' % (content_type, CRLF))
        body.write(CRLF)
        body.write(value)
        body.write(CRLF)

    body.write('--%s--%s' % (FILE_BOUNDARY, CRLF))
    body.write(CRLF)
    content_type = 'multipart/form-data; boundary=%s' % FILE_BOUNDARY
    return content_type, body.getvalue()

  def _get_content_type(self, filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

  def create_assembly(self, files=None, **params):
    if 'auth' not in params:
      params['auth'] = {
        'key': self.key,
        'expires': (datetime.now() +
          timedelta(days=1)).strftime('%Y/%m/%d %H:%M:%S')
      }

    fields = {
      'params': json.dumps(params),
      'signature': self._sign_request(params)
    }

    return self._send_post_request(files, **fields)

  def get_assembly(self, assembly_id):
    return self._send_get_request(assembly_id)
