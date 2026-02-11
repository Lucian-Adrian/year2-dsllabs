from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import networkx as nx

if TYPE_CHECKING:
    from .automaton import Automaton


def plot_automaton(
    automaton: "Automaton", title: str = "Finite Automaton", save_path: str = None
) -> None:
    """Plot the automaton as a directed graph. Optionally save to file."""
    G = nx.DiGraph()

    # Add nodes
    for state in automaton.states:
        if state in automaton.accepting_states:
            G.add_node(state, color="green")
        elif state == automaton.start_state:
            G.add_node(state, color="blue")
        else:
            G.add_node(state, color="lightblue")

    # Add edges
    for (from_state, token), to_state in automaton.transitions.items():
        G.add_edge(from_state, to_state, label=token)

    # Draw the graph
    pos = nx.spring_layout(G)
    node_colors = [G.nodes[node]["color"] for node in G.nodes]

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=2000,
        font_size=16,
        font_weight="bold",
    )

    # Draw edge labels
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=12)

    plt.title(title)

    if save_path:
        plt.savefig(save_path)
        print(f"Graph saved to {save_path}")
    else:
        plt.show()
