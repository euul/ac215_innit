# Generate Module

## Overview
This module is designed to generate additional training data based on an existing labeled dataset using the 'gemini-1.5-flash-002' model. It facilitates the creation of English learning materials tailored to specific proficiency levels.

## Instructions

### 1. Running the Container
**TBC**

### 2. Downloading the Training Dataset
First, download the training dataset from GCP by running the following command:

```bash
python download_train_datasets.py
```

To generate more samples for each proficiency level, execute the following command:

```bash
python gen_samples.py --level <level>
```

Replace <level> with one of the following options: A1, A2, B1, B2, C1