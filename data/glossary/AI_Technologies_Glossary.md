# Artificial Intelligence Fundamentals

# Artificial Intelligence

## Definition
Artificial Intelligence is a broad field of computer science focused on creating systems capable of performing tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and natural language understanding.

---

## Why It Matters
Artificial Intelligence forms the foundational theory and engineering practice behind all modern automation, predictive modeling, and generative systems, fundamentally altering how software interacts with the physical and digital world.

---

## Where It Is Used
Artificial Intelligence is used in autonomous vehicles, fraud detection systems, medical image analysis, recommendation engines, and natural language processing applications.

---

## Advantages
- Automates complex, repetitive tasks at scale.
- Identifies patterns in massive datasets faster than human analysts.
- Enables highly personalized user experiences.

---

## Limitations
- Heavily dependent on the quality and quantity of training data.
- Often operates as a "black box," making decision processes opaque.
- Susceptible to amplifying historical biases present in training data.

---

## Related Concepts
Machine Learning, Deep Learning, Generative AI.

---

## Common Interview Questions
- How do you define Artificial Intelligence compared to traditional rule-based software engineering?
- Can you explain the difference between Artificial General Intelligence (AGI) and Narrow AI?

---

## Common Misconceptions
A frequent misconception is that Artificial Intelligence inherently possesses consciousness or understanding, whereas modern AI is strictly advanced statistical pattern matching.

---

## Practical Example
A navigation application using real-time traffic data, historical patterns, and routing algorithms to predict the fastest route to a destination.

---

## Keywords
AI, Automation, Narrow AI, Machine Intelligence, Pattern Recognition.


# Machine Learning

## Definition
Machine Learning is a subset of Artificial Intelligence focused on developing algorithms that allow computers to learn from and make predictions or decisions based on data, without being explicitly programmed for that specific task.

---

## Why It Matters
Machine Learning enables systems to adapt and improve over time as they process more data, shifting software engineering from manually writing rules to defining architectures that learn the rules from examples.

---

## Where It Is Used
Machine Learning is heavily used in credit scoring, email spam filtering, product recommendation systems, and predictive maintenance in manufacturing.

---

## Advantages
- Improves accuracy as the volume of training data increases.
- Discovers non-linear relationships in tabular data that are invisible to human analysts.
- Reduces the need for hardcoded business logic in software.

---

## Limitations
- Degrades in performance when exposed to data distributions unseen during training (data drift).
- Requires significant computational resources for model training.
- Often requires extensive manual feature engineering for optimal performance.

---

## Related Concepts
Artificial Intelligence, Deep Learning, Supervised Learning, Unsupervised Learning.

---

## Common Interview Questions
- What is the difference between a Random Forest and a Support Vector Machine?
- How do you handle imbalanced datasets in a classification task?

---

## Common Misconceptions
Many people confuse Machine Learning with Deep Learning. Machine Learning includes classical algorithms (like Decision Trees or K-Means) that work well on small, structured tabular data without requiring neural networks.

---

## Practical Example
An algorithm analyzing historical customer purchasing data to classify whether a new customer is likely to churn or remain subscribed.

---

## Keywords
ML, Algorithms, Predictive Modeling, Feature Engineering, Training Data.


# Deep Learning

## Definition
Deep Learning is a specialized subfield of Machine Learning based on Artificial Neural Networks with multiple layers (deep architectures) designed to extract high-level features from raw input data.

---

## Why It Matters
Deep Learning drives the current revolution in Artificial Intelligence because it scales exponentially with compute and data, effectively solving problems in computer vision and natural language processing that classical Machine Learning could not handle.

---

## Where It Is Used
Deep Learning is used in facial recognition systems, voice assistants, autonomous driving perception modules, and all modern Large Language Models.

---

## Advantages
- Automatically performs feature extraction from raw unstructured data (images, text, audio).
- Achieves state-of-the-art performance on highly complex perception tasks.
- Highly parallelizable, benefiting massively from GPU acceleration.

