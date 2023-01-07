from django.urls import path
from completion.apis import DocumentCompleteAPI, DocumentListCreateAPI, DocumentRetrieveUpdateDestroyAPI


app_name = 'completion'
urlpatterns = [
    path('document/<int:pk>/complete',
         DocumentCompleteAPI.as_view(), name='document-complete'),
    path('document/<int:pk>/', DocumentRetrieveUpdateDestroyAPI.as_view(),
         name='document-retrieve'),
    path('document/', DocumentListCreateAPI.as_view(), name='document-list'),

]
