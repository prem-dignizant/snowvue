from rest_framework.pagination import PageNumberPagination

class BuyerContractPagenation(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page'  # Allow clients to set custom page size via query param
    max_page_size = 100  # Max number of items per page