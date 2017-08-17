![andromeda](icon.png)

# Andromeda
declarative, class-driven framework written around flask

### Abstract
Andromeda is a mini-framework that's built around the world-famous library flask, and aims to define a simple yet explicit interface for creating expressive, api-driven servers.

Andromeda abstracts away the technicalities of setting up endpoints, making room for your business logic to shine. With Andromeda, the *request/response* flow becomes a simple *input/output* method driven logic that takes advantage of the good old pythonic control flow: returning a value yields a valid (`2xx`) response, and raising an exception yields an errorneous one.

### Motivation
Having worked on many server \ client systems in the past couple of years, I've realized that most of my projects have similar foundations; whether they were written in python, java, javascript, swift or go, the first thing I always did was to create a layer of abstraction that decouples business logic from request \ response handling.

Andromeda was born out of that process, as a reusable piece of code which I utilized as the backbone of many of my restful api servers. Since it was born out of my own necessities, it is somewhat opinionated (for example, it uses json requests and responses as default), but as part of making it a standalone project, I put effort into making Andromeda into a framework that's more general-purposed and centered on what (the abstraction) and less of how (which headers? body format? etc).

Why Andromeda? Good question. Between micro-frameworks (such as flask) which provide nothing but the essence of the server, to MVC frameworks (such as django) which provide zero-conf servers that do everything from the get-go, there are not too many contestants for the usual rapid developer. If you aim for a microframework, you might end up installing four or five extensions just to get it to do what you want it to, and if you go with big frameworks for small to medium projects, you can end up getting too much for your own good, often losing control of the entire flow of your app. Andromeda aims for that average user, which just wants to expose their business logic to the outside world. You can regard to Andromeda as the "AWS Lambda" for flask - you can ship an entire Andromeda app without mounting it on a single server.

### Installation
Installing Andromeda is easiest using pip. You can install it by executing:

`$ pip install andromeda`

Or by clonning and installing the dependencies specified under `requirements.txt`.

### Usage

#### Getting Started
We'll do so in three basic steps:

* Import the andromeda package:

```python
import andromeda
```

* Define a new endpoint specification which supports `[GET] /`, by deriving it from the andromeda.Endpoint base class:

```python
class Endpoint(andromeda.Endpoint):

	url = '/'
	
	def get(self):
		return 'hello, world'
```

* And create a server instance, which uses the endpoint and listens on the port of of your choice:

```python
app = andromeda.Server(__name__)
app.use(Endpoint)
app.run(3000)
```

And we're done! Let's run the program and open `localhost:3000` in our browser.

#### In Depth

**Server**

The server is the central component of the Andromeda system. It is the de-facto imperative interface to create, mount and run the entierity of the application.

*Primary concerns:*

1. Interpret, register and properly mount Endpoint classes.
2. Register and mount middleware.
3. Provide means for dependency injection (`context`)
4. Handle incoming requests, route them, launch the relevant endpoint class and method and wrap around them, providing environment and callbacks.

*The imperative interface:*

* `app.use` - register an Endpoint class or a list of classes
* `app.add_context` - adds an object to the context of the server. more about contexts soon
* `app.middleware` - registers and applies a middleware to the server. more about middlewares soon
* `app.run` - starts listening on the given port

**Endpoints**

The Endpoint class is the de-facto contract between Andromeda and you, the applicative programmer. By defining endpoints, you can simply lay out your api **logic** without having to contaminate it with the regular request handling boilerplate.

In order to define an endpoint, you **must** derive it from `andromeda.Endpoint`, as it takes care of several fallbacks and initialization boilerplate.

Let's break down what makes an endpoint:

*URL*

In order to define the URL from which an endpoint should be available, you should define your own `url` static member for your class:

```python
class Endpoint(andromeda.Endpoint):

	url = '/foo'
```

