from utils.t2t_llm import t2t
from utils.t2s_llm import t2s_minimax
from typing import List, Dict, Any
from pathlib import Path
import json
import re
from dotenv import dotenv_values

config: dict = dotenv_values(".env")


def identify_role(text: str) -> List[Dict[str, Any]]:
    """identify role from text

    Args:
        text (str): input text

    Returns:
        List[Dict[str, Any]]: role list with specific structure
                            Each dictionary has the structure:
                            {
                                "role_id": int,
                                "name": str,
                                "description": str
                            }
    """
    # get current file path
    current_file = Path(__file__)
    # create prompt file path
    prompt_file_path = current_file.parent / "prompts" / "identify_role.md"
    # read prompt file content
    try:
        system_prompt = prompt_file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise e

    # use llm to identify role
    try:
        role_list_str = t2t(
            system_prompt=system_prompt,
            user_prompt=text,
            llm="qwen",
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise e

    # check output format
    try:
        role_list = json.loads(role_list_str)
    except Exception as e:
        raise e

    return role_list


def novel_segmentation(text: str) -> List[Dict[str, Any]]:
    """Segment novel text into smaller chunks based on punctuation marks.

    Args:
        text (str): The input novel text to be segmented.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing segmented text chunks.
                             Each dictionary has the structure:
                             {
                                 "segment_id": int,
                                 "content": str
                             }
    """
    # Get segmentation punctuation from config
    try:
        punctuation_marks = config["SEGMENTATION_PUNCTUATION"]
    except KeyError:
        raise KeyError("SEGMENTATION_PUNCTUATION not found in .env configuration")

    # Create regex pattern for splitting text based on punctuation marks
    # Escape special regex characters in punctuation marks
    escaped_punctuation = re.escape(punctuation_marks)
    # Create pattern that matches any of the punctuation marks
    pattern = f"[{escaped_punctuation}]"

    # Split text using the punctuation pattern
    # Use re.split with capturing groups to keep the punctuation marks
    segments = re.split(f"({pattern})", text)

    # Process segments to combine text with their punctuation marks
    processed_segments = []
    current_segment = ""

    for i, segment in enumerate(segments):
        if segment.strip():  # Skip empty segments
            current_segment += segment
            # skip single punctuation mark
            if len(current_segment) <= 6:
                continue
            # If this segment is a punctuation mark or we're at the end
            if re.match(pattern, segment) or i == len(segments) - 1:
                if current_segment.strip():  # Only add non-empty segments
                    processed_segments.append(current_segment.strip())
                    current_segment = ""

    # Create final result list with segment information
    result = []
    for idx, segment_content in enumerate(processed_segments):
        if segment_content:  # Ensure segment is not empty
            segment_info = {"segment_id": idx, "content": segment_content}
            result.append(segment_info)

    return result


def identify_speaker(
    segments: List[Dict[str, Any]], role_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """identify speaker from segments and role list

    Args:
        segments (List[Dict[str, Any]]): segment list with specific structure
        role_list (List[Dict[str, Any]]): role list with specific structure

    Returns:
        List[Dict[str, Any]]: speaker list with specific structure
                            Each dictionary has the structure:
                            {
                                "segment_id": int,
                                "speaker": str
                            }

    """
    # get current file path
    current_file = Path(__file__)
    # create prompt file path
    prompt_file_path = current_file.parent / "prompts" / "identify_speaker.md"
    # read prompt file content
    try:
        system_prompt = prompt_file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise e

    # convert role list and segments to json string
    role_list_str = json.dumps(role_list, ensure_ascii=False)
    segments_str = json.dumps(segments, ensure_ascii=False)

    # create user prompt
    user_prompt = f"""
    # 角色列表: {role_list_str}
    # 片段列表: {segments_str}
    """

    # use llm to identify speaker
    try:
        speaker_list_str = t2t(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm="new_api",
            model="gemini-2.5-pro",
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise e

    # check output format
    try:
        speaker_list = json.loads(speaker_list_str)
    except Exception as e:
        raise e

    return speaker_list


def combine_data(
    segments: List[Dict[str, Any]], speaker_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """combine segments and speaker list

    Args:
        segments (List[Dict[str, Any]]): segment list with specific structure
        speaker_list (List[Dict[str, Any]]): speaker list with specific structure

    Returns:
        List[Dict[str, Any]]: combined data list with specific structure
    """
    # create combined data list
    combined_data = []
    for segment in segments:
        # find speaker from speaker list
        speaker = next(
            (
                item["speaker"]
                for item in speaker_list
                if item["segment_id"] == segment["segment_id"]
            ),
            None,
        )
        # add speaker to segment
        segment["speaker"] = speaker
        # add segment to combined data list
        combined_data.append(segment)
    return combined_data


def auto_voice_match_minimax(
    role_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """auto voice match by minimax voice list

    Args:
        role_list (List[Dict[str, Any]]): role list with specific structure

    Returns:
        List[Dict[str, Any]]: voice match list with specific structure
                            Each dictionary has the structure:
                            {
                                "role_id": int,
                                "name": str,
                                "voice_name": str,
                            }
    """
    # get current file path
    current_file = Path(__file__)
    # create prompt file path
    prompt_file_path = current_file.parent / "prompts" / "auto_voice_match.md"
    # read prompt file content
    try:
        system_prompt = prompt_file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise e

    # read minimax voice list
    minimax_voice_list_file_path = (
        current_file.parent / "voice_list" / "minimax_voice_list.json"
    )
    try:
        minimax_voice_list_str = minimax_voice_list_file_path.read_text(encoding="utf-8")
        minimax_voice_list = json.loads(minimax_voice_list_str)
    except Exception as e:
        raise e

    # create voice list
    voice_list = []
    for item in minimax_voice_list:
        voice_list.append(
            {
                "voice_name": item["voice_name"],
                "description": item["description"],
            }
        )

    # create user prompt
    voice_list_str = json.dumps(voice_list, ensure_ascii=False)
    role_list_str = json.dumps(role_list, ensure_ascii=False)

    user_prompt = f"""
    # 角色列表: {role_list_str}
    # 音色库: {voice_list_str}
    """

    # auto match voice by llm
    try:
        voice_match_list_str = t2t(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm="new_api",
            model="gemini-2.5-pro",
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise e

    # check output format
    try:
        voice_match_list = json.loads(voice_match_list_str)
    except Exception as e:
        raise e

    return voice_match_list


def tts_generation(segments: List[Dict[str, Any]]):
    pass


def multi_tts_workflow(text: str):
    pass


if __name__ == "__main__":
    # 读取小说文本
    with open("tests/test_novel/血玫瑰.txt", "r", encoding="utf-8") as f:
        text_novel = f.read()

    # 测试角色识别功能
    print("=== 角色识别结果 ===")
    role_list = identify_role(text_novel)
    print(role_list)

    # # 测试小说切分功能
    # print("\n=== 小说切分结果 ===")
    # segments = novel_segmentation(text_novel)
    # print(segments)

    # # 测试说话人识别功能
    # print("\n=== 说话人识别结果 ===")
    # speaker_list = identify_speaker(segments, role_list)
    # print(speaker_list)

    # # 测试数据合并功能
    # print("\n=== 数据合并结果 ===")
    # combined_data = combine_data(segments, speaker_list)
    # print(combined_data)

    # 测试音色匹配功能
    print("\n=== 音色匹配结果 ===")
    voice_match_list = auto_voice_match_minimax(role_list)
    print(voice_match_list)
