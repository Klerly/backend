from django.urls import path
from jarvis.apis.image.dalle2 import (
    Dalle2PromptSellerListCreateAPIView,
    Dalle2PromptSellerRetrieveUpdateDestroyAPIView,
    Dalle2PromptBuyerListAPIView,
    Dalle2PromptBuyerRetrieveAPIView,
    Dalle2PromptGeneratorAPIView
)
from jarvis.apis.language.gpt3 import (
    GPT3PromptSellerListCreateAPIView,
    GPT3PromptSellerRetrieveUpdateDestroyAPIView,
    GPT3PromptBuyerListAPIView,
    GPT3PromptBuyerRetrieveAPIView,
    GPT3PromptGeneratorAPIView
)

from jarvis.apis.output import (
    PromptOutputListAPIView,
    PromptOutputRetrieveAPIView
)


app_name = 'jarvis'
urlpatterns = [
    path('language/gpt3/seller', GPT3PromptSellerListCreateAPIView.as_view(),
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
    path('language/gpt3/generate/<int:pk>', GPT3PromptGeneratorAPIView.as_view(),
         name='gpt3-prompt-generator'
         ),
    path('image/dalle2/seller', Dalle2PromptSellerListCreateAPIView.as_view(),
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

    path('image/dalle2/generate/<int:pk>', Dalle2PromptGeneratorAPIView.as_view(),
         name='dalle2-prompt-generator'
         ),
    path('output', PromptOutputListAPIView.as_view(),
         name='prompt-output-list'
         ),
    path('output/<int:pk>', PromptOutputRetrieveAPIView.as_view(),
         name='prompt-output-detail'
         ),
]
