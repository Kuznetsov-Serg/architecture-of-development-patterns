from framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html')


class About:
    def __call__(self, request):
        return '200 OK', render('about.html')


class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))