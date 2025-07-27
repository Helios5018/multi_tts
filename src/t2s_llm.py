import requests
import json
import uuid
import base64
from dotenv import dotenv_values

config: dict = dotenv_values(".env")


def t2s_minimax(
    text: str,
    model: str = "speech-02-hd",
    voice_id: str = "male-qn-qingse",
    speed: float = 1,
    vol: float = 1,
    pitch: float = 0,
    emotion: str = "calm",
) -> bytes:
    """text to sound by minimax api

    Args:
        text (str): input text
        model (str, optional): speed model name. Defaults to "speech-02-hd".
        voice_id (str, optional): voice id. Defaults to "male-qn-qingse".
        speed (float, optional): speed. Defaults to 1.0.
        vol (float, optional): volume. Defaults to 1.0.
        pitch (float, optional): pitch. Defaults to 0.0.
        emotion (str, optional): emotion. Defaults to "happy".

    Returns:
        bytes: audio bytes
    """
    base_url: str = config["MINIMAXI_API_URL"]
    group_id: str = config["MINIMAXI_GROUP_ID"]
    api_key: str = config["MINIMAXI_API_KEY"]

    url: str = f"{base_url}/t2a_v2?GroupId={group_id}"

    payload: str = json.dumps(
        {
            "model": model,
            "text": text,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
                "emotion": emotion,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            },
        }
    )

    headers: dict = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response: requests.Response = requests.request(
            "POST", url, stream=True, headers=headers, data=payload
        )
    except requests.exceptions.RequestException as e:
        print(f"Minimax API error: {e}")
        raise e

    try:
        parsed_json: dict = json.loads(response.text)
        audio_value: bytes = bytes.fromhex(parsed_json["data"]["audio"])
    except Exception as e:
        print(f"Minimax API error: {e}")
        raise e

    return audio_value


def t2s_doubao(
    text: str,
    voice_type: str = "zh_female_sophie_conversation_wvae_bigtts",
    speed_ratio: float = 1.0,
) -> bytes:
    """text to sound by doubao tts api

    Args:
        text (str): input text
        voice_type (str, optional): voice type. Defaults to "zh_female_sophie_conversation_wvae_bigtts".
        speed_ratio (float, optional): speed ratio to control sound speed. Defaults to 1.0.

    Returns:
        bytes: audio bytes
    """
    url: str = config["DOUBAO_API_URL"]
    api_key: str = config["DOUBAO_API_KEY"]
    appid: str = config["DOUBAO_APPID"]

    payload: str = json.dumps(
        {
            "app": {
                "appid": appid,
                "token": "api_key",
                "cluster": "volcano_tts",
            },
            "user": {
                "uid": "uid",
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": "mp3",
                "speed_ratio": speed_ratio,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "operation": "query",
            },
        }
    )

    headers: dict = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{api_key}",
    }

    try:
        response: requests.Response = requests.request(
            "POST", url, headers=headers, data=payload
        )
    except requests.exceptions.RequestException as e:
        print(f"Doubao API error, call fail: {e}")
        raise e

    try:
        parsed_json: dict = json.loads(response.text)
        audio_value: bytes = base64.b64decode(parsed_json["data"])
    except Exception as e:
        print(f"Doubao API error, parse fail: {e}")
        raise e

    return audio_value


if __name__ == "__main__":
    audio_value = t2s_minimax("你好，我是你的语音助手123，很高兴见到你")
    with open("minimax_test.mp3", "wb") as f:
        f.write(audio_value)

    # audio_value = t2s_doubao("你好，我是你的语音助手呵呵，很高兴见到你")
    # with open("doubao_test.mp3", "wb") as f:
    #     f.write(audio_value)
