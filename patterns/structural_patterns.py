from time import time

# collects Routes at the application level (AppRoute class)
routes = {}

# structural Pattern Decorator
class AppRoute:
    """Decorator for Classes"""
    def __init__(self, url):
        # Get URL
        self.url = url

    def __call__(self, cls, *args, **kwargs):
        """ Decorator's method """
        routes[self.url] = cls()
        # required to support the operation of the classical method 'urls.py ' (calling __call__ without arguments)
        return cls


# структурный паттерн - Декоратор
class Debug:

    # def __init__(self, name):
    #
    #     self.name = name

    def __call__(self, cls):
        """ Decorator's method """

        # это вспомогательная функция будет декорировать каждый отдельный метод класса, см. ниже
        def timeit(method):
            '''
            нужен для того, чтобы декоратор класса wrapper обернул в timeit
            каждый метод декорируемого класса
            '''
            def timed(*args, **kw):
                ts = time()
                result = method(*args, **kw)
                te = time()
                delta = te - ts

                print(f'debug --> {method.__qualname__} выполнялся {delta:2.2f} ms')
                return result

            return timed

        return timeit(cls)
