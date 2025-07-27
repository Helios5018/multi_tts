import requests
import json
from typing import Dict, Optional
from dotenv import dotenv_values

config: dict = dotenv_values(".env")


def t2t_new_api(
    system_prompt: str,
    user_prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    response_format: Dict[str, str] = {"type": "text"},
) -> str:
    """Call new api to invoke various supported t2t large language models

    Args:
        system_prompt (str): System prompt that defines AI's role and behavior
        user_prompt (str): User input content
        model (str, optional): Model name. Defaults to "gemini-2.5-flash".
        temperature (float, optional): Model temperature parameter. Defaults to 0.7.
        response_format (Dict[str, str], optional): Model response format. Defaults to {"type": "text"}.

    Returns:
        str: AI generated response content
    """
    new_api_token: str = config["NEW_API_TOKEN"]
    new_api_chat_url: str = config["NEW_API_CHAT_URL"]

    payload: str = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": response_format,
        }
    )

    headers: dict = {
        "Authorization": f"Bearer {new_api_token}",
        "Content-Type": "application/json",
    }

    try:
        response: requests.Response = requests.request(
            "POST", new_api_chat_url, headers=headers, data=payload
        )
    except requests.exceptions.RequestException as e:
        print(f"NewApi API error: {e}")
        raise e

    try:
        parsed_json: dict = json.loads(response.text)
        llm_result: Optional[str] = parsed_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"NewApi API error: {e}")
        raise e

    return llm_result


def t2t_hunyuan(
    system_prompt: str,
    user_prompt: str,
    model: str = "hunyuan-turbos-latest",
    temperature: float = 0.7,
    response_format: Dict[str, str] = {"type": "text"},
) -> str:
    """Tencent Hunyuan various supported t2t large language models

    Args:
        system_prompt (str): System prompt that defines AI's role and behavior
        user_prompt (str): User input content
        model (str, optional): Model name. Defaults to "hunyuan-turbos-latest".
        temperature (float, optional): Model temperature parameter. Defaults to 0.7.
        response_format (Dict[str, str], optional): Model response format. Defaults to {"type": "text"}.

    Returns:
        str: AI generated response content
    """

    hunyuan_token: str = config["HUNYUAN_TOKEN"]
    hunyuan_url: str = config["HUNYUAN_URL"]

    payload: str = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": response_format,
        }
    )

    headers: dict = {
        "Authorization": f"Bearer {hunyuan_token}",
        "Content-Type": "application/json",
    }

    try:
        response: requests.Response = requests.request(
            "POST", hunyuan_url, headers=headers, data=payload
        )
    except requests.exceptions.RequestException as e:
        print(f"Hunyuan API error: {e}")
        raise e

    try:
        parsed_json: dict = json.loads(response.text)
        llm_result: Optional[str] = parsed_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Hunyuan API error: {e}")
        raise e

    return llm_result


def t2t_qwen(
    system_prompt: str,
    user_prompt: str,
    model: str = "qwen3-235b-a22b",
    temperature: float = 0.7,
    response_format: Dict[str, str] = {"type": "text"},
) -> str:
    """Alibaba Qwen various supported t2t large language models

    Args:
        system_prompt (str): System prompt that defines AI's role and behavior
        user_prompt (str): User input content
        model (str, optional): Model name. Defaults to "qwen3-235b-a22b".
        temperature (float, optional): Model temperature parameter. Defaults to 0.7.
        response_format (Dict[str, str], optional): Model response format. Defaults to {"type": "text"}.

    Returns:
        str: AI generated response content
    """

    qwen_token: str = config["QWEN_TOKEN"]
    qwen_chat_url: str = config["QWEN_CHAT_URL"]

    payload: str = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": response_format,
            "enable_thinking": False,
        }
    )

    headers: dict = {
        "Authorization": f"Bearer {qwen_token}",
        "Content-Type": "application/json",
    }

    try:
        response: requests.Response = requests.request(
            "POST", qwen_chat_url, headers=headers, data=payload
        )
    except requests.exceptions.RequestException as e:
        print(f"Qwen API error: {e}")
        raise e

    try:
        parsed_json: dict = json.loads(response.text)
        llm_result: Optional[str] = parsed_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Qwen API error: {e}")
        raise e

    return llm_result


if __name__ == "__main__":
    # 测试api调用
    system_prompt = "你是一个聊天机器人"
    user_prompt = "你好呀~"

    # 测试NewApi
    response = t2t_new_api(system_prompt, user_prompt)
    print(f"NewApi回复: {response}")

    # 测试Hunyuan
    response = t2t_hunyuan(system_prompt, user_prompt)
    print(f"Hunyuan回复: {response}")

    # 测试Qwen
    response = t2t_qwen(system_prompt, user_prompt)
    print(f"Qwen回复: {response}")

    pass
