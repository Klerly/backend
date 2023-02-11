from rest_framework.generics import GenericAPIView
from jarvis.apis.common import mixins


class GenerateAPIView(mixins.GeneratePromptMixin,
                      GenericAPIView):
    """
    Concrete view for generating a prompt.
    """

    def post(self, request, *args, **kwargs):
        return self.generate(request, *args, **kwargs)
