from utils.t2t_llm import t2t
from utils.t2s_llm import t2s
from typing import List, Dict, Any
from pathlib import Path
import json
import re
from dotenv import dotenv_values
from time import sleep
from abc import ABC, abstractmethod

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
    segments = re.split(f"({pattern})", text.replace("\n", ""))

    # Process segments to combine text with their punctuation marks
    processed_segments = []

    for segment in segments:
        if segment.strip():  # Skip empty segments
            if re.search(r"\d|[\u4e00-\u9fff]|[a-zA-Z]", segment):
                processed_segments.append(segment)
            else:
                processed_segments[-1] += segment

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


class VoiceMatcher(ABC):
    """voice matcher father class"""

    def __init__(self):
        self.current_file = Path(__file__)
        self.prompt_file_path = (
            self.current_file.parent / "prompts" / "auto_voice_match.md"
        )
        self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            self.system_prompt = self.prompt_file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise e

    @abstractmethod
    def _load_voice_list(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def _process_voice_list(
        self, raw_voice_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def _create_voice_info(
        self, voice_match_item: Dict[str, Any], raw_voice_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        pass

    def _match_voice_by_llm(
        self, role_list: List[Dict[str, Any]], voice_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """use llm to match suitable rolevoice"""
        # create user prompt
        voice_list_str = json.dumps(voice_list, ensure_ascii=False)
        role_list_str = json.dumps(role_list, ensure_ascii=False)

        user_prompt = f"""
        # 角色列表: {role_list_str}
        # 音色库: {voice_list_str}
        """

        # use llm to match voice
        try:
            voice_match_list_str = t2t(
                system_prompt=self.system_prompt,
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

    def match_voices(self, role_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """match voices by role list
        Args:
            role_list (List[Dict[str, Any]]): role list with specific structure
        Returns:
            List[Dict[str, Any]]: voice match info list with specific structure
                                Each dictionary has the structure:
                                {
                                    "role_id": str,
                                    "name": str,
                                    "voice_info": Dict[str, Any]
                                }
        """
        # load voice list
        raw_voice_list = self._load_voice_list()

        # process voice list
        processed_voice_list = self._process_voice_list(raw_voice_list)

        # match voice by llm
        voice_match_list = self._match_voice_by_llm(role_list, processed_voice_list)

        # create final match info list
        voice_match_info_list = []
        for item in voice_match_list:
            voice_match_info = {
                "role_id": item["role_id"],
                "name": item["name"],
                "voice_info": self._create_voice_info(item, raw_voice_list),
            }
            voice_match_info_list.append(voice_match_info)

        return voice_match_info_list


class MinimaxVoiceMatcher(VoiceMatcher):
    """minimax voice matcher"""

    def _load_voice_list(self) -> List[Dict[str, Any]]:
        minimax_voice_list_file_path = (
            self.current_file.parent / "voice_list" / "minimax_voice_list.json"
        )
        try:
            minimax_voice_list_str = minimax_voice_list_file_path.read_text(
                encoding="utf-8"
            )
            minimax_voice_list = json.loads(minimax_voice_list_str)
            return minimax_voice_list
        except Exception as e:
            raise e

    def _process_voice_list(
        self, raw_voice_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        voice_list = []
        for item in raw_voice_list:
            voice_list.append(
                {
                    "voice_name": item["voice_name"],
                    "description": item["description"],
                }
            )
        return voice_list

    def _create_voice_info(
        self, voice_match_item: Dict[str, Any], raw_voice_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        voice_id = next(
            (
                voice["voice_id"]
                for voice in raw_voice_list
                if voice["voice_name"] == voice_match_item["voice_name"]
            ),
            None,
        )

        return {
            "voice_name": voice_match_item["voice_name"],
            "voice_source": "minimax",
            "voice": voice_id,
        }


class DoubaoVoiceMatcher(VoiceMatcher):
    """doubao voice matcher"""

    def _load_voice_list(self) -> List[Dict[str, Any]]:
        doubao_voice_list_file_path = (
            self.current_file.parent / "voice_list" / "doubao_voice_list.json"
        )
        try:
            doubao_voice_list_str = doubao_voice_list_file_path.read_text(
                encoding="utf-8"
            )
            doubao_voice_list = json.loads(doubao_voice_list_str)
            return doubao_voice_list
        except Exception as e:
            raise e

    def _process_voice_list(
        self, raw_voice_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        voice_list = []
        for item in raw_voice_list:
            voice_list.append(
                {
                    "voice_name": item["character_name"],
                    "category": item["category"],
                }
            )
        return voice_list

    def _create_voice_info(
        self, voice_match_item: Dict[str, Any], raw_voice_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        voice_type = next(
            (
                voice["voice_type"]
                for voice in raw_voice_list
                if voice["character_name"] == voice_match_item["voice_name"]
            ),
            None,
        )

        return {
            "voice_name": voice_match_item["voice_name"],
            "voice_source": "doubao",
            "voice": voice_type,
        }


def combine_data(
    segments: List[Dict[str, Any]],
    speaker_list: List[Dict[str, Any]],
    voice_match_info_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """combine segments and speaker list and voice match list

    Args:
        segments (List[Dict[str, Any]]): segment list with specific structure
        speaker_list (List[Dict[str, Any]]): speaker list with specific structure
        voice_match_info_list (List[Dict[str, Any]]): voice match list with specific structure

    Returns:
        List[Dict[str, Any]]: combined data list with specific structure
                            Each dictionary has the structure:
                            {
                                "segment_id": int,
                                "content": str,
                                "speaker": str,
                                "voice_info": Dict[str, Any]
                            }
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
        # find voice from voice match list
        voice_info = next(
            (
                item["voice_info"]
                for item in voice_match_info_list
                if item["name"] == speaker
            ),
            None,
        )
        # add speaker and voice to segment
        segment["speaker"] = speaker
        segment["voice_info"] = voice_info
        # add segment to combined data list
        combined_data.append(segment)

    return combined_data


def integrate_same_speaker(combined_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """integrate same speaker sentence

    Args:
        combined_data (List[Dict[str, Any]]): combined data list with specific structure

    Returns:
        List[Dict[str, Any]]: integrated data list with specific structure
                            Each dictionary has the structure:
                            {
                                "segment_id": int,
                                "content": str,
                                "speaker": str,
                                "voice_info": Dict[str, Any]
                            }
    """
    # integrate same speaker sentence
    integrated_data = []
    last_segment_speaker = ""
    last_voice_info = {}
    combile_content = ""

    for item in combined_data:
        if item["speaker"] == last_segment_speaker:
            combile_content += item["content"]
        else:
            if combile_content:
                new_item = {
                    "segment_id": len(integrated_data),
                    "speaker": last_segment_speaker,
                    "content": combile_content.replace("\n", ""),
                    "voice_info": last_voice_info,
                }
                integrated_data.append(new_item)
            combile_content = item["content"]

        last_segment_speaker = item["speaker"]
        last_voice_info = item["voice_info"]

    # add last item
    if combile_content:
        new_item = {
            "segment_id": len(integrated_data),
            "speaker": last_segment_speaker,
            "content": combile_content,
            "voice_info": last_voice_info,
        }
        integrated_data.append(new_item)

    return integrated_data


def tts_generation(integrated_data: List[Dict[str, Any]], floder_name="output"):
    """tts generation

    Args:
        integrated_data (List[Dict[str, Any]]): integrated data list with specific structure
        floder_name (str, optional): output floder name. Defaults to "output".
    """
    # create output dir
    output_dir = Path(f"tests/output_tts/{floder_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # generate tts
    for item in integrated_data:
        # tts bytes generation
        try:
            audio_bytes = t2s(
                text=item["content"],
                llm=item["voice_info"]["voice_source"],
                voice=item["voice_info"]["voice"],
            )
        except Exception as e:
            raise e
        sleep(2)
        # save audio file
        try:
            with open(output_dir / f"{item['segment_id']}.mp3", "wb") as f:
                f.write(audio_bytes)
        except Exception as e:
            raise e


def multi_tts_workflow(
    text: str, floder_name: str = "output", tts_llm: str = "minimax"
):
    """multi tts workflow, generate tts audio file from input novel text, which output to floder_name

    Args:
        text (str): input text
        floder_name (str, optional): output floder name. Defaults to "output".
        tts_llm (str, optional): tts llm name. Defaults to "minimax".options: "minimax", "doubao"

    """
    # step1: identify role
    role_list = identify_role(text)
    # step2: auto voice match
    if tts_llm == "minimax":
        voice_match_info_list = MinimaxVoiceMatcher().match_voices(role_list)
    elif tts_llm == "doubao":
        voice_match_info_list = DoubaoVoiceMatcher().match_voices(role_list)
    else:
        raise ValueError(f"tts_llm {tts_llm} not supported")
    # step3: segment novel text
    segments = novel_segmentation(text)
    # step4: identify speaker
    speaker_list = identify_speaker(segments, role_list)
    # step5: combine data
    combined_data = combine_data(segments, speaker_list, voice_match_info_list)
    # step6: integrate same speaker
    integrated_data = integrate_same_speaker(combined_data)
    # step7: tts generation
    tts_generation(integrated_data, floder_name=floder_name)


if __name__ == "__main__":
    # 读取小说文本
    with open(
        "tests/test_novel/第三人称/三体第一部第四集.txt", "r", encoding="utf-8"
    ) as f:
        text_novel = f.read()

    # 测试角色识别功能
    print("\n=== 角色识别结果 ===")
    role_list = identify_role(text_novel)
    print(role_list)

    # 测试音色匹配功能
    print("\n=== 音色匹配结果 ===")
    voice_match_info_list = DoubaoVoiceMatcher().match_voices(role_list)
    print(voice_match_info_list)

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
    # combined_data = combine_data(segments, speaker_list, voice_match_info_list)
    # print(combined_data)

    # # 测试数据整合功能
    # print("\n=== 数据整合结果 ===")
    # integrated_data = integrate_same_speaker(combined_data)
    # print(integrated_data)

    # # 测试TTS生成功能
    # print("\n=== TTS生成结果 ===")
    # tts_generation(integrated_data, floder_name="1911新中华")
