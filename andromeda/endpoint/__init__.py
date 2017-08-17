import andromeda.exception


HTTP_METHODS = ['get', 'post', 'put', 'delete', 'options', 'head', 'patch']


class Endpoint(object):
    '''
    Declares an endpoint to be instated by the server.
     
    Each of the methods below represents a handler that is automatically registered as a flask route.
    
    Whenever a route is invoked, a new Endpoint instance is created. Therefore, endpoint classes CAN be stateful, but
    take notice that it is discouraged.

    Each of the created instances has two local variables: request and session. They are being passed from the server
    itself, and therefore any deriving class MUST accept them in their constructor.
    '''

    # the url for which the methods will be registered.
    # supports uri types and regexes, much like a flask route.
    # uri parts are passed as keyword arguments to the handlers.
    url = '/'

    def __init__(self, request, context):
        self.request = request
        self.context = context

    def get(self, **uri_parts):
        self._method_not_allowed()

    def post(self, **uri_parts):
        self._method_not_allowed()

    def put(self, **uri_parts):
        self._method_not_allowed()

    def delete(self, **uri_parts):
        self._method_not_allowed()

    def options(self, **uri_parts):
        self._method_not_allowed()

    def head(self, **uri_parts):
        self._method_not_allowed()

    def patch(self, **uri_parts):
        self._method_not_allowed()

    def _method_not_allowed(self):
        raise andromeda.exception.HTTPException(405, 'method not allowed')
