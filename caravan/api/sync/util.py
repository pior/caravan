import json
import logging

log = logging.getLogger(__name__)


# http://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-dg-limits.html
MAX_SWF_MESSAGE_SIZE = 32000


def swf_encode_data(data):
    """Encode data in JSON. Compress in zlib if too large."""
    encoded_data = json.dumps(data)

    if len(encoded_data) > MAX_SWF_MESSAGE_SIZE:
        encoded_data = encoded_data.encode('utf-8').encode('zlib_codec')

    if len(encoded_data) > MAX_SWF_MESSAGE_SIZE:
        log.warning('This message is probably too large for SWF:\n%s', data)

    return encoded_data


def swf_decode_data(data):
    """Decode data in JSON, possibly zlib compressed."""
    try:
        data = data.decode('zlib_codec')
    except:
        pass  # Fallback on bare json data
    return json.loads(data)
