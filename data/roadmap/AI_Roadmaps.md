# AI Engineer

## Roadmap Overview

Goal of the roadmap: To transition a learner from basic programming proficiency to building, deploying, and scaling production-grade AI applications using Large Language Models (LLMs), Vector Databases, and Agentic frameworks.

Expected learning outcome: The learner will be able to architect enterprise RAG pipelines, develop autonomous agents, manage LLM context windows, and deploy robust APIs that serve AI features to end-users.

Typical learning duration: 6 to 9 months of consistent part-time study for an individual already possessing basic programming knowledge.

---

## Prerequisites

- Basic understanding of Python programming (variables, loops, functions, OOP).
- Familiarity with working in a terminal/command prompt.
- Basic understanding of Git (commit, push, pull).
- High school level algebra.

---

## Beginner Stage

Topics: Python advanced concepts (asyncio, type hinting), REST APIs, JSON parsing, Introduction to OpenAI API, prompt structuring.

Projects: A terminal-based chatbot using the OpenAI API. A script that summarizes text files using basic prompt engineering.

Practice: Recreate basic ChatGPT functionality locally using Python. Experiment with different temperature and top_p settings.

Expected Outcome: Ability to make reliable API calls to LLM providers, manage API keys securely, and parse JSON responses.

---

## Intermediate Stage

Topics: Embeddings, Vector Databases (ChromaDB, Pinecone), Naive RAG architecture, document chunking, LangChain basics.

Projects: A web-based PDF Q&A application using Streamlit or Gradio. A semantic search engine over a small dataset of Wikipedia articles.

Practice: Implement different chunking strategies (character vs. recursive) and compare retrieval quality. Write LangChain LCEL pipelines.

Expected Outcome: Ability to ingest raw text data, embed it, store it in a vector database, and retrieve relevant context to augment an LLM prompt.

---

## Advanced Stage

Topics: Advanced RAG (Hybrid search, Re-ranking with Cross-Encoders, Query Transformation), Tool Calling / Function Calling, LangGraph state management, Semantic Caching.

Projects: A multi-agent research assistant built with LangGraph that searches the web, reads articles, and synthesizes a report. An API that executes SQL queries based on natural language input securely.

Practice: Implement a LangGraph workflow with conditional edges and a "human-in-the-loop" approval step.

Expected Outcome: Ability to build stateful AI agents that can interact with external systems and databases reliably.

---

## Expert Stage

Topics: Model Context Protocol (MCP), LangSmith tracing and evaluation, streaming responses via Server-Sent Events (SSE) or WebSockets, Prompt Injection prevention, deploying open-source models (vLLM, Ollama).

Projects: A production-ready AI backend using FastAPI that streams responses, logs all trajectories to LangSmith, and uses an MCP Server to securely access local enterprise data.

Practice: Set up automated evaluation datasets in LangSmith. Load test an AI endpoint to observe rate-limiting behavior.

Expected Outcome: Ability to architect secure, scalable, and observable AI systems that meet enterprise production standards.

---

## Mathematics Roadmap

Statistics: Learn basic descriptive statistics and distributions to understand evaluation metrics.

Probability: Learn conditional probability to understand how LLMs predict the next token.

Linear Algebra: Learn matrix multiplication, dot products, and cosine similarity to deeply understand vector embeddings.

Calculus: Not strictly necessary for an applied AI Engineer unless diving into model fine-tuning.

Optimization: Understand the concept of loss conceptually, but mathematical deep dives are unnecessary for the applied AI Engineer.

---

## Programming Roadmap

Master Python. Focus intensely on `asyncio` for concurrent API calls, `Pydantic` for strict data validation, and decorators. Learn basic TypeScript/JavaScript to interface with frontend teams building AI UIs.

---

## AI Fundamentals

Understand the difference between Discriminative AI and Generative AI. Learn the history of NLP from Word2Vec to modern Transformers.

---

## Machine Learning

Learn basic evaluation metrics (Precision, Recall, F1 Score) as these apply directly to evaluating RAG retrieval performance.

---

## Deep Learning

Understand the Transformer architecture conceptually (Self-Attention, Positional Encoding), but do not spend months learning to write backpropagation from scratch.

---

## Transformers

Understand the difference between Encoder-only (BERT, used for embeddings/re-ranking) and Decoder-only (GPT, used for generation) architectures.

---

## Generative AI

Learn temperature scaling, context window limits, tokenization mechanics (BPE), and hallucination mitigation strategies.

---

## LLM Engineering

Learn how to interact with instruction-tuned models. Understand the difference between Base models and Chat models. Learn how to run quantized models locally using Ollama or LM Studio.

---

## Prompt Engineering

