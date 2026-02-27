import logging
import time

import requests

from . import exceptions


logger = logging.getLogger(__name__)

#: Maximum number of retries for rate-limited (429) responses.
MAX_RETRIES = 5

#: Initial backoff delay in seconds (doubles with each retry).
INITIAL_BACKOFF = 1


class Session(requests.Session):
    """An HTTP session for making API requests.

    This session sets the content type to JSON and injects the API token.
    """

    def __init__(self, token):
        super().__init__()
        self.headers = {
            'content-type': 'application/json',
            'x-access-token': token,
        }

    def request(self, *args, **kwargs):
        # ensure we reraise exceptions as our own
        backoff = INITIAL_BACKOFF
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = super().request(*args, **kwargs)
                response.raise_for_status()
                return Response(response)
            except requests.HTTPError as e:
                if response.status_code == 429 and attempt < MAX_RETRIES:
                    retry_after = response.headers.get('Retry-After')
                    delay = int(retry_after) if retry_after else backoff
                    logger.warning(
                        'Rate limited (429). Retrying in %s seconds (attempt %d/%d)',
                        delay, attempt + 1, MAX_RETRIES,
                    )
                    time.sleep(delay)
                    backoff *= 2
                    continue
                logger.exception('received a bad response')
                raise exceptions.BadResponse(response) from e
            except requests.RequestException as e:
                logger.exception('could not receive a response')
                raise exceptions.NoResponse(e.request) from e


class Response:
    def __init__(self, response):
        self._resp = response

    # pretend we're a requests.Response
    def __getattr__(self, attr):
        return getattr(self._resp, attr)

    @property
    def data(self):
        try:
            return self.json()['response']
        except ValueError as e:
            raise exceptions.InvalidJsonError(self._resp) from e
        except KeyError as e:
            try:
                return self.json()['payload']
            except KeyError:
                raise exceptions.MissingResponseError(self._resp) from e

    @property
    def errors(self):
        try:
            return self.json()['meta']['errors']
        except ValueError as e:
            raise exceptions.InvalidJsonError(self._resp) from e
        except KeyError as e:
            raise exceptions.MissingMetaError(self._resp) from e