---

## Limitations
- Requires massive amounts of labeled training data to prevent overfitting.
- Computationally expensive, requiring significant GPU hardware.
- Extremely opaque, making it difficult to debug or explain specific model predictions.

---

## Related Concepts
Machine Learning, Transformer, Neural Network, Convolutional Neural Network (CNN).

---

## Common Interview Questions
- Explain the vanishing gradient problem in deep neural networks and how modern architectures mitigate it.
- What is the mathematical difference between Layer Normalization and Batch Normalization?

---

## Common Misconceptions
A common misconception is that Deep Learning is universally superior to classical Machine Learning. For small, structured tabular datasets, classical models like XGBoost often outperform Deep Learning models.

---

## Practical Example
A Convolutional Neural Network (CNN) processing raw pixels from an MRI scan to detect anomalies without any human-defined features.

---

## Keywords
Neural Networks, Representation Learning, Backpropagation, Gradient Descent, PyTorch, TensorFlow.

---

# Large Language Models

# LLM

## Definition
A Large Language Model (LLM) is a Deep Learning model based on the Transformer architecture, trained on massive datasets of text, capable of understanding and generating human language by predicting the next token in a sequence.

---

## Why It Matters
Large Language Models serve as the foundational reasoning engines for modern generative AI applications, enabling complex natural language understanding, translation, summarization, and autonomous agent decision-making.

---

## Where It Is Used
Large Language Models are used in conversational chatbots, code generation assistants, text summarization tools, and as the reasoning core in multi-agent orchestration frameworks.

---

## Advantages
- Exhibits zero-shot and few-shot reasoning capabilities across diverse domains.
- Drastically reduces the time required to build natural language interfaces.
- Can be fine-tuned or augmented (via RAG) to handle highly specialized, domain-specific tasks.

---

## Limitations
- Prone to hallucinations, generating plausible but factually incorrect information.
- Highly expensive to train and serve, requiring significant GPU memory (VRAM).
- Constrained by a fixed Context Window, limiting the amount of text they can process simultaneously.

---

## Related Concepts
Transformer, Prompt Engineering, Hallucination, RAG.

---

## Common Interview Questions
- Describe the process an LLM uses to generate text from a given prompt.
- What are the differences between an instruction-tuned LLM and a base LLM?

---

## Common Misconceptions
A frequent misconception is that an LLM stores a database of facts. In reality, an LLM stores statistical probabilities of word occurrences (weights), which is why it can easily hallucinate when recalling specific data.

---

## Practical Example
An enterprise chatbot utilizing a Large Language Model to draft email responses based on short bullet points provided by a user.

---

## Keywords
Large Language Model, Foundation Model, GPT, Llama, Claude, Next Token Prediction.


# Transformer

## Definition
The Transformer is a deep learning architecture introduced in 2017 that relies entirely on an attention mechanism to capture global dependencies between inputs and outputs, eliminating the need for recurrence or convolutions.

---

## Why It Matters
The Transformer architecture revolutionized Natural Language Processing by enabling highly parallelized training on massive datasets, directly enabling the creation of modern Large Language Models.

---

## Where It Is Used
The Transformer is the underlying architecture for all modern Large Language Models, Vision Transformers for image processing, and audio generation models.

---

## Advantages
- Allows for parallel processing of sequence data, drastically speeding up training compared to RNNs.
- Effectively handles long-range dependencies in text using the self-attention mechanism.
- Scales efficiently with increased compute and dataset sizes.

---

## Limitations
- The computational complexity of the self-attention mechanism grows quadratically with sequence length, making long context windows expensive.
- Requires massive amounts of data to train effectively from scratch.
- Lacks inherent sequential inductive bias, requiring explicit Positional Encoding.

---

## Related Concepts
Attention, Deep Learning, Positional Encoding, Multi-Head Attention.