Master Few-Shot Prompting, Chain of Thought (CoT), ReAct prompting, and enforcing strict JSON output schemas.

---

## RAG

Master Naive RAG, then progress to Advanced RAG techniques: Parent Document Retrieval, Multi-Query Retrieval, and Cross-Encoder Re-ranking.

---

## AI Agents

Understand how an LLM decides to call a tool. Learn to build agentic loops (Thought -> Action -> Observation -> Response).

---

## LangChain

Learn LangChain Expression Language (LCEL). Understand Document Loaders, Text Splitters, and Output Parsers.

---

## LangGraph

Master State Graphs, Reducers (`add_messages`), conditional routing, and Checkpointers for conversational memory persistence.

---

## MCP

Learn how to build an MCP Server in Python to expose a local SQLite database to an MCP Client (like Claude Desktop or a custom LangGraph agent).

---

## LangSmith

Learn to configure tracing via environment variables. Build an evaluation pipeline using `LLM-as-a-Judge` to score RAG outputs.

---

## Vector Databases

Start with local ChromaDB. Progress to cloud-hosted Pinecone or Qdrant. Understand indexing algorithms (HNSW).

---

## Backend Development

Master FastAPI. Learn to structure API routes, handle dependencies, and stream responses asynchronously.

---

## Cloud

Learn AWS (EC2 for hosting APIs, S3 for storing documents) or equivalent services in Azure/GCP.

---

## Deployment

Learn Docker. Write a multi-stage Dockerfile for a FastAPI + LangChain application. Deploy to a platform like AWS ECS or Render.

---

## MLOps

Learn basic CI/CD (GitHub Actions) to automatically test prompt outputs before deploying API changes.

---

## Portfolio Milestones

After Beginner Stage: A GitHub repo with a CLI tool that uses the OpenAI API to translate or summarize text.

After Intermediate Stage: A deployed Streamlit app showcasing a working RAG pipeline over a public dataset.

After Advanced Stage: A repository demonstrating a LangGraph multi-agent system executing external tools.

After Expert Stage: A fully Dockerized, streaming FastAPI backend interacting with LangSmith and a Vector DB, deployed to the cloud.

---

## GitHub Milestones

Beginner: Clean Python scripts with `requirements.txt` and basic `README.md`.

Intermediate: Modularized code (`src/` folder), environment variable templates (`.env.example`), and basic unit tests.

Advanced: LangGraph architectures documented with Mermaid.js diagrams in the README.

Expert: Fully containerized infrastructure using `docker-compose.yml`, GitHub Actions for CI/CD, and comprehensive API documentation (Swagger/OpenAPI).

---

## Resume Milestones

After the Intermediate Stage, the candidate becomes competitive for AI Engineering Internships. After the Advanced Stage, the candidate is competitive for Junior AI Engineer roles. After mastering the Expert Stage and deploying those systems, the candidate is competitive for Mid-Level AI Engineer roles.

---

## Interview Readiness

Beginner Stage: Can pass basic Python screening interviews.

Intermediate Stage: Can pass basic RAG conceptual interviews and take-home coding tests involving LangChain.

Advanced Stage: Can pass System Design interviews for standard AI applications and explain multi-agent architectures.

Expert Stage: Can pass Senior-level AI infrastructure interviews, including scaling, security, and observability discussions.

---

## Common Mistakes

- Spending months learning PyTorch and backpropagation when the goal is to build applied LLM applications (AI Engineer role).
- Using LangChain for everything instead of learning the underlying OpenAI/Anthropic API structures.
- Ignoring backend engineering (FastAPI, Docker). An AI Engineer who cannot deploy their code is unhirable.
- Memorizing prompt templates instead of understanding how to systematically evaluate prompt performance.

---

## Estimated Timeline

Full-time learners (40 hrs/week): 3 to 4 months.

Part-time learners (15 hrs/week): 6 to 9 months.

University students (alongside coursework): 9 to 12 months.

--------------------------------------------------------
LEARNING PATH ADAPTATION
--------------------------------------------------------

Internship: The AI Engineer roadmap for internships should stop at the Intermediate Stage. Focus heavily on mastering Python, basic API integration, and creating one polished, bug-free Streamlit RAG application.

Junior: The AI Engineer roadmap for Junior roles must include the Advanced Stage. The candidate must prove they can handle Tool Calling and basic agentic workflows, as companies are moving beyond Naive RAG.

Mid-Level: The AI Engineer roadmap for Mid-Level roles requires absolute mastery of the Expert Stage. The focus shifts from "making it work" to "making it scalable, secure, and observable" using LangSmith, streaming APIs, and Docker.

Senior Career Transition: For traditional Senior Software Engineers transitioning to an AI Engineer role, skip the basic Programming and Backend stages. Focus entirely on Vector Databases, Advanced RAG, LangGraph, and prompt injection security. The timeline for this transition is typically 2-3 months.

