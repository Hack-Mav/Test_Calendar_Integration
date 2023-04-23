from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import View


class GoogleCalendarInitView(View):
    def get(self, request, *args, **kwargs):
        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect')),
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return HttpResponseRedirect(auth_url)


class GoogleCalendarRedirectView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'Authorization code not found.'}, status=400)

        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect')),
        )
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
        except HttpError as error:
            return JsonResponse({'error': str(error)}, status=400)

        try:
            service = build('calendar', 'v3', credentials=credentials)
            events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
            return JsonResponse({'events': events})
        except HttpError as error:
            return JsonResponse({'error': str(error)}, status=400)