---

## Common Interview Questions
- Explain the mathematical operation inside a self-attention block of a Transformer.
- Why did the Transformer architecture replace LSTMs in natural language processing?

---

## Common Misconceptions
People often assume Transformers can only process text. However, Vision Transformers (ViTs) process image patches using the exact same attention mechanism.

---

## Practical Example
A language translation service translating a paragraph from English to French, using the attention mechanism to correctly map adjectives to nouns despite differing grammatical structures.

---

## Keywords
Self-Attention, Encoder, Decoder, Neural Architecture, Parallelization.


# Token

## Definition
A Token is the fundamental unit of data processed by a Large Language Model, representing a sequence of characters, a part of a word, or an entire word.

---

## Why It Matters
Tokens define the computational unit for Large Language Models. API pricing, processing speed, and Context Window limits are all measured in Tokens, making them a critical metric for AI engineering.

---

## Where It Is Used
Tokens are used in LLM API billing, Prompt Engineering constraints, and analyzing Context Window overflow.

---

## Advantages
- Allows models to handle out-of-vocabulary words by breaking them down into known sub-word tokens.
- Standardizes the input format for the Transformer architecture regardless of the input language.
- More efficient than character-level encoding, balancing vocabulary size and sequence length.

---

## Limitations
- Token boundaries do not always align with linguistic syllables or words, causing issues with rhyming or character-level manipulation tasks.
- Different languages (especially non-Latin scripts) require significantly more tokens for the same meaning, increasing costs.
- The mapping between words and tokens can be non-intuitive for users.

---

## Related Concepts
Tokenizer, LLM, Context Window.

---

## Common Interview Questions
- Explain how Byte-Pair Encoding (BPE) creates a token vocabulary.
- How does the tokenization of numerical digits affect an LLM's ability to perform mathematics?

---

## Common Misconceptions
A widespread misconception is that one token equals one word. In English, one token typically represents about 3/4 of a word, while in other languages, a single word might be split into multiple tokens.

---

## Practical Example
The word "unbelievable" being split by a Tokenizer into the tokens "un", "believ", and "able" before being processed by an LLM.

---

## Keywords
BPE, Sub-word, Vocabulary, Encoding, LLM Inputs.


# Context Window

## Definition
The Context Window is the maximum number of tokens a Large Language Model can process in a single inference step, including both the input prompt and the generated output.

---

## Why It Matters
The Context Window dictates the limits of what an LLM can "remember" during a conversation or how much documentation it can read at once. Exceeding the Context Window results in the model forcibly truncating information, leading to degraded performance or hard errors.

---

## Where It Is Used
Context Windows are critical in designing RAG architectures (determining chunk size limits), summarizing long documents, and managing conversational memory in AI Agents.

---

## Advantages
- Larger Context Windows allow models to process entire books or codebases in a single prompt.
- Reduces the need for complex summarization or chunking strategies for medium-length texts.
- Allows for extensive Few-shot Learning by placing many examples directly in the prompt.

---

## Limitations
- Computational cost scales quadratically (or near-quadratically) with the size of the Context Window.
- Models often suffer from "lost in the middle" syndrome, where they fail to retrieve facts buried in the center of a massive Context Window.
- Latency increases significantly as the Context Window fills up.

---

## Related Concepts
LLM, Token, RAG, Memory.

---

## Common Interview Questions
- How do you manage conversation history in an AI Agent when the text exceeds the model's Context Window?
- Explain the "Lost in the Middle" phenomenon and how it impacts Retrieval-Augmented Generation.

---

## Common Misconceptions
Many believe that if a model has a 128k Context Window, it will perfectly recall any fact within that text. In reality, retrieval accuracy degrades significantly as the context approaches the maximum limit.

---

## Practical Example
An AI Engineer truncating an array of past chat messages to only include the last 10 interactions before sending the payload to the OpenAI API to avoid a Context Window overflow error.

