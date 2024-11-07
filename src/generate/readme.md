# Generate Module

## Overview
The `Generate` module generates additional training data based on an existing labeled dataset using the 'gemini-1.5-flash-002' model. It enables the creation of English learning materials customized to specific proficiency levels.

This module downloads the training dataset from GCP and generates new samples by passing the following parameters to the container:
- `--level=<level>`: Specifies the proficiency level (A1, A2, B1, B2, C1).
- `--n_samples=<n_samples>`: Defines the number of samples to generate.

### Available Proficiency Levels
- A1
- A2
- B1
- B2
- C1
