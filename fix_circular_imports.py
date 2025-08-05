import os

BASE_DIR = os.path.join(os.path.dirname(__file__), 'ai-backend-python', 'app', 'services')

TRUSTED_SOURCES_CODE = '''TRUSTED_SOURCES = [
    "https://stackoverflow.com",
    "https://ai.stackexchange.com",
    "https://datascience.stackexchange.com",
    "https://www.reddit.com/r/MachineLearning",
    "https://www.reddit.com/r/artificial",
    "https://github.com",
    "https://huggingface.co/models",
    "https://paperswithcode.com",
    "https://arxiv.org",
    "https://www.semanticscholar.org",
    "https://medium.com",
    "https://dev.to",
    "https://ai.googleblog.com",
    "https://openai.com/blog",
    "https://docs.python.org",
    "https://pytorch.org",
    "https://www.tensorflow.org",
    "https://scikit-learn.org",
    "https://fastapi.tiangolo.com"
]

def is_trusted_source(url: str) -> bool:
    for source in TRUSTED_SOURCES:
        if url.startswith(source):
            return True
    return False
'''

# 1. Write trusted_sources.py
trusted_sources_path = os.path.join(BASE_DIR, 'trusted_sources.py')
with open(trusted_sources_path, 'w') as f:
    f.write(TRUSTED_SOURCES_CODE)

# 2. Update internet_fetchers.py
fetchers_path = os.path.join(BASE_DIR, 'internet_fetchers.py')
with open(fetchers_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'from .imperium_learning_controller import ImperiumLearningController' in line:
        new_lines.append('from .trusted_sources import is_trusted_source\n')
    else:
        new_lines.append(line.replace('ImperiumLearningController.is_trusted_source', 'is_trusted_source'))

with open(fetchers_path, 'w') as f:
    f.writelines(new_lines)

# 3. Update imperium_learning_controller.py
controller_path = os.path.join(BASE_DIR, 'imperium_learning_controller.py')
with open(controller_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'TRUSTED_SOURCES' in line or 'def get_trusted_sources' in line or 'def is_trusted_source' in line:
        continue  # Remove old trusted source logic
    elif 'class ImperiumLearningController' in line:
        new_lines.append('from .trusted_sources import TRUSTED_SOURCES, is_trusted_source\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(controller_path, 'w') as f:
    f.writelines(new_lines)

print('Circular import fix applied. Please restart your backend.') 