---

## Keywords
Memory Limit, Token Limit, Input Size, Information Recall, KV Cache.

---

# Retrieval-Augmented Generation

# RAG

## Definition
Retrieval-Augmented Generation (RAG) is an architectural pattern that enhances a Large Language Model by retrieving relevant facts from an external knowledge base (usually a Vector Database) and injecting them into the prompt before generation.

---

## Why It Matters
RAG is the primary method for enabling LLMs to answer questions about proprietary, private, or highly up-to-date information without requiring expensive and difficult model Fine-Tuning, simultaneously minimizing hallucinations.

---

## Where It Is Used
RAG is used in enterprise knowledge bases, customer support chatbots referencing private documentation, and legal or medical research assistants requiring citations.

---

## Advantages
- Drastically reduces LLM hallucinations by grounding the generation in retrieved facts.
- Knowledge can be updated instantly by updating the database, without retraining the model.
- Provides traceability, allowing applications to cite the exact source document used to generate the answer.

---

## Limitations
- Retrieval performance is highly sensitive to the quality of Chunking and Embedding models.
- Cannot easily answer questions that require synthesizing information across thousands of distinct documents (unless using GraphRAG or massive Context Windows).
- Introduces additional latency and system complexity compared to a direct LLM call.

---

## Related Concepts
Vector Databases, Chunking, Semantic Search, Re-ranking, LLM.

---

## Common Interview Questions
- What is the difference between Naive RAG and Advanced RAG?
- How do you evaluate the retrieval accuracy of a RAG pipeline independently of the generation step?

---

## Common Misconceptions
A common misconception is that RAG trains the LLM on new data. RAG does not alter the model weights; it simply provides temporary contextual information inside the prompt.

---

## Practical Example
A user asks a chatbot about their company's new leave policy. The system searches a Vector Database, retrieves the PDF chunk containing the leave policy, and appends it to the LLM prompt to generate an accurate answer.

---

## Keywords
Information Retrieval, Knowledge Base, Context Injection, Semantic Search, Generation.


# Chunking

## Definition
Chunking is the process of breaking down large documents into smaller, manageable text segments (chunks) before converting them into Embeddings and storing them in a Vector Database for a RAG system.

---

## Why It Matters
Chunking directly impacts the semantic meaning captured by embeddings. If chunks are too small, context is lost. If chunks are too large, the embedding becomes diluted, reducing retrieval accuracy and consuming too much of the Context Window.

---

## Where It Is Used
Chunking is a required data ingestion step in all RAG pipelines when processing PDFs, documentation, websites, or databases.

---

## Advantages
- Ensures text segments fit within the embedding model's maximum token limit.
- Improves semantic retrieval accuracy by isolating specific concepts into distinct vectors.
- Conserves the LLM Context Window by only retrieving the most relevant segments.

---

## Limitations
- Splitting text arbitrarily can sever the connection between a pronoun and its noun, destroying context.
- Optimal chunk size is highly dependent on the specific dataset and query types, requiring trial and error.
- Managing tabular data (tables) or code blocks during chunking is extremely difficult.

---

## Related Concepts
RAG, Chunk Overlap, Embeddings, Vector Databases.

---

## Common Interview Questions
- Describe the trade-offs between character-level chunking and recursive semantic chunking.
- How does the chunk size affect the performance of a Cross-Encoder Re-ranker?

---

## Common Misconceptions
A frequent misconception is that larger chunks always provide better context. In reality, massive chunks dilute the embedding vector, making it harder for the Vector Database to find exact matches to specific user queries.

---

## Practical Example
An AI Engineer using LangChain's `RecursiveCharacterTextSplitter` to split a 50-page employee handbook into 500-token chunks with a 50-token overlap to ensure paragraphs are not split mid-sentence.

---

## Keywords
Text Splitting, Ingestion Pipeline, Preprocessing, Chunk Size, Document Processing.

