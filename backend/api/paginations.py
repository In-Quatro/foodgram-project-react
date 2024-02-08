from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор для изменения количества объектов
    на странице Рецептов через параметр limit."""
    page_size_query_param = 'limit'
