from django.urls import path

from perfumes.views import perfume_list, brand_list, OfferAPIView, OfferDetailAPIView, \
    category_list, perfume_detail, review_list_create, review_replies, filteredProductsView

urlpatterns = [
    path('', perfume_list, name='perfume-list'),
    path('<int:pk>/', perfume_detail, name='perfume-list'),
    path('brands/', brand_list, name='brand-list'),
    path('categories/', category_list, name='category-list'),
    path('offers/', OfferAPIView.as_view(), name='make-offer'),
    path('offers/<int:perfume_id>/', OfferAPIView.as_view(), name='offer-list-perfume'),
    path('offer-detail/<int:offer_id>/', OfferDetailAPIView.as_view(), name='offer-detail'),
    path('reviews/<int:perfume_id>/', review_list_create, name='review_list_create'),
    path('reviews/<int:perfume_id>/<int:review_id>/', review_list_create, name='review-manage'),
    path('reviews/<int:review_id>/replies/', review_replies, name='review-replies'),

    path('filtered-products/', filteredProductsView, name='filtered-products'),

]
