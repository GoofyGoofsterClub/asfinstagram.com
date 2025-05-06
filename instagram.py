import http.client
import json
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import urlencode

class InstagramEndpoints:
    GRAPHQL = 'https://www.instagram.com/api/graphq'

class Instagram(object):

    def handle_post(self, post_id):
        gq = self.get_graphql(post_id)
        gq = gq['data']
        if 'xdt_shortcode_media' not in gq:
            return False

        match gq['xdt_shortcode_media']['__typename']:
            case "XDTGraphVideo": # Reels/Videos
                return [gq['xdt_shortcode_media']['video_url'] if gq['xdt_shortcode_media']['video_url'] else gq['xdt_shortcode_media']['display_url'], 'video/mp4']
            case "XDTGraphImage": # Images
                return [gq['xdt_shortcode_media']['display_url'], 'image/jpeg']
            case _:
                raise ValueError(f"Unknown shortcode media type ({gq['xdt_shortcode_media']['__typename']})")
        return False

    def get_graphql(self, post_id: str) -> dict:
        # Import and use the encode function from earlier
        encoded_data = self.encode_graphql_request_data(post_id)

        # Define connection
        conn = http.client.HTTPSConnection("www.instagram.com")

        # Define headers
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-Friendly-Name": "PolarisPostActionLoadPostQueryQuery",
            "X-CSRFToken": "RVDUooU5MYsBbS1CNN3CzVAuEP8oHB52",
            "X-IG-App-ID": "1217981644879628",
            "X-FB-LSD": "AVqbxe3J_YA",
            "X-ASBD-ID": "129477",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36"
            )
        }

        # Send POST request
        conn.request("POST", "/api/graphql", body=encoded_data, headers=headers)

        # Get response
        response = conn.getresponse()
        response_data = response.read().decode("utf-8")

        # Close connection
        conn.close()

        # Parse and return JSON
        return json.loads(response_data)


    def encode_graphql_request_data(self, shortcode: str) -> str:
        request_data = {
            "av": "0",
            "__d": "www",
            "__user": "0",
            "__a": "1",
            "__req": "3",
            "__hs": "19624.HYP:instagram_web_pkg.2.1..0.0",
            "dpr": "3",
            "__ccg": "UNKNOWN",
            "__rev": "1008824440",
            "__s": "xf44ne:zhh75g:xr51e7",
            "__hsi": "7282217488877343271",
            "__dyn": (
                "7xeUmwlEnwn8K2WnFw9-2i5U4e0yoW3q32360CEbo1nEhw2nVE4W0om78b87C0yE5ufz81s8hwGwQwoEcE7O2l0Fwqo31w9a9x-0z8-U2zxe2GewGwso88cobEaU2eUlwhEe87q7-0iK2S3qazo7u1xwIw8O321LwTwKG1pg661pwr86C1mwraCg"
            ),
            "__csr": (
                "gZ3yFmJkillQvV6ybimnG8AmhqujGbLADgjyEOWz49z9XDlAXBJpC7Wy-vQTSvUGWGh5u8KibG44dBiigrgjDxGjU0150Q0848azk48N09C02IR0go4SaR70r8owyg9pU0V23hwiA0LQczA48S0f-x-27o05NG0fkw"
            ),
            "__comet_req": "7",
            "lsd": "AVqbxe3J_YA",
            "jazoest": "2957",
            "__spin_r": "1008824440",
            "__spin_b": "trunk",
            "__spin_t": "1695523385",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "PolarisPostActionLoadPostQueryQuery",
            "variables": str({
                "shortcode": shortcode,
                "fetch_comment_count": "null",
                "fetch_related_profile_media_count": "null",
                "parent_comment_count": "null",
                "child_comment_count": "null",
                "fetch_like_count": "null",
                "fetch_tagged_user_count": "null",
                "fetch_preview_comment_count": "null",
                "has_threaded_comments": "false",
                "hoisted_comment_id": "null",
                "hoisted_reply_id": "null",
            }).replace("'", '"'),
            "server_timestamps": "true",
            "doc_id": "10015901848480474"
        }

        encoded = "&".join(
            f"{urllib.parse.quote_plus(str(k))}={urllib.parse.quote_plus(str(v))}"
            for k, v in request_data.items()
        )
        print(encoded)
        return encoded
    
    def get_http_video_response(self, url: str):
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            raise HTTPException(status_code=400, detail="Invalid URL scheme")

        conn_cls = http.client.HTTPSConnection if parsed_url.scheme == "https" else http.client.HTTPConnection
        conn = conn_cls(parsed_url.netloc)

        path = parsed_url.path or "/"
        if parsed_url.query:
            path += f"?{parsed_url.query}"

        conn.request("GET", path)
        res = conn.getresponse()
        if res.status != 200:
            conn.close()
            raise HTTPException(status_code=404, detail="Video not found")
        return conn, res

    def stream_chunks(self, response):
        def generator():
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                yield chunk
            response.close()
        return generator