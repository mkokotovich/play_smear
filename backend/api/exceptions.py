import logging
import sys
import traceback

from django.conf import settings
from django.http.response import Http404, HttpResponse
from rest_framework.response import Response
from rest_framework.serializers import ValidationError as SerializerValidationError
from rest_framework.views import exception_handler

LOG = logging.getLogger(__name__)


def add_stack_trace_to_response(response_data):
    if settings.DEBUG is True:
        exc_trace = None
        try:
            exc_type, exc_value, exc_trace = sys.exc_info()
            response_data["error"]["traceback"] = traceback.format_exception(exc_type, exc_value, exc_trace)
        finally:
            del exc_trace  # see https://docs.python.org/2/library/sys.html#sys.exc_info


def custom_exception_handler(exc, context):
    # First get the default exception
    response = exception_handler(exc, context)
    if response is None:
        response = Response(data=None, status=500)

    # Protect against bad error handling leading to bad error messages, wrap in try
    try:
        response_data = {"status": "error", "error": {}}

        if response is not None:
            # Add the HTTP status code to the response_data
            response_data["error"]["error_code"] = response.status_code

            if response.status_code >= 500:
                # log all exceptions above 500 as warnings
                LOG.error(
                    "Exception handling request for %s: %s. STATUS CODE: %s",
                    context["request"].method,
                    context["request"].path,
                    response.status_code,
                    exc_info=True,
                )
            elif response.status_code >= 400:
                # log all 4XX errors as info, as invalid requests aren't errors in the server
                LOG.info(
                    "Exception handling request for %s: %s. STATUS CODE: %s",
                    context["request"].method,
                    context["request"].path,
                    response.status_code,
                    exc_info=True,
                )

        # Errors from Django
        if isinstance(exc, HttpResponse):
            response_data["error"]["error"] = exc.reason_phrase
            response_data["error"]["error_description"] = str(exc)

        # Http404 errors come from Django and need to be treated differently
        elif isinstance(exc, Http404):
            response_data["error"]["error"] = "Error, not found"
            response_data["error"]["error_description"] = f"Could not find resource at {context['request'].path}"

        # Validation Errors will have a different format
        elif isinstance(exc, SerializerValidationError):
            response_data["error"]["error"] = "Validation Error"
            response_data["error"]["error_description"] = "Unable to validate input"
            response_data["error"]["validation_errors"] = {
                "error_description": "Unable to validate input",
                "meta": exc.detail,
            }

        # All errors from DRF should have a get_codes method
        elif hasattr(exc, "get_codes"):
            response_data["error"]["error"] = exc.get_codes()
            response_data["error"]["error_description"] = exc.detail

        # All remaining errors we should handle as best as we can
        else:
            response_data["error"]["error"] = str(exc.__class__.__name__)
            response_data["error"]["error_description"] = str(exc)

        # Only adds stack trace if DEBUG == True
        add_stack_trace_to_response(response_data)

        # Overwrite the response's data with our new object
        response.data = response_data

    except Exception:
        LOG.exception("Additional error occurred while attempting to handle exception")

    return response
