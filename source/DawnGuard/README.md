# DawnGuard

This repository contains the artifacts for the paper:
**"Early-Stage Detection of Encrypted Malware Traffic via Multi-flow Temporal Graph Learning"**,
which has been submitted to IEEE TIFS.

---
## Code
We commit to publishing all reproducible artifacts of this paper, including code, configuration files and data, on GitHub upon acceptance of the paper. To ensure high code quality and enhance overall readability, we are currently reorganizing and optimizing our code. The complete reproducible artifacts will be made publicly available here in the near future.

---
## Dataset

**CTU-Malware**. Comprising real-world university network traces, this dataset provides continuous PCAP captures rather than isolated samples. 
This continuity preserves the natural chronological order and concurrency of flows, enabling the reconstruction of temporal-topological structures in multi-flow attacks. 
We select six malware families (i.e., Dridex, Emotet, Geodo, Miuref, Zeus, and TrickBot) for D1, and use the remaining traffic for D2 to evaluate unseen malware detection.
You can download the above dataset via https://www.stratosphereips.org/datasets-malware.

**USTC-TFC2016**. This real-world dataset contains ten categories, each of benign and malware traffic. 
To facilitate inter-flow analysis, we utilize original timestamps and IP identifiers to re-establish session-based context, grouping logical interactions into local subgraphs. 
We construct D3 from malware and D4 from benign traffic.
D4 serves as a noisy testbed to evaluate false positives in simulated real-world network scenarios.
You can download the above dataset via https://github.com/davidyslu/USTC-TFC2016.

---
## Supported Environments
The project is compatible with the following operating systems and environments:

### Operating System
- Windows or Ubuntu (Linux)
### Programming Language & Version
- Python 3.10 is required.
- Must use the python3 command (ensure compatibility with modern deep learning libraries).
### Software & Libraries
- PyTorch: The core deep learning framework used for model implementation.
- CUDA-compatible GPU: Required for accelerating the Vision Transformer (ViT) and Graph Learning modules.
- Key Dependencies: Standard scientific computing and networking libraries (e.g., for PCAP processing and graph construction). 
### Hardware Requirements
- GPU: NVIDIA GeForce RTX 3080 (or equivalent/superior) is used as the baseline for performance evaluation. 
- RAM: At least 32GB to handle graph reconstruction and temporal-topological analysis.
- CPU: Intel Core i7 3.4 GHz or higher.
- Disk Space: Sufficient space for storing large-scale network datasets (e.g., CTU-Malware, USTC-TFC2016) and model checkpoints.
### Recommended Configuration
- SSD storage: For faster data loading and processing

---
## Contact
If you have any questions, please get in touch with us.

* Jizhe Jia (jiajizhe@bit.edu.cn)

More detailed information about the research of Meng Shen Lab can be found here (https://mengshen-office.github.io/).
