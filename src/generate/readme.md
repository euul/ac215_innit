# Generate Module

## Overview

The `Generate` module generates additional training data based on an existing labeled dataset using the 'gemini-1.5-flash-002' model. This module is designed to help create customized English learning materials tailored to specific proficiency levels.

The module works by downloading the training dataset from Google Cloud Platform (GCP) and generating new samples. It does this by creating a Cloud Run job in GCP with the following configuration:

1. **Container image URL**: `yanher/generate_samples:v1.6`
2. **Container arguments**:
   - `--level=<level>`: Specifies the proficiency level (A1, A2, B1, B2, C1).
   - `--n_samples=<n_samples>`: Defines the number of samples to generate.
3. **Service account**: Ensure that the selected service account has the following roles:
   - **AI Platform Admin**
   - **Storage Admin**
   - **Vertex AI Administrator**

### Available Proficiency Levels

- A1
- A2
- B1
- B2
- C1