# Machine Learning Engineer

## Roadmap Overview

Goal of the roadmap: To guide a learner from fundamental mathematics and data manipulation to training, optimizing, and deploying scalable machine learning models in production environments.

Expected learning outcome: The learner will be able to perform feature engineering, train robust classical and deep learning models, utilize MLOps tools for tracking, and deploy models as low-latency microservices using containers.

Typical learning duration: 9 to 12 months of consistent part-time study, assuming prior basic programming knowledge.

---

## Prerequisites

- Intermediate Python programming.
- Solid understanding of high school mathematics (Algebra, Pre-Calculus).
- Familiarity with basic data structures and algorithms.

---

## Beginner Stage

Topics: Linear Algebra (Vectors, Matrices), Calculus (Derivatives, Gradients), Statistics (Distributions, Hypothesis Testing), Pandas, NumPy, Matplotlib.

Projects: An Exploratory Data Analysis (EDA) notebook on a public dataset (e.g., Titanic or Housing Prices) uncovering statistical insights.

Practice: Implement basic matrix multiplication and derivative calculations in raw Python before using libraries.

Expected Outcome: Ability to manipulate large tabular datasets efficiently, handle missing values, and visualize data distributions.

---

## Intermediate Stage

Topics: Scikit-Learn, Classical ML (Linear/Logistic Regression, Decision Trees, Random Forests, SVMs), Cross-Validation, Hyperparameter Tuning (GridSearch), Evaluation Metrics (ROC-AUC, F1).

Projects: An end-to-end classification model predicting customer churn, complete with a robust feature engineering pipeline.

Practice: Participate in beginner Kaggle competitions. Write custom scikit-learn transformers.

Expected Outcome: Ability to train, evaluate, and select the best classical machine learning model for tabular data problems.

---

## Advanced Stage

Topics: Deep Learning Fundamentals, PyTorch or TensorFlow, Convolutional Neural Networks (CNNs), Recurrent Neural Networks (RNNs/LSTMs), Gradient Descent Optimizers (Adam), MLOps basics (MLflow).

Projects: An image classification model built from scratch in PyTorch. A time-series forecasting model using LSTMs.

Practice: Implement a custom training loop in PyTorch. Use MLflow to track different hyperparameter experiments.

Expected Outcome: Ability to build and train deep neural networks on image or sequential data, and systematically track experiments.

---

## Expert Stage

Topics: Model Deployment (FastAPI, Docker, ONNX, TensorRT), Distributed Training, CI/CD for ML, Data Drift Detection, Cloud ML Platforms (AWS SageMaker).

Projects: A complete MLOps pipeline that trains a model, converts it to ONNX, packages it in a Docker container, and serves it via FastAPI with inference monitoring.

Practice: Write a GitHub Action that automatically triggers model retraining when data changes.

Expected Outcome: Ability to architect and deploy highly optimized, production-ready machine learning systems that run at scale.

---

## Mathematics Roadmap

Linear Algebra: Start here. Focus on matrix operations, eigenvalues, and eigenvectors, as these are the core of neural networks.

Calculus: Learn partial derivatives and the chain rule to deeply understand how backpropagation calculates gradients.

Probability: Learn Bayes' theorem and probability distributions, essential for generative and probabilistic models.

Statistics: Learn variance, standard deviation, and sampling methods for robust model evaluation and A/B testing.

Optimization: Understand convex versus non-convex optimization, gradient descent, and learning rate scheduling.

---

## Programming Roadmap

Master Python, heavily focusing on vectorized operations in NumPy. Learn OOP for structuring complex PyTorch models. Learn basic C++ if targeting high-performance inference optimization later.

---

## AI Fundamentals

Understand the Bias-Variance tradeoff, overfitting, underfitting, and the curse of dimensionality.

---

## Machine Learning

Master Ensemble methods (XGBoost, LightGBM) as they dominate tabular data in the industry. Master dimensionality reduction (PCA, t-SNE).

---

## Deep Learning

Master PyTorch `nn.Module`, `DataLoader`, and custom datasets. Understand batch normalization and dropout thoroughly.

---

## Transformers

Understand the self-attention mechanism mathematically. Learn to use the HuggingFace `transformers` library to fine-tune existing models (BERT, RoBERTa) for classification tasks.

---

## Generative AI

Not the primary focus for a traditional Machine Learning Engineer, but understand the basics of Autoencoders and GANs.

---

## LLM Engineering

Learn Parameter-Efficient Fine-Tuning (PEFT) specifically LoRA, as ML Engineers are increasingly tasked with fine-tuning small open-source LLMs.

---

## Prompt Engineering

