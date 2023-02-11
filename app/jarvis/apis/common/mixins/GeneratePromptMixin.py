from rest_framework.response import Response


class GeneratePromptMixin:
    """
    Generate a prompt from a model instance.
    """

    def generate(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # type: ignore
        serializer = self.get_serializer(  # type: ignore
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = self.perform_generate(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)

    def perform_generate(self, serializer):
        return serializer.generate()
