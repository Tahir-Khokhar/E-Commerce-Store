# Standard pagination class for the REST API.

from rest_framework.pagination import PageNumberPagination  # Base pagination class provided by DRF.


# Custom pagination class.
class StandardPagination(PageNumberPagination):

    # Number of items returned per page by default.
    page_size = 12

    # Allows the client to change the page size using ?page_size=.
    page_size_query_param = 'page_size'

    # Maximum number of items allowed in one page.
    max_page_size = 100
