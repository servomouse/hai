An attempt to create a general AI using the hybrid approach. The neuronet part is a refactored version of [this repo](https://github.com/servomouse/neural_network)

## Motivation & Philosophy

The **Thinking Core** project is driven by the idea that intelligence does not require massive scale or preloaded knowledge. Instead, it emerges from simple, modular processes that can grow and reorganize themselves over time. The architecture is designed to be lightweight at its core, with complexity arising naturally from interaction between nodes, memory, and context.

Key philosophical principles:

- **Simplicity at the core**: The thinking core itself is minimal. It does not store knowledge or create nodes; it only juggles, merges, and organizes them.
- **Emergence through interaction**: Higher-level concepts (words, phrases, ideas) arise from local rules of merging and unmerging, not from pretraining.
- **Context as structure**: Short-term memory graphs provide immediate context, while long-term embedding builds a global graph that evolves into a world model.
- **Creativity as recombination**: Embedding processes generate new connections and unexpected merges, producing creativity and dream-like structures.
- **Curiosity as expansion**: The drive to extend the global graph is a natural motivation system. As the graph saturates with age, curiosity decreases.
- **Alternation of modes**: Wakefulness and sleep are not just biological necessities but architectural requirements. Wakefulness builds graphs; sleep embeds them, ensuring stability and insight.

This philosophy emphasizes **natural growth, adaptability, and dialogue**. The system learns not by brute force training, but by continuously reorganizing its own graph structures, asking for clarification when contradictions arise, and embedding experiences into a coherent world model. 

---

Thinking Core Architecture

This project explores a minimalist architecture for a Thinking Core — a system that evolves naturally without requiring traditional neural network training. The design emphasizes modularity, dynamic graph construction, and emergent creativity.

---

Overview

The system is composed of three main parts:

1. Input Processors  
   Responsible for creating nodes or pulling subgraphs from memory.  
   - Serial Processor: Handles sequential inputs (text, audio). Produces nodes for each symbol or syllable.  
   - Parallel Processor: Handles spatial inputs (vision). Segments input into parts and merges them into higher-level nodes.  
   - Associative Processor: Handles memory-trigger inputs (smell, episodic recall). Pulls entire subgraphs directly from global memory.

2. Thinking Core  
   A lightweight agent that juggles nodes. It does not create nodes itself.  
   - Receives nodes/subgraphs from input processors.  
   - Aligns, merges, or unmerges nodes based on context.  
   - Decides whether to embed nodes into the current context or switch contexts.  
   - Actively decides whether to produce output or not.

3. Memory Systems  
   - Short-Term Memory (STM): Holds the current working graph. Supports context switching via stack-like management.  
   - Long-Term Memory (LTM): Stores completed STM graphs in a queue. A separate embedding agent merges these into the global graph.  
   - Global Graph: The evolving world model. Embedding creates new connections, merges, and sometimes contradictions (dreams, creativity).

---

Node Structure

Each Node is both a data container and a micro-processor.

`python
class Node:
    def init(self, vector):
        # Main vector representing the node’s identity/state
        self.vector = vector
        
        # Placeholder for the node’s internal network
        self.network = None
        
        # Dictionary mapping input links → output links
        self.links = {}
    
    def computeforcore(self, neighbor_vectors):
        """
        Calculate output for the thinking core.
        Uses self.vector + neighbor_vectors.
        Currently empty — to be filled later.
        """
        pass
    
    def computeformerging(self, neighbor_vectors):
        """
        Calculate output for the merging agent.
        Uses self.vector + neighbor_vectors.
        Currently empty — to be filled later.
        """
        pass
`

---

Link Structure

Links connect nodes and encode directionality and context.

`python
class InputLink:
    def init(self, source_node):
        # Points to the previous node
        self.source = source_node


class OutputLink:
    def init(self, target_node, context=None):
        # Points to the next node
        self.target = target_node
        # Context stores role, ordering, or semantic info
        self.context = context
`

- Input Links: Simple pointers to previous nodes.  
- Output Links: Pointers to next nodes, enriched with context (e.g., subject/object, before/after).  
- Node Dictionary: Maps input links (keys) to output links (values). Supports multiple outputs per input.

---

Merge & Unmerge Logic

- Merge: Nodes fuse into higher-level units when co-occurrence or context suggests coherence.  
  - Example: [d, o, g, s] → "dogs".  
- Unmerge: Nodes split when later input contradicts the merge.  
  - Example: "dogs" + "m" + "ells" → corrected to "dog" + "smells".  
- Auxiliary Network: External agent checks memory for known merges/unmerges and guides corrections.

---

Contradiction Handling

When STM contradicts LTM/global graph:
1. Thinking core produces clarification output.  
2. After clarification, memory can be updated in different ways:  
   - Mark old link as obsolete.  
   - Mark old link as deception.  
   - Mark old link as error.  
   - Add new link alongside existing ones.  

This creates a layered memory that tracks not just facts but the history of belief changes.

---

Sleep/Wake Alternation

- Wakefulness: Thinking core active, juggling STM graphs, reasoning with global graph.  
- Sleep: Embedding agent active, merging STM graphs into LTM/global graph.  
- Alternation prevents interference between reasoning and embedding, and naturally produces dream-like recombinations.

---

Key Properties

- Modularity: Input processors handle node creation; core only organizes.  
- Contextuality: Input/output links encode order and role.  
- Self-Correction: Merge/unmerge logic allows reinterpretation mid-stream.  
- Creativity: Embedding generates new connections and ideas.  
- Curiosity: Drive to expand the global graph; naturally decreases as graph saturates.  

---

Next Steps

- Define local rules for merge/unmerge decisions.  
- Implement prioritization logic for multiple output links.  
- Fill in computeforcore and computeformerging methods with actual vector/network operations.  
`

---