---

# AI Agents

# AI Agent

## Definition
An AI Agent is an autonomous software system that uses a Large Language Model as its core reasoning engine, granting the model access to specific Tools and the autonomy to plan, execute, and evaluate actions to achieve a given goal.

---

## Why It Matters
AI Agents represent the transition from passive chatbots (which only answer questions) to active digital workers capable of interacting with external systems, APIs, and databases to perform real-world tasks automatically.

---

## Where It Is Used
AI Agents are used in automated customer support (taking actions like issuing refunds), autonomous coding assistants, and automated web research pipelines.

---

## Advantages
- Can solve complex, multi-step problems that a single LLM prompt cannot handle.
- Capable of interacting with legacy software systems through Tool Calling.
- Can self-correct by observing the output of a tool and adjusting its next action.

---

## Limitations
- Highly prone to infinite loops if a tool fails repeatedly and the agent cannot reason a way out.
- Non-deterministic execution makes testing and predicting the agent's exact path difficult.
- High latency and high API costs due to the numerous LLM calls required to complete a single goal.

---

## Related Concepts
Tool Calling, Multi-Agent Systems, Reasoning, Planning, LangGraph.

---

## Common Interview Questions
- Explain the architecture of a ReAct (Reasoning and Acting) agent.
- How do you prevent an autonomous AI Agent from executing destructive actions on a production database?

---

## Common Misconceptions
People often confuse a standard RAG pipeline with an AI Agent. A RAG pipeline executes a hardcoded sequence of steps. An AI Agent autonomously decides *which* steps to take based on its internal reasoning.

---

## Practical Example
An AI Agent instructed to "find the weather in Paris and email the result to the CEO." The agent reasons it must first call a Weather API tool, waits for the response, formats the text, and then calls an Email API tool.

---

## Keywords
Autonomous Systems, ReAct, Agentic AI, Reasoning Engine, Tool Execution.


# Tool Calling

## Definition
Tool Calling (often referred to as Function Calling) is a capability fine-tuned into modern Large Language Models allowing them to reliably output structured data (usually JSON) that matches a predefined schema, signaling an external application to execute a specific function.

---

## Why It Matters
Tool Calling is the critical bridge that allows text-based LLMs to interact with external software. It enables AI Agents to fetch real-time data, execute code, or mutate state in a database.

---

## Where It Is Used
Tool Calling is used in AI Agents interacting with REST APIs, executing Python code in a sandbox, querying SQL databases, and interacting with the Model Context Protocol (MCP).

---

## Advantages
- Eliminates the need to parse messy, unstructured text outputs to extract commands.
- Allows the LLM to request missing information dynamically before executing an action.
- Centralizes the execution logic in the secure backend environment, rather than inside the model.

---

## Limitations
- Models often hallucinate tool arguments that were not provided or invent tools that do not exist.
- Schema definitions must be incredibly explicit, consuming significant context window space.
- Adding too many tools confuses the model, severely degrading decision-making accuracy.

---

## Related Concepts
AI Agent, Structured Output, MCP, Prompt Engineering.

---

## Common Interview Questions
- How do you handle a scenario where an LLM calls a tool with missing required arguments?
- Explain the mechanism by which OpenAI's API enforces strict JSON schema adherence in Function Calling.

---

## Common Misconceptions
A major misconception is that the LLM actually executes the tool. The LLM only generates the JSON text *describing* the tool call; the backend Python or Node.js code is responsible for actually executing the function and returning the result to the LLM.

---

## Practical Example
An LLM returning a JSON payload like `{"name": "get_stock_price", "arguments": {"ticker": "AAPL"}}` when a user asks for the current price of Apple stock, prompting the backend to fetch the data.

---

## Keywords
Function Calling, JSON Schema, API Integration, Agent Actions, Execution.

---

# LangChain

# LCEL

