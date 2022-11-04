from rest_framework.pagination import PageNumberPagination


class SmearPagination(PageNumberPagination):
    """Pagination settings for smear models

    Default page size = 25 and can be set up to 100 via the 'page_size' query parameter. Page
    selection is done via the 'page' parameter.
    """

    page_query_param = "page"
    page_size = 25
    max_page_size = 100
    page_size_query_param = "page_size"
    last_page_strings = ()
