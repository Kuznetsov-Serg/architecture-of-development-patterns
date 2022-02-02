from jinja2 import FileSystemLoader
from jinja2.environment import Environment



def render(template_name, folder='templates', **kwargs):
    """
    :param template_name:
    :param folder: folder with pattern
    :param kwargs: parameters to pass to the template
    :return:
    """

    env = Environment()                         # creating an environment object
    env.loader = FileSystemLoader(folder)       # folder for searching for templates
    template = env.get_template(template_name)  # take the template specified in the parameters
    return template.render(**kwargs)
