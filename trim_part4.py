"""
Refinement pass — Part 4 only.
Fixes: workflow accuracy, Planner contract, Router pseudocode,
       resume_review routing, Part 5 transition.
"""
import json

NB = "notebook/05_LangGraph.ipynb"

PART4_IDS = {
    "part4-header-01", "part4-sec1-md", "part4-sec2-md",
    "part4-sec3-md",   "part4-sec4-md", "part4-sec5-md",
    "part4-sec6-md",   "part4-sec7-md", "part4-sec8-md",
}

CELLS = [

    # ── Header ────────────────────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-header-01",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "# Part 4 — Workflow Design, Edges & Routing\n",
            "\n",
            "Parts 2–3 established **State** (shared memory) and **Nodes** (processing units).  \n",
            "Part 4 defines the **execution contract**: which nodes always run, which are intent-driven, and how routing decisions are made — without implementing any LangGraph API yet.\n",
            "\n",
            "| Concern | Owner |\n",
            "|---|---|\n",
            "| WHAT the system does | Node function |\n",
            "| HOW execution flows | Edges |\n",
            "| WHICH node runs next | Router |\n"
        ]
    },

    # ── 1. Workflow Philosophy ─────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec1-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 1. Workflow Philosophy\n",
            "\n",
            "**Separate execution flow from business logic.**  \n",
            "Node functions are unaware of what runs before or after them — they only read from and write to `CareerState`.  \n",
            "The edge structure owns sequencing and branching entirely.\n",
            "\n",
            "This makes routing independently testable (zero LLM calls) and nodes independently replaceable.  \n",
            "`CareerState` is the only interface between the two layers.\n"
        ]
    },

    # ── 2. Sequential Edges ────────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec2-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 2. Sequential Edges — Mandatory Foundation\n",
            "\n",
            "Sequential edges enforce **hard data dependencies**.  \n",
            "Three nodes always execute in order before any conditional branching occurs:\n",
            "\n",
            "```\n",
            "[User Input]\n",
            "      │\n",
            "      ▼\n",
            "resume_parsing_node      in: uploaded_cv (raw)           out: uploaded_cv (clean)\n",
            "      │\n",
            "      ▼\n",
            "skill_extraction_node    in: uploaded_cv (clean)         out: extracted_skills\n",
            "      │\n",
            "      ▼\n",
            "planner_node             in: user_message                 out: planner_output\n",
            "                             extracted_skills                   active_node\n",
            "      │\n",
            "   [career_router]\n",
            "```\n",
            "\n",
            "The Planner must receive `extracted_skills` to make personalized routing decisions — sequential ordering is not optional.\n"
        ]
    },

    # ── 3. Conditional Edges ───────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec3-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 3. Conditional Edges — Intent-Driven Branching\n",
            "\n",
            "After the Planner runs, the Router selects **one** execution path based on `planner_output`.  \n",
            "Each intent activates a dedicated sub-workflow; all paths converge at `final_response_node`.\n",
            "\n",
            "| Intent | Sub-workflow activated |\n",
            "|---|---|\n",
            "| `job_search` | `advanced_rag_retrieval_node` → `job_recommendation_node` |\n",
            "| `roadmap` | `learning_roadmap_node` |\n",
            "| `interview` | `advanced_rag_retrieval_node` → interview chain |\n",
            "| `resume_review` | *(future extension — dedicated review node)* |\n",
            "\n",
            "> `advanced_rag_retrieval_node` is **not** a standalone branch. It runs internally within the `job_search` and `interview` sub-workflows, fetching context before the specialist node executes.\n"
        ]
    },

    # ── 4. Planner Node ────────────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec4-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 4. Planner Node — Intent Classifier\n",
            "\n",
            "The Planner is a **classification node**, not a generation node.  \n",
            "It reads `CareerState`, classifies the user's intent using the LLM, then updates state and returns.  \n",
            "It does not answer the user, perform retrieval, or execute any business logic.\n",
            "\n",
            "**Does:**\n",
            "- Reads `user_message`, `extracted_skills`, `uploaded_cv`, `career_goal` from `CareerState`\n",
            "- Classifies intent via a constrained LLM call (structured output — reuses output parsers from earlier notebooks)\n",
            "- Writes `planner_output` and `active_node` back into `CareerState`\n",
            "\n",
            "**Does not:**\n",
            "- Generate responses\n",
            "- Query the retriever\n",
            "- Modify any field other than `planner_output` and `active_node`\n",
            "\n",
            "```\n",
            "Planner\n",
            "  │\n",
            "  ├─ Read CareerState  (user_message + extracted_skills)\n",
            "  │\n",
            "  ├─ Classify intent   (LLM structured output)\n",
            "  │       │\n",
            "  │       ├─ \"Find me ML roles\"       →  intent = job_search\n",
            "  │       ├─ \"Roadmap to Staff Eng\"   →  intent = roadmap\n",
            "  │       └─ \"Google design prep\"     →  intent = interview\n",
            "  │\n",
            "  └─ Write planner_output + active_node  →  return updated CareerState\n",
            "```\n"
        ]
    },

    # ── 5. Router Function ─────────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec5-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 5. Router Function\n",
            "\n",
            "The Router is a **pure Python function** — no LLM, no I/O, no state mutation.  \n",
            "It reads `planner_output` from `CareerState` and returns a node name string.  \n",
            "LangGraph calls it automatically on the conditional edge after `planner_node`.\n",
            "\n",
            "```python\n",
            "# PSEUDOCODE — full implementation in Part 5\n",
            "def career_router(state: CareerState) -> str:\n",
            "    decision = state.get(\"planner_output\", \"\")\n",
            "\n",
            "    ROUTE_MAP = {\n",
            "        \"job_search\": \"advanced_rag_retrieval_node\",   # RAG feeds job recommendation\n",
            "        \"roadmap\":    \"learning_roadmap_node\",\n",
            "        \"interview\":  \"advanced_rag_retrieval_node\",   # RAG feeds interview chain\n",
            "        # \"resume_review\": reserved for future extension\n",
            "    }\n",
            "\n",
            "    for key, node in ROUTE_MAP.items():\n",
            "        if key in decision:\n",
            "            return node\n",
            "\n",
            "    return \"final_response_node\"  # safe fallback\n",
            "```\n",
            "\n",
            "> `resume_review` is not routed to `resume_parsing_node` — that node already ran in the sequential phase. Resume Review requires a dedicated node and is marked as a future extension.\n"
        ]
    },

    # ── 6. Sub-Workflow Detail ─────────────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec6-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 6. Sub-Workflow Design\n",
            "\n",
            "Each intent branch is a **sub-workflow** — a local sequence of nodes that executes before converging on `final_response_node`.\n",
            "\n",
            "```\n",
            "── JOB SEARCH ──────────────────────────────────────────────────────────────\n",
            "  advanced_rag_retrieval_node          fetches relevant job context (Chroma)\n",
            "          │\n",
            "          ▼\n",
            "  job_recommendation_node              ranks and filters jobs against skills\n",
            "          │\n",
            "          ▼  → final_response_node\n",
            "\n",
            "── ROADMAP ─────────────────────────────────────────────────────────────────\n",
            "  learning_roadmap_node                generates step-by-step skill plan\n",
            "          │\n",
            "          ▼  → final_response_node\n",
            "\n",
            "── INTERVIEW ────────────────────────────────────────────────────────────────\n",
            "  advanced_rag_retrieval_node          fetches interview guides (Chroma)\n",
            "          │\n",
            "          ▼\n",
            "  career_goal_analysis_node            aligns context to target role\n",
            "          │\n",
            "          ▼  → final_response_node\n",
            "```\n",
            "\n",
            "`advanced_rag_retrieval_node` is shared across `job_search` and `interview` sub-workflows — it is not a top-level branch.\n"
        ]
    },

    # ── 7. Full Workflow Architecture ──────────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec7-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 7. Full Architecture\n",
            "\n",
            "```\n",
            "[User Input]\n",
            "      │\n",
            "      ▼  sequential\n",
            "resume_parsing_node\n",
            "      │\n",
            "      ▼  sequential\n",
            "skill_extraction_node\n",
            "      │\n",
            "      ▼  sequential\n",
            "planner_node  →  planner_output  |  active_node\n",
            "      │\n",
            "      ▼  conditional  [career_router reads planner_output]\n",
            "      │\n",
            "   ┌──┴───────────────────┬────────────────────────┐\n",
            "   ▼                      ▼                         ▼\n",
            "job_search            roadmap                  interview\n",
            "sub-workflow          sub-workflow             sub-workflow\n",
            "  rag_retrieval_node    learning_roadmap_node    rag_retrieval_node\n",
            "  job_recomm_node                                career_goal_node\n",
            "   │                      │                         │\n",
            "   └──────────────────────┴─────────────────────────┘\n",
            "                           │\n",
            "                           ▼  sequential\n",
            "                   final_response_node\n",
            "                   synthesizes state  →  final_response + AIMessage\n",
            "                           │\n",
            "                        [User]\n",
            "```\n",
            "\n",
            "The sequential foundation runs unconditionally. The conditional fan-out is bounded by `planner_output`. All sub-workflows converge at `final_response_node`.\n"
        ]
    },

    # ── 8. Production Notes + Transition ──────────────────────────────────────
    {
        "cell_type": "markdown",
        "id": "part4-sec8-md",
        "metadata": {},
        "source": [
            "---\n",
            "\n",
            "## 8. Architecture Principles & Edge Selection\n",
            "\n",
            "| Rule | Edge type | Rationale |\n",
            "|---|---|---|\n",
            "| Node always runs regardless of intent | Sequential | Correctness — data dependency |\n",
            "| All branches must converge | Sequential | `final_response_node` is universal |\n",
            "| Intent determines path | Conditional | Efficiency — execute only what's needed |\n",
            "| New intent added | + 1 Router entry | No existing node or edge modified |\n",
            "\n",
            "**Three-layer independence:**\n",
            "\n",
            "| Layer | Owns | Changes independently |\n",
            "|---|---|---|\n",
            "| State | `CareerState` schema | When new data fields are needed |\n",
            "| Logic | Node functions | When business logic changes |\n",
            "| Flow | Edges + Router | When routing rules change |\n",
            "\n",
            "---\n",
            "\n",
            "With the workflow architecture finalized, the next step is to translate this design into a LangGraph `StateGraph` — registering nodes, declaring sequential and conditional edges, and compiling the graph into an executable object. That is the responsibility of **Part 5**.\n"
        ]
    },
]


def refine_part4():
    with open(NB, "r", encoding="utf-8") as f:
        nb = json.load(f)

    new_cells = []
    injected = False

    for cell in nb["cells"]:
        if cell.get("id", "") in PART4_IDS:
            if not injected:
                new_cells.extend(CELLS)
                injected = True
        else:
            new_cells.append(cell)

    nb["cells"] = new_cells

    with open(NB, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    total = sum(len("".join(c["source"])) for c in CELLS)
    print(f"✅ Part 4 refined — {len(CELLS)} cells | {total} total chars")
    print()
    for c in CELLS:
        src = "".join(c["source"])
        heading = next((l.strip() for l in src.splitlines() if l.startswith("#")), "—")
        print(f"  {heading:55s}  {len(src):>4} chars")


if __name__ == "__main__":
    refine_part4()
