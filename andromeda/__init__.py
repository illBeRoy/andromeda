import functools
import flask

from .endpoint import HTTP_METHODS, Endpoint
from .parsers import BodyParser, HeadersParser, QuerystringParser
from .exception import HTTPException
from .context import Context


class Server(object):

    def __init__(self, name, *args, **kwargs):
        self._app = flask.Flask(name, *args, **kwargs)
        self._app.errorhandler(404)(functools.partial(self._error_handler, 404, 'not found'))
        self._endpoints_count = 0
        self._context = Context()
        self._middlewares = []

    def run(self, port, debug=False):
        self._app.run('0.0.0.0', port, debug)

    def use(self, cls):
        if isinstance(cls, list):
            for endpoint in cls:
                self.use(endpoint)

        else:
            for method in HTTP_METHODS:
                self._app.add_url_rule(cls.url,
                                       'endpoint.{0}'.format(self._endpoints_count),
                                       view_func=functools.partial(self._endpoint_handler, cls, method),
                                       methods=[method])

                self._endpoints_count += 1

    def add_context(self, attribute_name, context_value):
        setattr(self._context, attribute_name, context_value)

    def middleware(self, middleware):
        self._middlewares.append(middleware(self._app))

    def _endpoint_handler(self, endpoint_cls, method, **uri_params):
        request = flask.request

        try:
            # create instance in the request and server contexts
            endpoint_instance = endpoint_cls(request, self._context)

            # run endpoint handler
            response = getattr(endpoint_instance, method)(**uri_params)

            # return the outcome
            return self._render_response(response)

        except HTTPException as err:
            # return rendered exception
            return self._error_handler(err.status, err.message, err)

        except Exception as err:
            # return rendered exception with 500
            return self._error_handler(500, str(err), err)

    def _error_handler(self, status, message, err=None):
        response = flask.make_response((flask.jsonify({'status': status, 'message': message}), status))

        for middleware in self._middlewares:
            middleware(response)

        return response

    def _render_response(self, response):
        if isinstance(response, tuple):
            # response = list(response)
            response[0] = flask.jsonify(response[0])
            response = tuple(response)
        else:
            response = flask.jsonify(response)

        response = flask.make_response(response)

        for middleware in self._middlewares:
            middleware(response)

        return response
