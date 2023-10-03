from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mediaprobe import MediaProbe


def _ch_template(asset_no: str, ch_no: str, desc: str, layout: str | None=None) -> dict:
    return {
        "master_no": asset_no,
        "audio_channel": ch_no,
        "audio_desc": desc,
        "audio_desc2": layout
    }

def _51_split(asset_no: str, startindex: int=1) -> list[dict]:
    return [
        _ch_template(asset_no, str(startindex), "5.1", "L"),
        _ch_template(asset_no, str(startindex+1), "5.1", "R"),
        _ch_template(asset_no, str(startindex+2), "5.1", "C"),
        _ch_template(asset_no, str(startindex+3), "5.1", "LFE"),
        _ch_template(asset_no, str(startindex+4), "5.1", "Ls"),
        _ch_template(asset_no, str(startindex+5), "5.1", "Rs")
    ]

def _mono_split(asset_no: str, amount: int, startindex: int=1) -> list[dict]:
    ch_list = []
    increment = startindex
    for _ in range(amount):
        ch_list.append(_ch_template(asset_no, str(increment), "mono"))
        increment += 1
    return ch_list

def _predict_singlestream_51(layouts: list[str], startindex: int=0) -> bool:
    default_layout = ["L", "R", "C", "LFE", "Ls", "Rs"]
    if len(layouts) < startindex + 1:
        return False
    if layouts[startindex] != "L":
        return False
    if len(layouts[startindex:]) < len(default_layout):
        return False
    for index, ch_layout in enumerate(layouts[startindex:]):
        if ch_layout != layouts[index]:
            return False
    return True

def _get_layouts(probe: "MediaProbe") -> list[str]:
    layouts = []
    for track in probe.fulljson["tracks"]:
        if track["@type"] == "Audio":
            layout = track.get("ChannelLayout")
            if layout:
                layouts.append(layout)
    return layouts

def _layout_handler(asset_no: str, chs_per_stream: list[int], layouts: list[str]) -> list[dict]:
    ch_dicts = []
    assert len(layouts) == len(chs_per_stream)
    listindex = 1
    skip = 0
    for streamindex, channels in enumerate(chs_per_stream):
        if skip > 0:
            skip -= 1
            continue
        if channels == 6:
            ch_dicts.extend(_51_split(asset_no, listindex))
            listindex += 6
        elif channels == 2:
            ch_dicts.append(_ch_template(asset_no, str(listindex), "Stereo", "Lt"))
            ch_dicts.append(_ch_template(asset_no, str(listindex+1), "Stereo", "Rt"))
            listindex += 2
        elif channels == 1:
            if _predict_singlestream_51(layouts, streamindex):
                ch_dicts.extend(_51_split(asset_no, listindex))
                listindex += 6
                skip = 5
            else:
                ch_dicts.append(_ch_template(asset_no, str(listindex), "Mono", layouts[streamindex]))
                listindex += 1
        else:
            ch_dicts.extend(_mono_split(asset_no, channels, listindex))
            listindex += channels
    return ch_dicts

def _nolayout_handler(asset_no: str, probe: "MediaProbe") -> list[dict]:
    ch_dicts = []
    chs_per_stream = probe.chs_per_stream()
    index = 1
    for channels in chs_per_stream:
        ch_dicts.extend(_mono_split(asset_no, channels, index))
        index += channels
    return ch_dicts

def asset_audio_dict(asset_no: str, probe: "MediaProbe") -> list[dict]:
    total_chs = probe.audio()
    if total_chs < 1:
        return []
    
    layouts = _get_layouts(probe)
    if layouts:
        return _layout_handler(asset_no, probe.chs_per_stream(), layouts)
    else:
        return _nolayout_handler(asset_no, probe)