Not required for this roadmap, beyond basic API usage.

---

## RAG

Understand dense retrieval and embedding generation, as these overlap with traditional ML recommendation systems.

---

## AI Agents

Not required for the Machine Learning Engineer roadmap.

---

## LangChain

Not required, unless bridging into an AI Engineer role.

---

## LangGraph

Not required.

---

## MCP

Not required.

---

## LangSmith

Not required.

---

## Vector Databases

Learn FAISS for high-performance, in-memory similarity search, which is heavily used in traditional ML pipelines.

---

## Backend Development

Master FastAPI and Pydantic to create robust, strongly-typed REST APIs that serve model predictions.

---

## Cloud

Learn AWS SageMaker or GCP Vertex AI for managing remote training jobs and deploying endpoints. Understand Amazon S3 for storing massive datasets.

---

## Deployment

Master Docker. Learn to write Dockerfiles that handle heavy dependencies (CUDA, PyTorch) efficiently using multi-stage builds. Learn model optimization formats like ONNX.

---

## MLOps

Master MLflow for experiment tracking and Model Registry. Learn DVC (Data Version Control) to version datasets alongside code.

---

## Portfolio Milestones

After Beginner Stage: A well-documented Jupyter Notebook demonstrating advanced EDA and statistical testing on a real-world dataset.

After Intermediate Stage: A GitHub repository containing a clean Python package for training and evaluating an XGBoost model.

After Advanced Stage: A PyTorch project tracked with MLflow, demonstrating custom training loops and deep learning architecture.

After Expert Stage: A fully deployed ML microservice (Docker + FastAPI + ONNX) with an automated CI/CD pipeline on GitHub Actions.

---

## GitHub Milestones

Beginner: Basic scripts and Jupyter Notebooks.

Intermediate: Transition from Notebooks to Python modules (`.py` files). Inclusion of `requirements.txt`.

Advanced: Integration of MLOps tools (e.g., `mlruns` directory ignored, DVC pipelines defined).

Expert: Production-ready repos with Dockerfiles, GitHub Actions workflows, and rigorous unit tests for data processing functions.

---

## Resume Milestones

After the Intermediate Stage, the candidate is competitive for Data Science / ML Internships. After the Advanced Stage, the candidate is competitive for Junior Machine Learning Engineer roles. After mastering the Expert Stage (Deployment and MLOps), the candidate is competitive for Mid-Level Machine Learning Engineer roles.

---

## Interview Readiness

Beginner Stage: Can pass basic Python and SQL data manipulation interviews.

Intermediate Stage: Can pass Machine Learning theory interviews (e.g., explaining Random Forests vs. SVMs) and take-home modeling tasks.

Advanced Stage: Can pass Deep Learning architecture interviews and PyTorch coding challenges.

Expert Stage: Can pass ML System Design interviews (e.g., designing a recommendation system for millions of users) and MLOps infrastructure rounds.

---

## Common Mistakes

- Staying entirely in Jupyter Notebooks. A Machine Learning Engineer must write modular, production-ready Python code.
- Focusing purely on maximizing model accuracy (hyperparameter tweaking) while ignoring inference latency and deployment costs.
- Skipping mathematics. While an AI Engineer can skip Calculus, a Machine Learning Engineer will fail senior technical interviews without understanding gradients and optimization.
- Ignoring MLOps. Training a model is only 20% of the job; tracking, deploying, and monitoring it is the other 80%.

---

## Estimated Timeline

Full-time learners (40 hrs/week): 4 to 6 months.

Part-time learners (15 hrs/week): 9 to 12 months.

University students (alongside coursework): 12 to 18 months.

--------------------------------------------------------
LEARNING PATH ADAPTATION
--------------------------------------------------------

Internship: The Machine Learning Engineer roadmap for internships should focus deeply on the Beginner and Intermediate stages. Deep Learning and MLOps are rarely expected from interns, but strong SQL, Pandas, and Scikit-Learn skills are strictly required.

Junior: The Machine Learning Engineer roadmap for Junior roles must cover up to the Advanced stage (PyTorch/Deep Learning) and the absolute basics of the Expert stage (wrapping a model in FastAPI).

Mid-Level: The Machine Learning Engineer roadmap for Mid-Level roles heavily indexes on the Expert Stage. The candidate must prove they can utilize Docker, MLflow, and cloud platforms to deploy and monitor models independently.

Senior Career Transition: For a traditional Data Scientist transitioning to a Machine Learning Engineer role, skip the mathematics, ML, and DL stages. Focus entirely on the Expert Stage: Backend Development (FastAPI), Deployment (Docker, ONNX, Kubernetes), and MLOps (CI/CD, MLflow). The timeline for this specific transition is typically 3-4 months.
