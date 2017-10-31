from django.http import HttpResponse
import simplejson
import traceback

def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = simplejson.dumps(objects)
            if 'callback' in request.GET:
                # a jsonp response!
                data = '%s(%s);' % (request.GET['callback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            traceback.print_exc()
            data = simplejson.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator
