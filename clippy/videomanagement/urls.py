from .views import TemplatePromptView,TestView
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash = False)
router.register('templates/', TemplatePromptView)
router.register('test/', TestView)
urlpatterns = router.urls