## Definition
LangChain Expression Language (LCEL) is a declarative syntax used in LangChain for composing custom chains, utilizing a pipe operator (`|`) to seamlessly link prompts, models, and output parsers while automatically supporting streaming and asynchronous execution.

---

## Why It Matters
LCEL replaced LangChain's legacy, hardcoded chain classes by providing a highly composable, readable, and standard way to build complex LLM pipelines. It natively handles standardizing inputs and outputs across completely different model providers.

---

## Where It Is Used
LCEL is used universally in modern LangChain applications to build RAG pipelines, format API inputs, and construct the nodes for LangGraph architectures.

---

## Advantages
- Automatically provides asynchronous, batch, and streaming capabilities for free.
- Highly readable syntax, similar to Unix pipes, making debugging pipeline steps easier.
- Standardizes the `Runnable` interface, allowing any component to be swapped seamlessly.

---

## Limitations
- The syntax and underlying magic can be confusing for developers unfamiliar with Python operator overloading.
- Stack traces generated during LCEL errors can be deeply nested and difficult to interpret without tracing tools.
- Complex conditional logic within an LCEL chain can become unreadable, requiring migration to LangGraph.

---

## Related Concepts
LangChain, Runnables, Streaming, Prompts, Output Parsers.

---

## Common Interview Questions
- How does LCEL handle the passing of variables between a PromptTemplate and a ChatModel?
- Describe a situation where you would abandon LCEL in favor of building a custom LangGraph state machine.

---

## Common Misconceptions
Developers often think LCEL is a completely new programming language. It is strictly a Python-level abstraction leveraging the `__or__` dunder method to chain components together.

---

## Practical Example
Constructing a simple RAG chain using LCEL: `chain = prompt | llm | StrOutputParser()`, which can then be invoked with `chain.invoke({"topic": "AI"})`.

---

## Keywords
LangChain Expression Language, Pipe Syntax, Runnables, Composition, Chains.

---

# Vector Databases

# ChromaDB

## Definition
ChromaDB is an open-source, embedding-native Vector Database designed specifically to store and retrieve high-dimensional vectors and their associated metadata, optimized for building AI applications locally and scaling to the cloud.

---

## Why It Matters
ChromaDB significantly lowered the barrier to entry for AI Engineers building Retrieval-Augmented Generation (RAG) systems by providing a simple, SQLite-like local development experience that does not require provisioning cloud infrastructure during prototyping.

---

## Where It Is Used
ChromaDB is heavily used in local AI development, proof-of-concept RAG applications, hackathon projects, and scalable production environments when hosted as a client-server architecture.

---

## Advantages
- Exceptionally easy to set up locally (runs entirely in memory or backed by local files).
- Natively integrates with major embedding providers and LangChain.
- Supports robust metadata filtering before performing vector similarity search.

---

## Limitations
- Not traditionally designed for the massive, enterprise-scale billion-vector workloads where Pinecone or Milvus excel.
- Local instances cannot be easily shared across distributed microservices without migrating to the client-server mode.
- Lacks advanced hybrid search capabilities (combining vector search with BM25 keyword search) out-of-the-box compared to Weaviate.

---

## Related Concepts
Vector Databases, Similarity Search, Embeddings, RAG.

---

## Common Interview Questions
- When would you choose to use ChromaDB locally versus migrating your RAG pipeline to a managed service like Pinecone?
- Explain how to perform metadata filtering in ChromaDB and why it improves retrieval precision.

---

## Common Misconceptions
A common misconception is that ChromaDB only runs locally. While famous for its local developer experience, it fully supports distributed client-server deployments for production use cases.

---

## Practical Example
An AI Engineer initializing a persistent local ChromaDB client to store document embeddings for a personal knowledge base application, allowing semantic querying without incurring cloud database costs.

---

## Keywords
Vector Store, Embeddings Database, Local RAG, Similarity Search, Open Source.
