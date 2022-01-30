# get requests
class GetRequests:

    @staticmethod
    def parse_input_data_to_dict(data: str):
        return {key: val for key, val in (item.split('=') for item in data.split('&'))} if data else {}

    @classmethod
    def get_request_params(cls, environ):
        # getting the request parameters
        query_string = environ['QUERY_STRING']
        # fill in the dictionary with parameters
        request_params = cls.parse_input_data_to_dict(query_string)
        return request_params


# post requests
class PostRequests:

    @staticmethod
    def parse_input_data_to_dict(data: str) -> dict:
        return {key: val for key, val in (item.split('=') for item in data.split('&'))} if data else {}

    @staticmethod
    def get_wsgi_input_data(env) -> bytes:
        # get content
        content_length = env.get('CONTENT_LENGTH')
        return env['wsgi.input'].read(int(content_length)) if content_length else b''

    @classmethod
    def parse_wsgi_input_data(cls, data: bytes) -> dict:
        return cls.parse_input_data_to_dict(data.decode(encoding='utf-8')) if data else {}

    @classmethod
    def get_request_params(cls, environ):
        # get content
        data = cls.get_wsgi_input_data(environ)
        # convert to dict with decode
        data = cls.parse_wsgi_input_data(data)
        return data
