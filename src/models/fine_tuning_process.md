# Fine-tuning Process Documentation


## Hyperparameters

| **Hyperparameter**               | **Value**                     |
|-----------------------------------|-------------------------------|
| **Model**                        | `microsoft/deberta-v3-small`   |
| **Max Sequence Length**           | 800                           |
| **Learning Rate**                 | \( 2 \times 10^{-5} \)        |
| **Training Batch Size**           | 4                             |
| **Evaluation Batch Size**         | 4                             |
| **Number of Training Epochs**     | 5                             |
| **Weight Decay**                  | 0.01                          |
| **Metric**                        | `accuracy`                    |


## Run Summary

| **Metric**                    | **Value**             |
|--------------------------------|-----------------------|
| **eval/accuracy**              | 56.16438              |
| **eval/loss**                  | 1.15111               |
| **eval/runtime**               | 10.6216               |
| **eval/samples_per_second**    | 20.618                |
| **eval/steps_per_second**      | 5.178                 |
| **test/accuracy**              | 56.16438              |
| **test/loss**                  | 1.15111               |
| **test/runtime**               | 10.8404               |
| **test/samples_per_second**    | 20.202                |
| **test/steps_per_second**      | 5.074                 |
| **total_flos**                 | 679990916088000.0     |
| **train/epoch**                | 5                     |
| **train/global_step**          | 825                   |
| **train/grad_norm**            | 18.91897              |
| **train/learning_rate**        | \(2 \times 10^{-5}\)  |
| **train/loss**                 | 0.8989                |
| **train_loss**                 | 1.14098               |
| **train_runtime**              | 678.1971              |
| **train/samples_per_second**   | 4.844                 |
| **train/steps_per_second**     | 1.216                 |


## Fine-tuning Process

* **Batch Size**: Ideally, we would like to increase the batch size, but due to memory limitations, we are currently using a batch size of 4. We plan to increase it when training on cloud infrastructure.

* **Max Sequence Length**: Initially, we set the max sequence length to 512, but the model did not predict the C1 level. We hypothesized that this was because the sequence length was too short to capture the features of C1-level text, which is typically longer. After analyzing the distribution of our text data, we found that most samples had a length around 800, so we increased the max sequence length accordingly.

* **Learning Rate**: We started with a learning rate of 1e-5, but it appeared to be too large. After lowering the learning rate, the model's performance improved.

## Future Plan: Bayes Parameter Tuning using Sweep

We plan to run hyperparameter optimization at scale by automating multiple experiments with different configurations using Weights and Biases Sweeps. This will allow us to fine-tune the model with Bayes parameter tuning.
