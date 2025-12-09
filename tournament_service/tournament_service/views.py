from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


# Health check endpoint (excluded from API schema)
@extend_schema(exclude=True)
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})