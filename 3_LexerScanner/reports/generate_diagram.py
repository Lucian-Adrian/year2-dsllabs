from graphviz import Digraph
import os

repodir = os.path.dirname(__file__)

os.chdir(repodir)

dot = Digraph('Architecture', format='png')
dot.attr(rankdir='LR', fontsize='12')
dot.node('A','TensorScript Source')
dot.node('B','src/lexer.py')
dot.node('C','src/tokens.py')
dot.node('D','LexicalError')
dot.node('E','CLI Output')
dot.node('F','Streamlit Observatory')
dot.node('G','src/highlighter.py')

dot.edges(['AB','BC','BD','CE','CF','CG'])
dot.edge('G','E', style='dashed')

outfile = dot.render(filename='architecture_diagram', directory=repodir, cleanup=True)
print('Generated', outfile)