URLs are compliant with [flask url formats](http://flask.pocoo.org/snippets/category/urls/), where url parameters are being passed as **named parameters** to the endpoint methods.

*HTTP Methods*

The http methods, and their underlying logic, are accessible by implementing instance methods in your Endpoint class which match their name; this means that `def get(self):` will define the handler for the GET request, `def post(self):` for POST, etc.

The default Endpoint class implements handlers for all of the generally used endpoints, where they all simply yield an `405: method not allowed` response.

Endpoints methods act as simple functions, which can imperatively process input and then return an output. The output is then caught by the server's framework and is returned to the user. The value itself can be any json serializable value, and is returned by the server as json<sup>[1]</sup>. 

There are three ways to return values from methods:

* Simply return the response

```python
def get(self):
	return 'hello, world'
```

This will return a response with HTTP status 200, the body being the returned value.

* Return response **and** status code:

```python
def post(self):
	return 'created!', 201
```

In such cases, the tuple will be interpreted into `(returned_value, status_code)`, and the response will bear the specified http status code, the body being the second value.

* Raise an exception

```python
def delete(self):
	raise andromeda.HTTPException(401, 'Unauthorized')
```

In cases where an exception is thrown, the server returns an automatic response containing `{status, message}`. The default status code that's used when an exception occures is `500`, but it is configurable by raising an HTTPException (see respective description).

**Parsers**

As HTTP requests have several ways of defining data, each with its own semantic meaning, I've had to come up with a uniform approach that would support taking the same measures for parsing requests, without having to explicitly and imperatively parse the request.

In order to address that, Andromeda provides you with a system of RequestParsers. They let you define the parameters which your expecting to get and do the parsing for you - whether its typecasting, rejecting invalid inputs or verifying fields to not be missing.

The RequestParsers work much like the [argparse](https://docs.python.org/3/library/argparse.html) package, and take great inspiration from flask restful's [reqparse](flask-restful.readthedocs.io/en/0.3.5/reqparse.html).

There are three types of RequestParsers:

* BodyParser, parses paramters from the body of a json-compliant request
* QuerystringParser, parses querystring parameters embedded in the url (`?param=val`)
* HeadersParser, parses the values of headers (dashes in header's key become underscores in args namespace - `x-my-header` will become `x_my_header`)

Example:

```python
def post(self):
	parser = BodyParser()
	parser.add_argument('name', help='name of person', type=str, required=True)
	args = parser.parse_args()
	
	return 'Hello, ' + args.name
```

This will automatically raise a `400 - Bad Request` exception in case the "name" field is missing, as it is set to be "required".

**Exceptions**

Exceptions are first-class citizens in the pythonic control flow, and so they are in Andromeda endpoints. You shouldn't be shy to use them - raise them whenever something didn't go as expected. Andromeda knows how to handle them, and will propagate them to the user whose making the requests.

In addition, Andromeda provides an Exception class called HTTPException, which allows you to set an HTTP status in addition to the message. Andromeda's server expects those kinds of exceptions, and formats the response accordingly.

**Context**

As we said before, the main goal of Andromeda is to provide an abstraction as thick as possible between the server and the overlying business-logic.

Still, some operations should be carried in the context of the environment in which the endpoints are being run, such as io operations, database read\writes or simply calling outter interfaces. 

For that matter exactly, Andromeda implments a context mechanism, avialable to each endpoint through `self.context`. The context is but a simple dependency injection pipeline, allowing you to provide your endpoints with objects originating from other parts of your program, such as ORMs, adapters, computational units, etc.

Example:

```python
app = andromeda.Server(__name__)
app.add_context('orm', MySQLiteOrm())
```

...

```python
class Endpoint(andromeda.Endpoint):
	
	url = '/users'
	
	def get():
		return self.context.orm.list_all_users()
```

**Request**

Each Endpoint instance can access the original flask request through `self.request`. This is an antipattern, though, and is only there so it could be accessed as a workaround in specific edge cases. Use with caution.

**Middleware**

Endpoints are good for defining pipelines, actions and interfaces, but when you want to define your server's global behaviour, you'll want to use middleware. As opposed to Endpoints, which define your internal business logic, middleware define the technicalities of handling requests and responses on the server's end.

An example for such global behaviour would be CORS: it does not concern your business logic, but each outgoing response should contain the respective `Access-Control-Allow-Origin: *` headers.

Middleware are functions which can be used with an Andromeda server. They accept the server's internal flask app as input, and produce another function that's called with every individual response. It is perfectly fine for them to **mutate** the flask app or the response, as they are not expected to return any related value.

Example:

```python
def foobar_middleware(flask_app):

	def on_response(response)
		response.headers['x-foo'] = 'bar'	
		
	return on_response
```

...

```python
app.middleware(foobar_middleware)
```

This will make every outgoing response to contain the `x-foo: bar` header.

#### Project structure suggestion
It is suggested to store all of the endpoints under a package called `endpoints`, which exports the list of all the endpoints the application should be using, making it agnostic to which endpoints they actually are.

In case there are multiple groups of endpoints, you may want to divide them into sub-packages, where the topmost packages simply concatenate the lists exported by their subpackages.

In the entry level script, simply import the list from the `endpoints` package and mount it into your server!

### What's next
1. Add thorough tests (sanity first, then unittests)
2. Create and upload packages for commonly used middleware (such as CORS)
3. Test kit for testing applicative endpoints in your app

### Attributions
Icon made by Freepik from [flaticon.com](httsp://www.flaticon.com)

-

**<sup>[1]</sup>** Treating request and response bodies as json is a point of debate, as doing so makes the server very opinionated. This behaviour can currently be overriden using middleware, and in the future it will probably be extracted and no longer be the default behaviour.
