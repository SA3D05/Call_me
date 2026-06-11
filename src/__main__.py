from .model import Model
from .parsing import GlobalInfo
from pprint import pprint
import sys
import numpy

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


info = GlobalInfo()
# give argument (program name not include)
info.get_paths(sys.argv[1:])
info.get_json()
# pprint()
model = Model(
    [prompt["prompt"] for prompt in info.input_json],
    info.functions_definition_json,
)
print(model.model.decode(numpy.argmax(model.generate())))
