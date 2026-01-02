# CV Dataset Utilities

CV Dataset Utilities is a collection of **lightweight tools for preparing and cleaning Computer Vision datasets**, specifically designed for YOLO-style workflows.

This repository focuses strictly on **dataset hygiene and preprocessing** — tasks that are required *before* model training begins.

It intentionally does **not** include any model training or inference code.

---

## Included Tools

This repository bundles the following utilities because they operate at the **same responsibility layer** (dataset preparation):

### 1. YOLO Image–Label Extractor
Extracts only valid image–label pairs from a dataset.

**Purpose**
- Create clean subsets
- Remove orphan images or labels
- Prepare datasets for training or review

**Input**
- Images folder
- Labels folder (YOLO `.txt`)

**Output**
- New dataset folder with:
  - `images/`
  - `labels/`
  - `classes.txt` (if present)

---

### 2. YOLO Class Remapper
Remaps YOLO class indices by **matching class names**, not raw IDs.

**Purpose**
- Fix class index mismatches
- Merge or reorder datasets safely
- Preserve bounding box coordinates

**Key Behavior**
- Only updates the first token (class index)
- Leaves coordinates untouched
- Keeps labels unchanged if mapping is not found
- Creates automatic backups

---

### 3. Image Renamer
Command-line utility to rename images sequentially.

**Purpose**
- Normalize filenames
- Avoid naming conflicts
- Prepare datasets for automation pipelines

**Features**
- Custom prefix
- Custom start index
- Dry-run mode

---

## What This Repo Is NOT

- ❌ Not an auto-labeling tool
- ❌ Not a model training repository
- ❌ Not an inference or deployment system

This separation is intentional.

---

## Installation

### Requirements
- Python 3.7+
- pip

### Python Dependencies
```bash
pip install -r requirements.txt
```

> **Note**
> - `tkinter` is bundled with most Python installations  
> - On Linux:
> ```bash
> sudo apt install python3-tk
> ```

---

## Setup & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/cv-dataset-utilities.git
cd cv-dataset-utilities
```

---

### 2. YOLO Image–Label Extractor (GUI)
```bash
python yolo_image_extractor/image_extractor.py
```

Steps:
1. Select source image folder
2. Select source label folder
3. Select output folder
4. Click **Start Extraction**

---

### 3. YOLO Class Remapper (GUI)
```bash
python yolo_class_remapper/remap.py
```

Steps:
1. Select labels folder
2. Select `old_classes.txt`
3. Select `new_classes.txt`
4. Select output folder
5. Press **Enter** or click **Run Remap**

---

### 4. Image Renamer (CLI)
```bash
python image_renamer/rename.py /path/to/images --start 1 --prefix image
```

Dry run:
```bash
python image_renamer/rename.py /path/to/images --dry-run
```

---

## Recommended Repository Structure

```
cv-dataset-utilities/
├── yolo_image_extractor/
│   └── image_extractor.py
├── yolo_class_remapper/
│   └── remap.py
├── image_renamer/
│   └── rename.py
├── requirements.txt
└── README.md
```

---

## Typical Workflow

1. Rename images for consistency
2. Remap class indices if required
3. Extract clean image–label pairs
4. Pass dataset to training pipeline

---

## License

MIT License

---

## Author

Varad Kulkarni  
Applied AI / Computer Vision
