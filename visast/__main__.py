from sys import argv
from visast import generate, visualise

for arg in argv[1:]:
    ast = generate.fromPath(arg)
    visualise.graph(ast)
