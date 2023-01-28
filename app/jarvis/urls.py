from django.urls import path
from jarvis.apis.image.dalle2 import (
    Dalle2PromptSellerCreateAPIView,
    Dalle2PromptSellerRetrieveUpdateDestroyAPIView,
    Dalle2PromptBuyerListAPIView,
    Dalle2PromptBuyerRetrieveAPIView
)
from jarvis.apis.language.gpt3 import (
    GPT3PromptSellerCreateAPIView,
    GPT3PromptSellerRetrieveUpdateDestroyAPIView,
    GPT3PromptBuyerListAPIView,
    GPT3PromptBuyerRetrieveAPIView
)


app_name = 'jarvis'
urlpatterns = [
    path('language/gpt3/seller', GPT3PromptSellerCreateAPIView.as_view(),
         name='gpt3-prompt-seller-create'
         ),
    path('language/gpt3/seller/<int:pk>', GPT3PromptSellerRetrieveUpdateDestroyAPIView.as_view(),
         name='gpt3-prompt-seller-detail'
         ),
    path('language/gpt3', GPT3PromptBuyerListAPIView.as_view(),
         name='gpt3-prompt-buyer-list'
         ),
    path('language/gpt3/<int:pk>', GPT3PromptBuyerRetrieveAPIView.as_view(),
         name='gpt3-prompt-buyer-detail'
         ),
    path('image/dalle2/seller', Dalle2PromptSellerCreateAPIView.as_view(),
         name='dalle2-prompt-seller-create'
         ),
    path('image/dalle2/seller/<int:pk>', Dalle2PromptSellerRetrieveUpdateDestroyAPIView.as_view(),
         name='dalle2-prompt-seller-detail'
         ),
    path('image/dalle2', Dalle2PromptBuyerListAPIView.as_view(),
         name='dalle2-prompt-buyer-list'
         ),
    path('image/dalle2/<int:pk>', Dalle2PromptBuyerRetrieveAPIView.as_view(),
         name='dalle2-prompt-buyer-detail'
         ),

]
