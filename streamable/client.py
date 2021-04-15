
import os.path
import requests
from streamable.errors import AuthError, UserNotFoundError, IncorrectPasswordError

BASE_URL = 'https://ajax.streamable.com'


class StreamableClient:

    def __init__(self):
        self.session = requests.Session()

    def login(self, username, password):
        body = {'username': username, 'password': password}

        with self.session.post(f'{BASE_URL}/check', json=body) as response:
            response.raise_for_status()

            json = response.json()
            if 'error' in json:
                error = json['error']
                message = json['message']

                if error == 'UserDoesNotExist':
                    raise UserNotFoundError(message)
                elif error == 'AuthError':
                    raise IncorrectPasswordError(message)
                else:
                    raise AuthError(message)

    def upload(self, file, *, title=None):
        size = os.path.getsize(file)

        upload_data = self.__request_upload(size)

        self.__upload_from_presigned_url(
            file, upload_data['upload_url'], upload_data['upload_fields'])

        original_name = os.path.basename(file)

        if title is None:
            title = os.path.splitext(original_name)[0]

        shortcode = upload_data['shortcode']

        self.__set_video_info(shortcode, original_name, size, title)

        transcoder_token = upload_data['transcoder_token']
        transcoder_url = upload_data['transcoder_url']
        transcoder_size = upload_data['transcoder_size']

        self.__transcode(shortcode, transcoder_url,
                         transcoder_size, transcoder_token)

        url = upload_data['video_url']
        file_url = upload_data['transcoder_url']

        return {'shortcode': shortcode, 'url': url, 'file_url': file_url,
                'size': transcoder_size, 'original_name': original_name}

    def __request_upload(self, size):
        payload = {'size': size,
                   'version': 'cc764e2a719399c2eb83ee6171fc50ba9fba8018'}

        with self.session.get(f'{BASE_URL}/shortcode', params=payload) as response:
            response.raise_for_status()

            json = response.json()

            return {'shortcode': json['shortcode'],
                    'upload_url': json['url'],
                    'upload_fields': json['fields'],
                    'transcoder_token': json['transcoder_options']['token'],
                    'transcoder_url': json['transcoder_options']['url'],
                    'transcoder_size': json['transcoder_options']['size'],
                    'video_url': json['video']['url']}

    def __upload_from_presigned_url(self, file, url, fields):
        with open(file, 'rb') as f:
            files = {'file': (file, f)}
            with self.session.post(url, data=fields, files=files) as response:
                response.raise_for_status()

    def __set_video_info(self, shortcode, original_name, size, title, upload_source='web'):
        body = {'original_name': original_name,
                'original_size': size,
                'title': title,
                'upload_source': upload_source}

        with self.session.put(f'{BASE_URL}/videos/{shortcode}', json=body) as response:
            response.raise_for_status()

    def __transcode(self, shortcode, url, size, token, upload_source='web'):
        body = {'shortcode': shortcode,
                'size': size,
                'token': token,
                'upload_source': upload_source,
                'url': url}

        with self.session.post(f'{BASE_URL}/transcode/{shortcode}', json=body) as response:
            response.raise_for_status()
