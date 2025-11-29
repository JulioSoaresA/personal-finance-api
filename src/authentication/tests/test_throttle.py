from django.test import override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


User = get_user_model()


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {"anon": "2/min", "user": "3/min"},
    }
)
class ThrottleTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.factory = APIRequestFactory()
        self.anon_ip = "127.0.0.1"
        self.user = User.objects.create_user(
            username="throttleuser", password="password"
        )
        self.login_url = "/api/auth/login/"
        self.profile_url = "/api/users/profile/"

    def test_anon_throttle_blocks_after_limit(self):
        throttle = AnonRateThrottle()
        throttle.rate = "2/min"
        throttle.num_requests, throttle.duration = throttle.parse_rate(throttle.rate)

        django_req = self.factory.get("/")
        django_req.META["REMOTE_ADDR"] = self.anon_ip
        request = Request(django_req)

        view = object()
        key = throttle.get_cache_key(request, view=view)
        self.assertIsNotNone(key)

        self.assertTrue(throttle.allow_request(request, view=view))
        history = throttle.cache.get(key)
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 1)

        self.assertTrue(throttle.allow_request(request, view=view))
        history = throttle.cache.get(key)
        self.assertEqual(len(history), 2)

        self.assertFalse(throttle.allow_request(request, view=view))

    def test_user_throttle_blocks_after_limit(self):
        throttle = UserRateThrottle()
        throttle.rate = "3/min"
        throttle.num_requests, throttle.duration = throttle.parse_rate(throttle.rate)

        django_req = self.factory.get("/")
        django_req.user = self.user
        request = Request(django_req)

        view = object()
        key = throttle.get_cache_key(request, view=view)
        self.assertIsNotNone(key)

        self.assertTrue(throttle.allow_request(request, view=view))
        history = throttle.cache.get(key)
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 1)

        self.assertTrue(throttle.allow_request(request, view=view))
        history = throttle.cache.get(key)
        self.assertEqual(len(history), 2)

        self.assertTrue(throttle.allow_request(request, view=view))
        history = throttle.cache.get(key)
        self.assertEqual(len(history), 3)

        self.assertFalse(throttle.allow_request(request, view=view))
