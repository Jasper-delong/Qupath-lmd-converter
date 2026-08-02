"""Streamlit web app for the GeoJSON -> LMD XML pipeline."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import pandas as pd
import streamlit as st

from lmd_converter.core import (
    PLATE_DIMENSIONS,
    assign_round_robin,
    convert_to_xml,
    extract_from_text,
    generate_wells,
)

st.set_page_config(page_title="GeoJSON to LMD Converter", layout="wide")

st.title("QuPath GeoJSON 到 Leica LMD XML 转换")

# ---------------------------------------------------------------------------
# Step 1: upload and parse the GeoJSON
# ---------------------------------------------------------------------------
uploaded = st.file_uploader("1. 上传 QuPath 导出的 GeoJSON 文件", type=["geojson", "json"])

extracted = None
if uploaded is not None:
    try:
        raw = uploaded.getvalue().decode("utf-8")
        extracted = extract_from_text(raw)
    except Exception as exc:  # noqa: BLE001
        st.error(f"文件解析失败：{exc}")
        extracted = None

if extracted is not None:
    st.session_state["extracted"] = extracted
    st.session_state["source_name"] = uploaded.name

source = st.session_state.get("extracted")
if source is None:
    st.info("请先上传 GeoJSON 文件。")
    st.stop()

st.subheader("解析结果")
cal_df = pd.DataFrame(
    [
        {
            "校准点": p["name"],
            "X": p["coordinates"][0],
            "Y": p["coordinates"][1],
        }
        for p in source["calibration_points"]
    ]
)
shape_df = pd.DataFrame(
    [
        {
            "名称": s["name"],
            "分类": s["classification"],
            "顶点数": len(s["coordinates"]),
        }
        for s in source["shapes"]
    ]
)
left, right = st.columns(2)
with left:
    st.write(f"校准点：{len(source['calibration_points'])} 个")
    st.dataframe(cal_df, use_container_width=True, hide_index=True)
with right:
    st.write(f"切割区域：{len(source['shapes'])} 个")
    st.dataframe(shape_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Step 2: choose collection device
# ---------------------------------------------------------------------------
st.divider()
st.subheader("2. 选择收集装置")

device = st.selectbox(
    "装置类型",
    options=list(PLATE_DIMENSIONS),
    format_func=lambda d: f"{d} - {PLATE_DIMENSIONS[d]['label']}",
    help="4：四孔位 A/B/C/D；96：A1-H12；384：A1-P24",
)
if device != "4":
    margin = st.slider("跳过外圈行列数 (margin)", 0, 3, 0)
else:
    margin = 0

wells = generate_wells(device, margin)
st.write(f"可用孔位 {len(wells)} 个：", ", ".join(wells[:16]) + ("..." if len(wells) > 16 else ""))

# ---------------------------------------------------------------------------
# Step 3: shape-to-well matching (editable table)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("3. 切割区域与孔位匹配")

shape_names = [s["name"] for s in source["shapes"]]
defaults = assign_round_robin(shape_names, wells)
match_df = pd.DataFrame(defaults)

edited = st.data_editor(
    match_df,
    num_rows="fixed",
    use_container_width=True,
    hide_index=True,
    column_config={
        "shape_name": st.column_config.TextColumn("切割区域", disabled=True),
        "well": st.column_config.SelectboxColumn("孔位", options=wells),
    },
)

assignments = [
    {"shape_name": row["shape_name"], "well": row["well"]}
    for _, row in edited.iterrows()
]

# ---------------------------------------------------------------------------
# Step 4: generate XML + preview
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4. 生成 LMD XML")

if st.button("生成 XML 与预览图", type="primary"):
    match = {"device": device, "assignments": assignments}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        xml_path = tmp_path / "cutting.xml"
        preview_path = tmp_path / "preview.png"
        try:
            summary = convert_to_xml(
                source,
                match,
                xml_path,
                preview_path=preview_path,
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"转换失败：{exc}")
            st.stop()

        st.success(
            f"转换完成：{summary['shapes_placed']}/{summary['shapes_total']} "
            "个区域已写入 XML"
        )
        if summary["shapes_skipped"]:
            st.warning(f"未匹配的区域：{', '.join(summary['shapes_skipped'])}")

        if preview_path.exists():
            st.image(str(preview_path), caption="最终切割预览（红色十字为校准点）", use_container_width=True)

        base_name = (st.session_state.get("source_name") or "cutting").rsplit(".", 1)[0]
        st.download_button(
            "下载 LMD XML",
            data=xml_path.read_bytes(),
            file_name=f"{base_name}_lmd.xml",
            mime="application/xml",
        )
        st.download_button(
            "下载预览图",
            data=preview_path.read_bytes(),
            file_name=f"{base_name}_preview.png",
            mime="image/png",
        )
        st.download_button(
            "下载孔位匹配表",
            data=json.dumps(match, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"{base_name}_match.json",
            mime="application/json",
        )
