# coding: utf-8
import unittest
from django.test import RequestFactory, Client
from django.contrib.auth.models import User

from django_th.views import TriggerEditedTemplateView
from django_th.views import TriggerDeletedTemplateView, TriggerListView
from django_th.views_fbv import can_modify_trigger, trigger_on_off
from django_th.models import TriggerService
from django_th.tests.test_main import MainTest


class TriggerEditedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template = "triggers/edited_thanks_trigger.html"
        # Setup request and view.
        request = RequestFactory().get('/th/trigger/edit/thanks')
        view = TriggerEditedTemplateView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'triggers/edited_thanks_trigger.html')


class TriggerDeletedTemplateViewTestCase(unittest.TestCase):

    def test_get(self):
        template = "triggers/deleted_thanks_trigger.html"
        # Setup request and view.
        request = RequestFactory().get('/th/trigger/delete/thanks')
        view = TriggerDeletedTemplateView.as_view(template_name=template)
        # Run.
        response = view(request)
        # Check.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'triggers/deleted_thanks_trigger.html')


class TriggerListViewTestCase(unittest.TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        try:
            self.user = User.objects.get(username='john')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='john', email='john@doe.info', password='doe')

    def test_context_data(self):
        """
        TriggerListView.get_context_data() sets
        'triggers_enabled', 'triggers_disabled', 'services_activated'
        in context.
        """
        # Setup name.
        triggers_enabled = triggers_disabled = services_activated = 0
        queryset = TriggerService.objects.all()

        # Setup request and view.
        request = self.factory.get('/')
        request.user = self.user

        view = TriggerListView(
            template_name='home.html', object_list=queryset)
        view = setup_view(view, request)
        # Run.
        if request.user.is_authenticated():
            triggers_enabled = 3
            triggers_disabled = 1
            services_activated = 5

        context = view.get_context_data()
        context['nb_triggers'] = {
            'enabled': triggers_enabled, 'disabled': triggers_disabled}
        context['nb_services'] = services_activated

        # Check.
        self.assertEqual(context['nb_triggers']['enabled'], triggers_enabled)
        self.assertEqual(context['nb_triggers']['disabled'], triggers_disabled)
        self.assertEqual(context['nb_services'], services_activated)


class ViewFunction(MainTest):

    def test_can_modify_trigger(self):
        request = RequestFactory().get('/')
        self.assertFalse(can_modify_trigger(request, provider='ServiceRss',
                                            consumer='ServiceTwitter'))

    def test_logout(self):
        c = Client()
        c.logout()

    def test_trigger_on_off(self):
        s = self.create_triggerservice()
        c = Client()
        response = c.get('/')
        self.assertTrue(response.status_code, 200)

        response = trigger_on_off(request=c, trigger_id=s.id)
        self.assertTrue(response.status_code, 200)


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view
