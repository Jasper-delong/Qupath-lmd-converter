# QuPath GeoJSON to Leica LMD XML Converter

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app/)  
**Open live app:** [qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app](https://qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app/)  

[:cn: 中文版](#qupath-geojson-到-leica-lmd-xml-转换工具)  

Convert QuPath GeoJSON annotations into cutting data for Leica LMD6/7 laser microdissection, with support for 4-well, 96-well and 384-well collection devices.

## Features

- Extract calibration points and cutting shapes from a QuPath GeoJSON export
- Choose a collection device: 4-well (A/B/C/D), 96-well (A1-H12) or 384-well (A1-P24, with configurable margin)
- Assign shapes to wells automatically (round-robin) or manually
- Generate LMD XML with Y-axis flip and `CapID` well metadata (shape coordinates are not translated)
- Local web app (Streamlit) with an editable match table, preview image and downloads
- CLI and web versions share the same core logic

## Pipeline

```text
src/lmd_converter/
  core.py                  shared core logic
  extract_geojson.py       extract calibration points and shapes  -> pipeline/extracted.json
  device_config.py         configure 4/96/384 device              -> pipeline/device.json
  match_shapes.py          match shapes to wells                  -> pipeline/match.json
  convert_to_xml.py        generate LMD XML + preview             -> output/cutting.xml
```

The root directory keeps only two entry points: `app.py` (Streamlit web app) and `run_pipeline.py` (one-command CLI). The four step modules live under `src/lmd_converter/` and can also be run individually with `python -m lmd_converter.<module>`. Intermediate files are JSON, so steps can be run separately and debugged easily.

## Installation

Python 3.9-3.12 is recommended (py-lmd requirement):

```powershell
conda activate bioinfo
python -m pip install -r requirements.txt
```

Dependencies are pinned in `requirements.txt`: py-lmd 1.6.0 (Apache-2.0) and streamlit 1.60.0.

## Usage

### Web app (Streamlit)

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501 in a browser. Upload a GeoJSON file, choose the device, edit shape-to-well assignments in the table, then generate and download the XML, preview image and match table.

On Windows you can also double-click `start.bat` to launch the web app locally.

### One-command CLI

```powershell
python run_pipeline.py "image_01.geojson" --device 4
```

`--device` accepts `4` (4-well A/B/C/D), `96` (A1-H12) or `384` (A1-P24). Add `--interactive` to confirm the device and each shape-to-well assignment step by step.

### Step by step

```powershell
$env:PYTHONPATH = "src"
python -m lmd_converter.extract_geojson "image_01.geojson"
python -m lmd_converter.device_config --device 96 --margin 0
python -m lmd_converter.match_shapes --interactive
python -m lmd_converter.convert_to_xml
```

## Deployment (shareable link)

The web app can be deployed for free on Streamlit Community Cloud:

1. Push this repository to a public GitHub repository
2. Go to https://share.streamlit.io and sign in with GitHub
3. Choose the repository, set the main file to `app.py`, and deploy

The result is a public URL such as `https://username-reponame.streamlit.app`.

## Acknowledgments

The workflow is inspired by [Qupath_to_LMD](https://github.com/CosciaLab/Qupath_to_LMD) (CosciaLab), and the XML serialization is based on [py-lmd](https://github.com/MannLabs/py-lmd) (MannLabs, Apache-2.0). All code in this repository is written independently and does not contain source code from Qupath_to_LMD.

- Nimo, J. et al. (2025). OpenDVP: An experimental and computational framework for community-empowered deep visual proteomics. bioRxiv. https://doi.org/10.1101/2025.07.13.662099
- Schmacke, N. A. et al. (2023). SPARCS, a platform for genome-scale CRISPR screening for spatial cellular phenotypes. bioRxiv. https://doi.org/10.1101/2023.06.01.542416

## License

Apache-2.0. See `LICENSE`. py-lmd is licensed under Apache-2.0; see `NOTICE.txt`.

---

# QuPath GeoJSON 到 Leica LMD XML 转换工具

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app/)  
**打开在线工具：** [qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app](https://qupath-lmd-converter-ggqnl6ufzzwnevv9pexv9e.streamlit.app/)  


[English](#qupath-geojson-to-leica-lmd-xml-converter)  

将 QuPath 导出的 GeoJSON 标注转化为 Leica LMD6/7 激光微切切割数据，支持 4 孔位、96 孔、384 孔三种收集装置。

## 功能

- 从 QuPath 导出的 GeoJSON 中提取校准点与切割区域
- 选择收集装置：4 孔位（A/B/C/D）、96 孔（A1-H12）、384 孔（A1-P24，可设置 margin）
- 自动（循环分配）或手动将切割区域分配到孔位
- 生成含 Y 轴翻转与 `CapID` 孔位标记的 LMD XML（坐标不做平移）
- 本地网页版（Streamlit）：可编辑匹配表、生成预览图并提供下载
- 命令行与网页版共用同一套核心逻辑

## 流程架构

```text
src/lmd_converter/
  core.py                  共享核心逻辑
  extract_geojson.py       提取校准点与切割形状  -> pipeline/extracted.json
  device_config.py         配置 4/96/384 孔位装置        -> pipeline/device.json
  match_shapes.py          形状与孔位匹配            -> pipeline/match.json
  convert_to_xml.py        生成 LMD XML 与预览图       -> output/cutting.xml
```

项目根目录只保留两个入口：`app.py`（Streamlit 网页）和 `run_pipeline.py`（一键命令行）。四个底层脚本在 `src/lmd_converter/` 下，也可以用 `python -m lmd_converter.<模块>` 单独运行。中间文件都是 JSON，可以单独调试。`run_pipeline.py` 可以一键连接四步。

## 安装

建议 Python 3.9-3.12（py-lmd 要求）：

```powershell
conda activate bioinfo
python -m pip install -r requirements.txt
```

`requirements.txt` 已锁定版本：py-lmd 1.6.0（Apache-2.0）和 streamlit 1.60.0。

## 使用

### 网页版（Streamlit）

```powershell
python -m streamlit run app.py
```

在浏览器打开 http://localhost:8501，上传 GeoJSON 文件，选择装置，在表格中编辑切割区域与孔位的匹配，然后生成并下载 XML、预览图和匹配表。

Windows 下也可以双击 `start.bat` 本地启动网页。

### 一键命令行

```powershell
python run_pipeline.py "image_01.geojson" --device 4
```

`--device` 可选 `4`（4 孔位 A/B/C/D）、`96`（A1-H12）、`384`（A1-P24）。加 `--interactive` 会逐步确认装置和孔位匹配。

### 分步执行

```powershell
$env:PYTHONPATH = "src"
python -m lmd_converter.extract_geojson "image_01.geojson"
python -m lmd_converter.device_config --device 96 --margin 0
python -m lmd_converter.match_shapes --interactive
python -m lmd_converter.convert_to_xml
```

## 部署（可分享链接）

网页版可免费部署到 Streamlit Community Cloud：

1. 将本仓库推送到 GitHub 公开仓库
2. 打开 https://share.streamlit.io 并用 GitHub 账号登录
3. 选择仓库，主文件设为 `app.py`，点击部署

部署完成后会获得公网地址，如 `https://username-reponame.streamlit.app`，别人点开即可使用。

## 致谢与引用

本项目的功能流程受 [Qupath_to_LMD](https://github.com/CosciaLab/Qupath_to_LMD)（CosciaLab）启发，XML 序列化基于 [py-lmd](https://github.com/MannLabs/py-lmd)（MannLabs，Apache-2.0）。本仓库代码均为独立编写，不包含 Qupath_to_LMD 的源代码。

- Nimo, J. et al. (2025). OpenDVP: An experimental and computational framework for community-empowered deep visual proteomics. bioRxiv. https://doi.org/10.1101/2025.07.13.662099
- Schmacke, N. A. et al. (2023). SPARCS, a platform for genome-scale CRISPR screening for spatial cellular phenotypes. bioRxiv. https://doi.org/10.1101/2023.06.01.542416

## 许可证

Apache-2.0，详见 `LICENSE`。py-lmd 同样为 Apache-2.0，详见 `NOTICE.txt`。
