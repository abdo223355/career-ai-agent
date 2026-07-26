import json

notebook_path = 'notebook/05_LangGraph.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}

def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }

# Find the index of the cell containing "### 1. Resume Parsing Node"
target_index = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown' and '### 1. Resume Parsing Node' in "".join(cell['source']):
        target_index = i
        break

if target_index == -1:
    print("Could not find the target cell to insert before.")
    exit(1)

new_cells = []

new_cells.append(md("""\
# Shared AI Components

To ensure our LangGraph architecture is efficient and production-ready, we must instantiate expensive objects (like the LLM, Embeddings, and the Advanced Retriever) exactly once. Instead of recreating them inside every node, we initialize them here globally using our existing project modules. Every node in our graph will reuse these shared resources, keeping the workflow modular and fast.
"""))

new_cells.append(code("""\
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.models.llm import get_llm
from src.models.embeddings import get_embeddings
from src.rag.retriever import get_advanced_retriever

print("Initializing shared AI components...")

# 1. Primary LLM
llm = get_llm()

# 2. Embedding Model
embeddings = get_embeddings()

# 3. Advanced Retriever Pipeline (Chroma + BM25 + CrossEncoder)
advanced_retriever = get_advanced_retriever(embeddings=embeddings)

print("✅ Shared resources successfully initialized and ready for LangGraph Nodes!")
"""))

# Insert the new cells before the target index
nb['cells'] = nb['cells'][:target_index] + new_cells + nb['cells'][target_index:]

# Wait, previously we had a cell under "### Loading Previous Results (VectorDB & Retrievers)" doing this exact thing.
# The prompt says: "Do NOT rewrite previous sections." So I should just leave the previous sections alone 
# and simply insert this block right before the nodes.
# However, this new instruction functionally replaces the concept we added previously, but to be strictly obedient:
# "Update Part 3 only. Do NOT rewrite previous sections."

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Shared AI Components section successfully inserted.")
